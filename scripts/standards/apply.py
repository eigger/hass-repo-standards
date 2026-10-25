"""Apply reviewed plans with an external recovery journal and guarded file writes."""

from __future__ import annotations

import base64
import binascii
import copy
import os
import secrets
import tempfile
from contextlib import contextmanager
from pathlib import Path

from . import contract, inventory, planning

JOURNAL_VERSION = 1


def external_path(value, target, *, must_exist=False):
    path = Path(value).absolute()
    target = Path(target).resolve()
    for candidate in (path, *path.parents):
        if candidate.is_symlink() or getattr(candidate, "is_junction", lambda: False)():
            raise ValueError("Plan/journal paths cannot traverse a symlink or junction")
    resolved = path.resolve()
    if resolved == target or resolved.is_relative_to(target):
        raise ValueError("Plan and journal must be outside the target repository")
    if not resolved.parent.is_dir() or (resolved.exists() and not resolved.is_file()):
        raise ValueError("Plan/journal requires an existing parent and a regular file")
    if must_exist and not resolved.is_file():
        raise ValueError("Required plan/journal file does not exist")
    return resolved


def target_root(value):
    path = Path(value).absolute()
    for candidate in (path, *path.parents):
        if candidate.is_symlink() or getattr(candidate, "is_junction", lambda: False)():
            raise ValueError("Target root cannot traverse a symlink or junction")
    root = path.resolve()
    if root == root.parent or not root.parent.is_dir() or (root.exists() and not root.is_dir()):
        raise ValueError(
            "Target requires an existing parent directory and cannot be a filesystem root"
        )
    return root


def atomic_json(path, document):
    external_path(path, document["target"])
    descriptor, name = tempfile.mkstemp(prefix=".hass-journal-", suffix=".json", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(planning.canonical_json(document).encode("utf-8"))
            stream.flush()
            os.fsync(stream.fileno())
        external_path(path, document["target"])
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def publish_exclusive(path, document, target):
    """Publish a fully flushed initial journal atomically without replacing evidence."""
    external_path(path, target)
    descriptor, temporary = tempfile.mkstemp(
        prefix=".hass-journal-", suffix=".json", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(planning.canonical_json(document).encode("utf-8"))
            stream.flush()
            os.fsync(stream.fileno())
        external_path(path, target)
        # Same-directory hard linking atomically fails when the journal name
        # already exists; replacing an existing journal would discard backups.
        os.link(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def reserve_journal(path, document):
    publish_exclusive(path, document, document["target"])


def anchor_path(journal_path, root, *, must_exist=False):
    return external_path(
        journal_path.with_name(journal_path.name + ".plan.json"), root, must_exist=must_exist
    )


def validate_anchor(path, root, document):
    source = anchor_path(path, root, must_exist=True)
    anchor = inventory.load_json(source)
    contract.validate_document(anchor, "plan")
    if planning.canonical_json(anchor) != planning.canonical_json(document["plan"]):
        raise ValueError("Recovery plan differs from the preserved original plan anchor")
    if planning.digest(planning.canonical_json(anchor).encode("utf-8")) != document["plan_sha256"]:
        raise ValueError("Recovery original plan anchor digest is invalid")


@contextmanager
def target_lock(root):
    name = (
        ".hass-standards-"
        + planning.digest(os.path.normcase(str(root)).encode("utf-8"))[:24]
        + ".lock"
    )
    path = root.parent / name
    token = secrets.token_hex(24).encode("ascii")
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as error:
        raise ValueError(f"Another transaction or stale lock exists: {path}") from error
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(token)
        yield
    finally:
        if not path.is_symlink() and path.is_file() and path.read_bytes() == token:
            path.unlink()


def current_hash(root, relative):
    target_root(root)
    path = inventory.safe_target_path(root, relative)
    if path.is_file():
        return planning.digest(path.read_bytes())
    if path.exists():
        raise ValueError(f"Expected regular file: {relative}")
    return None


def validate_guards(root, plan, applied=(), created_directories=()):
    target_root(root)
    operations = {operation["path"]: operation for operation in plan["operations"]}
    names = set()
    for guard in plan["guards"]:
        name = guard["path"]
        alias = name.casefold()
        if alias in names:
            raise ValueError("Duplicate or aliased guard path")
        names.add(alias)
        path = inventory.safe_target_path(root, name)
        if name in created_directories:
            expected_kind, expected_hash = "directory", None
        elif name in applied:
            expected_kind, expected_hash = "file", operations[name]["after_sha256"]
        else:
            expected_kind, expected_hash = guard["kind"], guard["sha256"]
        if expected_kind == "directory":
            if not path.is_dir() or expected_hash is not None:
                raise ValueError(f"Stale directory guard: {name}")
        elif expected_kind == "absent":
            if path.exists() or expected_hash is not None:
                raise ValueError(f"Stale absence guard: {name}")
        elif not path.is_file() or current_hash(root, name) != expected_hash:
            raise ValueError(f"Stale content guard: {name}")


def validate_plan(root, document, *, central=None):
    contract.validate_document(document, "plan")
    contract.validate_input(document["validated_input"])
    if document["input_digest"] != planning.digest(
        planning.canonical_json(document["validated_input"]).encode("utf-8")
    ):
        raise ValueError("Plan input digest does not match its validated input snapshot")
    if document["target_identity"]["path"] != str(root):
        raise ValueError("Plan target identity does not match the requested target")
    if document["target_identity"]["root_exists"] != root.exists():
        raise ValueError("Plan target root existence changed")
    standards_reference = planning.plan_reference(document)
    planning.verify_standards(standards_reference, central)
    if document["conflicts"]:
        raise ValueError("A plan with unresolved conflicts cannot be applied")
    validate_guards(root, document)
    regenerated = planning.plan(
        root,
        document["mode"],
        copy.deepcopy(document["validated_input"]),
        standards_reference,
        central=central,
        release_attestation=document.get("release_attestation"),
        internal_replan=True,
    )
    if planning.canonical_json(regenerated) != planning.canonical_json(document):
        raise ValueError("Plan differs from the current contract replan; inspect and plan again")
    return regenerated


def ensure_directories(root, parent, journal, journal_path):
    target_root(root)
    if not root.exists():
        root.mkdir()
        journal["root_created"] = True
        atomic_json(journal_path, journal)
    relative = parent.relative_to(root)
    current = root
    for part in relative.parts:
        current = current / part
        name = current.relative_to(root).as_posix()
        inventory.safe_target_path(root, name)
        if not current.exists():
            current.mkdir()
            journal["created_directories"].append(name)
            atomic_json(journal_path, journal)
        elif not current.is_dir():
            raise ValueError(f"Expected parent directory: {name}")


def replace_file(root, operation, journal, journal_path):
    name = operation["path"]
    path = inventory.safe_target_path(root, name)
    ensure_directories(root, path.parent, journal, journal_path)
    descriptor, temporary = tempfile.mkstemp(prefix=".hass-write-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(operation["content"].encode("utf-8"))
            stream.flush()
            os.fsync(stream.fileno())
        inventory.safe_target_path(root, name)
        if current_hash(root, name) != operation["before_sha256"]:
            raise ValueError(f"Target changed immediately before replacement: {name}")
        if path.exists():
            os.chmod(temporary, path.stat().st_mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def outcome(root, journal_path, journal, error=None):
    applied = []
    for entry in journal["entries"]:
        try:
            if current_hash(root, entry["path"]) == entry["after_sha256"]:
                applied.append(entry["path"])
        except (ValueError, OSError):
            pass  # Report the journal even if a subsequent user edit changed path type.
    result = {
        "status": journal["status"],
        "journal": str(journal_path),
        "applied": applied,
        "pending": journal["plan"]["pending"],
        "error": str(error) if error else None,
        "recovery_command": [
            "python",
            "scripts/manage_integration.py",
            "recover",
            str(root),
            "--journal",
            str(journal_path),
        ],
    }
    return result


def apply_plan(target, plan_path, *, journal_path=None, central=None):
    root = target_root(target)
    source = external_path(plan_path, root, must_exist=True)
    destination = external_path(journal_path or source.with_name(source.stem + ".apply.json"), root)
    anchor = anchor_path(destination, root)
    if anchor.exists() or anchor == source:
        raise ValueError(
            "Original plan anchor must be a new external file; existing evidence is preserved"
        )
    if destination == source or destination.exists():
        raise ValueError("Journal must be a new file distinct from the original plan")
    document = inventory.load_json(source)
    validate_plan(root, document, central=central)
    with target_lock(root):
        validate_plan(root, document, central=central)
        external_path(destination, root)
        entries = []
        for operation in document["operations"]:
            path = inventory.safe_target_path(root, operation["path"])
            before = path.read_bytes() if path.is_file() else None
            if (planning.digest(before) if before is not None else None) != operation[
                "before_sha256"
            ]:
                raise ValueError(f"Target changed while preparing backup: {operation['path']}")
            entries.append(
                {
                    "path": operation["path"],
                    "before_sha256": operation["before_sha256"],
                    "after_sha256": operation["after_sha256"],
                    "before_base64": base64.b64encode(before).decode("ascii")
                    if before is not None
                    else None,
                    "state": "pending",
                }
            )
        journal = {
            "schema_version": JOURNAL_VERSION,
            "target": str(root),
            "plan": document,
            "plan_sha256": planning.digest(planning.canonical_json(document).encode("utf-8")),
            "status": "prepared",
            "root_created": False,
            "created_directories": [],
            "entries": entries,
            "error": None,
        }
        publish_exclusive(anchor, document, root)
        try:
            reserve_journal(destination, journal)
        except BaseException:
            # No target write has started. Remove only our unchanged unpublished
            # transaction's anchor; orphan anchors after a process crash remain evidence.
            if (
                anchor.is_file()
                and not anchor.is_symlink()
                and anchor.read_bytes() == planning.canonical_json(document).encode("utf-8")
            ):
                anchor.unlink()
            raise
        applied = set()
        try:
            journal["status"] = "applying"
            atomic_json(destination, journal)
            for operation, entry in zip(document["operations"], journal["entries"]):
                validate_guards(root, document, applied, journal["created_directories"])
                entry["state"] = "writing"
                atomic_json(destination, journal)
                replace_file(root, operation, journal, destination)
                applied.add(entry["path"])
                entry["state"] = "applied"
                atomic_json(destination, journal)
            validate_guards(root, document, applied, journal["created_directories"])
            journal["status"] = "completed"
            atomic_json(destination, journal)
            return outcome(root, destination, journal)
        except (ValueError, OSError) as error:
            journal["status"], journal["error"] = "failed", str(error)
            try:
                atomic_json(destination, journal)
            except OSError:
                # The last durable 'writing' state and backup remain recoverable.
                pass
            return outcome(root, destination, journal, error)


def validate_journal(root, document, *, central=None):
    fields = {
        "schema_version",
        "target",
        "plan",
        "plan_sha256",
        "status",
        "root_created",
        "created_directories",
        "entries",
        "error",
    }
    if (
        not isinstance(document, dict)
        or set(document) != fields
        or type(document["schema_version"]) is not int
        or document["schema_version"] != JOURNAL_VERSION
    ):
        raise ValueError("Unsupported recovery journal")
    if document["target"] != str(root) or not isinstance(document["root_created"], bool):
        raise ValueError("Recovery target identity does not match")
    if document["status"] not in {
        "prepared",
        "applying",
        "completed",
        "failed",
        "recovering",
        "recovered",
    }:
        raise ValueError("Invalid recovery status")
    plan = document["plan"]
    contract.validate_document(plan, "plan")
    contract.validate_input(plan["validated_input"])
    if plan["target_identity"]["root_exists"] and document["root_created"]:
        raise ValueError("Recovery cannot delete a target root that originally existed")
    if plan["target_identity"]["path"] != str(root) or plan["conflicts"]:
        raise ValueError("Invalid recovery plan target or conflicts")
    if planning.digest(planning.canonical_json(plan).encode("utf-8")) != document["plan_sha256"]:
        raise ValueError("Recovery plan digest is invalid")
    if (
        planning.digest(planning.canonical_json(plan["validated_input"]).encode("utf-8"))
        != plan["input_digest"]
    ):
        raise ValueError("Recovery input digest is invalid")
    central = planning.verify_standards(planning.plan_reference(plan), central)
    records = contract.load_contract(central / "templates/integration/contract.json")["records"]
    allowed = {}
    for record in records:
        platforms = (
            plan["validated_input"]["platforms"]["value"]
            if record["condition"] == "platforms"
            else [None]
        )
        for platform in platforms:
            name = contract.destination_path(
                record, plan["validated_input"]["domain"]["value"], platform
            )
            if not name.endswith("/"):
                allowed[name] = record
    entries = document["entries"]
    if not isinstance(entries, list) or len(entries) != len(plan["operations"]):
        raise ValueError("Recovery entries must match the original operation list")
    seen, ancestors = set(), set()
    for operation, entry in zip(plan["operations"], entries):
        name = operation["path"]
        inventory.safe_target_path(root, name)
        if name.casefold() in seen or name not in allowed:
            raise ValueError("Recovery contains a duplicate or noncontract path")
        seen.add(name.casefold())
        if (
            operation["ownership"] != allowed[name]["ownership"]
            or operation["source"] != allowed[name]["source"]
        ):
            raise ValueError("Recovery operation does not match contract ownership/source")
        if planning.digest(operation["content"].encode("utf-8")) != operation["after_sha256"]:
            raise ValueError("Recovery operation content digest is invalid")
        required = {"path", "before_sha256", "after_sha256", "before_base64", "state"}
        if (
            not isinstance(entry, dict)
            or set(entry) != required
            or any(
                entry[field] != operation[field]
                for field in ("path", "before_sha256", "after_sha256")
            )
        ):
            raise ValueError("Recovery entry and operation do not match")
        if entry["state"] not in {"pending", "writing", "applied", "restoring", "restored"}:
            raise ValueError("Invalid recovery entry status")
        backup = entry["before_base64"]
        if entry["before_sha256"] is None:
            if backup is not None:
                raise ValueError("New files cannot have an original backup")
        else:
            try:
                original = base64.b64decode(backup, validate=True)
            except (TypeError, ValueError, binascii.Error) as error:
                raise ValueError("Invalid backup encoding") from error
            if planning.digest(original) != entry["before_sha256"]:
                raise ValueError("Recovery backup hash does not match the original")
        ancestors.update(parent.as_posix() for parent in Path(name).parents if parent != Path("."))
    directories = document["created_directories"]
    if (
        not isinstance(directories, list)
        or any(not isinstance(name, str) or name not in ancestors for name in directories)
        or len(set(directories)) != len(directories)
    ):
        raise ValueError("Invalid transaction-created directory list")
    initial_guards = {guard["path"]: guard for guard in plan["guards"]}
    for name in directories:
        inventory.safe_target_path(root, name)
        if name not in initial_guards or initial_guards[name]["kind"] != "absent":
            raise ValueError("Recovery cannot remove a directory that originally existed")
    validate_preimage(root, document, central=central)
    return document


def validate_preimage(root, journal, *, central=None):
    """Reconstruct the original read-only snapshot and reproduce the reviewed plan.

    Self-consistent edits to backup hashes are insufficient: the recovered
    preimage must produce exactly the original contract operations and diff.
    Subsequent changes to preserved source files cannot be reconstructed and
    therefore block recovery before any target write.
    """
    plan = journal["plan"]
    entries = {entry["path"]: entry for entry in journal["entries"]}
    with tempfile.TemporaryDirectory(prefix="hass-recovery-preimage-") as directory:
        stage = Path(directory) / "target"
        if plan["target_identity"]["root_exists"]:
            stage.mkdir()
        for guard in plan["guards"]:
            name = guard["path"]
            path = inventory.safe_target_path(root, name)
            if guard["kind"] == "directory":
                (stage / name).mkdir(parents=True, exist_ok=True)
            elif guard["kind"] == "file":
                if name in entries:
                    data = base64.b64decode(entries[name]["before_base64"], validate=True)
                else:
                    if current_hash(root, name) != guard["sha256"]:
                        raise ValueError(
                            f"Preserved source changed; cannot reproduce recovery preimage: {name}"
                        )
                    data = path.read_bytes()
                output = stage / name
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(data)
        # New operations have absence guards. Existing operations must have a
        # matching file guard and backup before re-planning the snapshot.
        for entry in journal["entries"]:
            guard = next(
                (guard for guard in plan["guards"] if guard["path"] == entry["path"]), None
            )
            expected_kind = "absent" if entry["before_sha256"] is None else "file"
            if (
                guard is None
                or guard["kind"] != expected_kind
                or guard["sha256"] != entry["before_sha256"]
            ):
                raise ValueError("Backup and original plan guard do not match")
        if plan["mode"] == "adopt":
            stage.mkdir(exist_ok=True)

            def local_git(*args):
                if inventory.git(stage, *args) is None:
                    raise ValueError("Unable to reproduce private recovery Git metadata")

            local_git(
                "init", "--initial-branch=" + plan["validated_input"]["default_branch"]["value"]
            )
            local_git("config", "user.name", "Local standards recovery snapshot")
            local_git("config", "user.email", "recovery@example.invalid")
            local_git("config", "core.autocrlf", "false")
            hooks = Path(directory) / "empty-hooks"
            hooks.mkdir()
            local_git("config", "core.hooksPath", str(hooks))
            local_git("config", "commit.gpgSign", "false")
            local_git("add", "--force", ".")
            local_git("commit", "--allow-empty", "-m", "Private recovery validation snapshot")
            local_git("remote", "add", "origin", plan["validated_input"]["remote"]["value"])
        reproduced = planning.plan(
            stage,
            plan["mode"],
            copy.deepcopy(plan["validated_input"]),
            planning.plan_reference(plan),
            central=central,
            release_attestation=plan.get("release_attestation"),
            internal_replan=True,
        )
        reproduced["target_identity"]["path"] = str(root)
        if planning.canonical_json(reproduced) != planning.canonical_json(plan):
            raise ValueError(
                "Recovery backup preimage does not reproduce the original contract plan"
            )


def recovery_states(root, journal):
    states = []
    for entry in journal["entries"]:
        current = current_hash(root, entry["path"])
        if current == entry["before_sha256"]:
            states.append("original")
        elif current == entry["after_sha256"]:
            states.append("applied")
        else:
            raise ValueError(f"Preserve subsequent user changes; cannot recover: {entry['path']}")
    return states


def restore_file(root, entry):
    name = entry["path"]
    path = inventory.safe_target_path(root, name)
    if current_hash(root, name) != entry["after_sha256"]:
        raise ValueError(f"Recovery target changed immediately before restore: {name}")
    if entry["before_sha256"] is None:
        path.unlink()
        return
    content = base64.b64decode(entry["before_base64"], validate=True)
    descriptor, temporary = tempfile.mkstemp(prefix=".hass-restore-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        inventory.safe_target_path(root, name)
        if current_hash(root, name) != entry["after_sha256"]:
            raise ValueError(f"Recovery target changed immediately before replacement: {name}")
        os.chmod(temporary, path.stat().st_mode)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def recover(target, journal_path, *, central=None):
    root = target_root(target)
    path = external_path(journal_path, root, must_exist=True)
    journal = inventory.load_json(path)
    validate_anchor(path, root, journal)
    journal = validate_journal(root, journal, central=central)
    recovery_states(root, journal)
    with target_lock(root):
        journal = inventory.load_json(path)
        validate_anchor(path, root, journal)
        journal = validate_journal(root, journal, central=central)
        states = recovery_states(root, journal)
        journal["status"] = "recovering"
        atomic_json(path, journal)
        try:
            for entry, state in reversed(list(zip(journal["entries"], states))):
                if state == "applied":
                    entry["state"] = "restoring"
                    atomic_json(path, journal)
                    restore_file(root, entry)
                entry["state"] = "restored"
                atomic_json(path, journal)
            remaining_directories = []
            for name in sorted(
                journal["created_directories"], key=lambda value: (-value.count("/"), value)
            ):
                directory = inventory.safe_target_path(root, name)
                if directory.is_dir():
                    try:
                        directory.rmdir()
                    except OSError:
                        remaining_directories.append(name)
            if journal["root_created"] and root.is_dir():
                try:
                    root.rmdir()
                except OSError:
                    remaining_directories.append(".")
            journal["status"], journal["error"] = "recovered", None
            atomic_json(path, journal)
            return {
                "status": "recovered",
                "journal": str(path),
                "preserved_directories": remaining_directories,
            }
        except (ValueError, OSError) as error:
            journal["status"], journal["error"] = "failed", str(error)
            try:
                atomic_json(path, journal)
            except OSError:
                pass
            return {
                "status": "failed",
                "journal": str(path),
                "error": str(error),
                "recovery_command": [
                    "python",
                    "scripts/manage_integration.py",
                    "recover",
                    str(root),
                    "--journal",
                    str(path),
                ],
            }
