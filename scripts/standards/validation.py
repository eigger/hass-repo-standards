"""Read-only structural checks shared by the integration checker and contract assets.

Static success only establishes these file/metadata contracts. Actual HA loading,
behavior, translation meaning and external mock boundaries require execution and review.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

import yaml

from . import categories, conditions, contract, inventory, readme, scaffold

UNFINISHED = re.compile(
    r"\b(?:TODO|TBD|FIXME|REPLACE_[A-Z_]+|YOUR_[A-Z_]+)\b|\{\{[^}]+\}\}|@@[a-z_]+@@|example\.com|hass-example|작성 필요|미입력|미확인",
    re.I,
)
RESERVED = {"__init__", "const", "config_flow", "coordinator", "entity", "diagnostics"}


def foundation_errors(root, domain, safe_path, central=None):
    central = Path(central or contract.CENTRAL)
    errors = []
    for record in contract.load_contract()["records"]:
        if record["ownership"] != "exact_file":
            continue
        relative = contract.destination_path(record, domain)
        path = safe_path(root, relative)
        expected = (central / record["source"]).read_bytes()
        if not path.is_file() or path.read_bytes() != expected:
            rule = "TEST-03" if relative == "tests/conftest.py" else "TEST-08"
            message = (
                "must match the central template exactly" if expected else "must exist and be empty"
            )
            errors.append((rule, relative, message))
    relative = f"tests/components/{domain}/conftest.py"
    record = next(
        record
        for record in contract.load_contract()["records"]
        if record["id"] == "domain-conftest"
    )
    try:
        actual = safe_path(root, relative).read_text(encoding="utf-8")
        expected = (central / record["source"]).read_text(encoding="utf-8")
        for marker in record["markers"]:
            if readme.block(actual, marker) != readme.block(expected, marker):
                raise ValueError("managed domain fixture skeleton is required")
    except (OSError, ValueError) as error:
        errors.append(("TEST-08", relative, str(error)))
    return errors


def python_tree(root, relative, safe_path, rule, errors):
    try:
        return ast.parse(
            safe_path(root, relative).read_text(encoding="utf-8"), filename=str(root / relative)
        )
    except SyntaxError as error:
        # Keep the historical interpreter/parse guidance without duplicating it.
        from bluetooth_documents import syntax_error_message

        errors.append((rule, relative, syntax_error_message(error)))
    except (OSError, ValueError) as error:
        errors.append((rule, relative, str(error)))
    return None


def assigned(tree, name):
    if tree is None:
        return []
    result = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name for target in node.targets
        ):
            result.append(node.value)
        elif (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == name
        ):
            result.append(node.value)
    return result


def registered_actions(trees, domain):
    """Return literal names at recognizable HA registration boundaries only."""
    result = set()
    for tree in trees.values():
        platform_modules = set()
        getters = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if node.module == "homeassistant.helpers" and alias.name == "entity_platform":
                        platform_modules.add(alias.asname or alias.name)
                    if (
                        node.module == "homeassistant.helpers.entity_platform"
                        and alias.name == "async_get_current_platform"
                    ):
                        getters.add(alias.asname or alias.name)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "homeassistant.helpers.entity_platform":
                        platform_modules.add(alias.asname or alias.name)
        receivers = set()
        for node in ast.walk(tree):
            if isinstance(node, (ast.Assign, ast.AnnAssign)) and isinstance(node.value, ast.Call):
                function = dotted(node.value.func)
                if function in getters or function in {
                    name + ".async_get_current_platform" for name in platform_modules
                }:
                    targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                    receivers.update(
                        target.id for target in targets if isinstance(target, ast.Name)
                    )
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            function = dotted(node.func)
            argument = None
            if function == "hass.services.async_register":
                domain_arg = (
                    node.args[0]
                    if node.args
                    else next((kw.value for kw in node.keywords if kw.arg == "domain"), None)
                )
                if not (
                    (isinstance(domain_arg, ast.Name) and domain_arg.id == "DOMAIN")
                    or (isinstance(domain_arg, ast.Constant) and domain_arg.value == domain)
                ):
                    continue
                argument = (
                    node.args[1]
                    if len(node.args) > 1
                    else next((kw.value for kw in node.keywords if kw.arg == "service"), None)
                )
            elif function in {name + ".async_register_entity_service" for name in receivers}:
                argument = (
                    node.args[0]
                    if node.args
                    else next((kw.value for kw in node.keywords if kw.arg == "name"), None)
                )
            if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
                result.add(argument.value)
    return result


def selected_platforms(trees, errors, component):
    platforms = set()
    for relative, tree in trees.items():
        for expression in assigned(tree, "PLATFORMS"):
            if not isinstance(expression, (ast.List, ast.Tuple, ast.Set)):
                errors.append(
                    (
                        "HA-13",
                        relative,
                        "Cannot statically verify PLATFORMS; use an explicit platform sequence or record an approved exception",
                    )
                )
                continue
            for item in expression.elts:
                name = (
                    item.value
                    if isinstance(item, ast.Constant) and isinstance(item.value, str)
                    else item.attr.lower()
                    if isinstance(item, ast.Attribute)
                    and isinstance(item.value, ast.Name)
                    and item.value.id == "Platform"
                    else None
                )
                if name is None or not re.fullmatch(r"[a-z][a-z0-9_]*", name):
                    errors.append(
                        ("HA-13", relative, "Unresolved platform identifier requires review")
                    )
                else:
                    platforms.add(name)
        module = Path(relative).stem
        if module in RESERVED:
            continue
        for node in ast.walk(tree):
            setup = any(
                isinstance(function, (ast.FunctionDef, ast.AsyncFunctionDef))
                and function.name in {"async_setup_entry", "async_setup_platform", "setup_platform"}
                for function in tree.body
            )
            if (
                setup
                and isinstance(node, ast.ImportFrom)
                and node.level == 0
                and (
                    (node.module or "") == f"homeassistant.components.{module}"
                    or (node.module or "").startswith(f"homeassistant.components.{module}.")
                )
            ):
                platforms.add(module)
    return sorted(platforms)


def scaffold_sentinels(central):
    """Read exact unfinished messages from the central authoring assets."""
    result = set()
    for filename in sorted(set(scaffold.ASSETS.values())):
        if not filename.endswith(".py.tmpl"):
            continue
        text = (central / "templates/integration/scaffold" / filename).read_text(encoding="utf-8")
        text = re.sub(
            r"@@([a-z_]+)@@",
            lambda match: (
                "from custom_components.sentinel.const import DOMAIN"
                if match[1] == "domain_import"
                else "[]"
                if match[1] == "platforms_literal"
                else "'sentinel'"
            ),
            text,
        )
        for node in ast.walk(ast.parse(text)):
            if (
                isinstance(node, ast.Constant)
                and isinstance(node.value, str)
                and node.value.startswith("TODO:")
            ):
                result.add(node.value)
    return result


def dotted(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return dotted(node.value) + "." + node.attr
    return ""


def inactive_marker(node):
    function = node.func if isinstance(node, ast.Call) else node
    name = dotted(function)
    if name.endswith((".mark.skip", ".unittest.skip")) or name == "unittest.skip":
        return True
    if name in {"unittest.skipIf", "unittest.skipUnless"} and isinstance(node, ast.Call):
        condition = (
            node.args[0]
            if node.args
            else next((item.value for item in node.keywords if item.arg == "condition"), None)
        )
        if isinstance(condition, ast.Constant) and isinstance(condition.value, bool):
            return condition.value if name == "unittest.skipIf" else not condition.value
    if name.endswith(".mark.xfail"):
        if not isinstance(node, ast.Call):
            return True
        condition = (
            node.args[0]
            if node.args
            else next((item.value for item in node.keywords if item.arg == "condition"), None)
        )
        return (
            condition is None
            or isinstance(condition, ast.Constant)
            and condition.value in (True, "True")
        )
    if name.endswith(".mark.skipif") and isinstance(node, ast.Call):
        expression = (
            node.args[0]
            if node.args
            else next((item.value for item in node.keywords if item.arg == "condition"), None)
        )
        return isinstance(expression, ast.Constant) and expression.value in (True, "True")
    return False


def marked_inactive(nodes):
    for node in nodes:
        if isinstance(node, (ast.List, ast.Tuple)):
            if marked_inactive(node.elts):
                return True
        elif inactive_marker(node):
            return True
    return False


def has_test_functions(tree):
    """Reject known empty/entirely inactive files without claiming runtime coverage."""
    if tree is None or marked_inactive(assigned(tree, "pytestmark")):
        return False
    if any(
        isinstance(statement, ast.Expr)
        and isinstance(statement.value, ast.Call)
        and dotted(statement.value.func) == "pytest.skip"
        and any(
            keyword.arg == "allow_module_level"
            and isinstance(keyword.value, ast.Constant)
            and keyword.value.value is True
            for keyword in statement.value.keywords
        )
        for statement in tree.body
    ):
        return False
    candidates = [
        (node, False)
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    for owner in (node for node in tree.body if isinstance(node, ast.ClassDef)):
        if not owner.name.startswith("Test") and not any(
            dotted(base).endswith("TestCase") for base in owner.bases
        ):
            continue
        inactive = marked_inactive(owner.decorator_list) or marked_inactive(
            assigned(owner, "pytestmark")
        )
        candidates.extend(
            (node, inactive)
            for node in owner.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        )
    for node, inactive in candidates:
        if not node.name.startswith("test_") or inactive or marked_inactive(node.decorator_list):
            continue
        body = [
            statement
            for statement in node.body
            if not (isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Constant))
        ]
        if any(
            isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Call)
            and dotted(statement.value.func).endswith(("pytest.skip", "pytest.xfail"))
            for statement in body
        ):
            continue
        if any(
            isinstance(statement, ast.Assert)
            or isinstance(statement, ast.Call)
            and (
                dotted(statement.func).endswith("pytest.raises")
                or dotted(statement.func).split(".")[-1].startswith("assert")
            )
            for statement in ast.walk(node)
        ):
            return True
    return False


def exports(tree):
    if tree is None:
        return set()
    names = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            names.update(alias.asname or alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names.update(target.id for target in targets if isinstance(target, ast.Name))
    return names


def check(root, config, manifest_path, manifest, safe_path, central=None):
    central = Path(central or contract.CENTRAL)
    records = contract.load_contract()["records"]
    domain = manifest["domain"]
    component = f"custom_components/{domain}"
    test_prefix = f"tests/components/{domain}"
    manifest_name = manifest_path.relative_to(root).as_posix()
    errors = []
    for field in ("domain", "name", "version", "documentation", "issue_tracker", "codeowners"):
        value = manifest.get(field)
        valid = (
            isinstance(value, list)
            and bool(value)
            and all(isinstance(item, str) and item.strip() for item in value)
            if field == "codeowners"
            else isinstance(value, str) and bool(value.strip())
        )
        if not valid:
            errors.append(("HA-02", manifest_name, f"Actual manifest {field} is required"))
        elif UNFINISHED.search(json.dumps(value, ensure_ascii=False)):
            errors.append(("HA-02", manifest_name, f"Unfinished manifest {field}"))
    try:
        categories.validate_review(manifest, config.get("categories_review"))
    except ValueError as error:
        errors.append(("HA-02", manifest_name, str(error)))
    trees = {}
    for path in sorted(safe_path(root, component).glob("*.py")):
        relative = path.relative_to(root).as_posix()
        tree = python_tree(root, relative, safe_path, "HA-13", errors)
        if tree is not None:
            trees[relative] = tree
    platforms = selected_platforms(trees, errors, component)
    values = [
        (relative, value) for relative, tree in trees.items() for value in assigned(tree, "DOMAIN")
    ]
    if not values:
        errors.append(
            (
                "HA-01",
                component + "/const.py",
                "An explicit integration DOMAIN identifier must be verifiable",
            )
        )
    for relative, value in values:
        if not isinstance(value, ast.Constant) or value.value != domain:
            errors.append(
                ("HA-01", relative, "DOMAIN must match the manifest domain and directory")
            )
    flow = manifest.get("config_flow", False)
    if not isinstance(flow, bool):
        errors.append(("HA-04", manifest_name, "config_flow must be a boolean"))
    flow_file = safe_path(root, component + "/config_flow.py").is_file()
    if bool(flow) != flow_file:
        errors.append(
            ("HA-04", manifest_name, "manifest config_flow and actual config_flow.py must agree")
        )
    data = {
        "manifest": {"value": manifest},
        "configuration": {"value": "ui" if flow else "yaml"},
        "platforms": {"value": platforms},
        "features": {
            "value": {
                name: safe_path(root, component + "/" + filename).exists()
                for name, filename in (
                    ("coordinator", "coordinator.py"),
                    ("shared_entity", "entity.py"),
                    ("diagnostics", "diagnostics.py"),
                    ("actions", "services.yaml"),
                )
            }
        },
    }
    actions = registered_actions(trees, domain)
    data["features"]["value"]["actions"] = data["features"]["value"]["actions"] or bool(actions)
    init_names = exports(trees.get(component + "/__init__.py"))
    config_entries = flow or "async_setup_entry" in init_names
    if config_entries:
        for name in ("async_setup_entry", "async_unload_entry"):
            if name not in init_names:
                errors.append(
                    (
                        "HA-05",
                        component + "/__init__.py",
                        f"Config entry lifecycle hook is missing: {name}",
                    )
                )
    for platform in platforms:
        relative = component + "/" + platform + ".py"
        if relative in trees and not exports(trees[relative]).intersection(
            {"async_setup_entry"} if config_entries else {"async_setup_platform", "setup_platform"}
        ):
            errors.append(("HA-13", relative, "Selected platform setup hook is missing"))
    required_tests = {f"{test_prefix}/test_init.py"}
    # Contract conditions choose the same destinations used by the generator.
    for record in records:
        destination = record["destination"]
        condition = record["condition"]
        if (
            record["status"] != "available"
            or destination.endswith("/")
            or destination == "custom_components/{domain}/const.py"
        ):
            continue
        if not (
            destination.startswith("custom_components/")
            or destination.startswith("tests/components/{domain}/test_")
        ):
            continue
        if condition not in {
            "always",
            "ui",
            "platforms",
            "coordinator",
            "shared_entity",
            "diagnostics",
            "actions",
            "imagespec",
        }:
            continue
        try:
            applies = conditions.matches(condition, data, root, manifest_path, safe_path)
        except (ValueError, OSError, SyntaxError):
            continue  # Dedicated DOC-07/08 checks retain their existing exact errors.
        if not applies:
            continue
        for platform in platforms if condition == "platforms" else [None]:
            relative = contract.destination_path(record, domain, platform)
            rule = (
                "TEST-08"
                if relative.startswith("tests/")
                else "HA-11"
                if relative.endswith((".json", ".yaml")) and not relative.endswith("manifest.json")
                else "HA-04"
                if relative.endswith("config_flow.py")
                else "HA-13"
            )
            if not safe_path(root, relative).is_file():
                errors.append((rule, relative, "Required contract file is missing"))
            if relative.startswith("tests/") and record["id"] != "payload-test":
                required_tests.add(relative)
    test_trees = {}
    for path in sorted(safe_path(root, test_prefix).glob("test_*.py")):
        relative = path.relative_to(root).as_posix()
        tree = python_tree(root, relative, safe_path, "TEST-08", errors)
        if tree is not None:
            test_trees[relative] = tree
    for relative in sorted(required_tests):
        if safe_path(root, relative).is_file() and not has_test_functions(test_trees.get(relative)):
            errors.append(
                (
                    "TEST-07",
                    relative,
                    "Corresponding actual tests are unwritten; file existence alone is insufficient",
                )
            )
    sentinels = scaffold_sentinels(central)
    for relative, tree in {**trees, **test_trees}.items():
        if any(
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and any(node.value.startswith(message) for message in sentinels)
            for node in ast.walk(tree)
        ):
            errors.append(
                (
                    "TEST-07" if relative.startswith("tests/") else "HA-13",
                    relative,
                    "Central authoring scaffold is unfinished; replace its actual behavior/assertion sentinel",
                )
            )
    for relative in (".hass-standards.json",):
        for value in (
            config.get("repository"),
            config.get("readme", {}).get("title"),
            *config.get("readme", {}).get("descriptions", {}).values(),
        ):
            if isinstance(value, str) and (UNFINISHED.search(value) or value == "Integration Name"):
                errors.append(("DOC-01", relative, "Unfinished common README metadata"))
                break
    errors.extend(translation_errors(root, component, platforms, trees, safe_path, actions))
    errors.extend(reference_errors(root, safe_path, config))
    return errors


def flow_namespaces(trees, errors):
    """Resolve literal HA subentry registrations without executing integration code."""
    classes, bindings = {}, {}
    for relative, tree in trees.items():
        module = Path(relative).with_suffix("")
        scope = bindings[relative] = {}
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                classes[(relative, node.name)] = node
            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for target in targets:
                    if isinstance(target, ast.Name):
                        scope[target.id] = (relative, node.value)
            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    parent = module.parent
                    for _ in range(node.level - 1):
                        parent = parent.parent
                    source = (parent / (node.module or "").replace(".", "/")).as_posix() + ".py"
                    for alias in node.names:
                        scope[alias.asname or alias.name] = (source, ast.Name(id=alias.name))
                elif node.module == "homeassistant.config_entries":
                    for alias in node.names:
                        scope[alias.asname or alias.name] = alias.name
                elif node.module == "homeassistant":
                    for alias in node.names:
                        if alias.name == "config_entries":
                            scope[alias.asname or alias.name] = "homeassistant.config_entries"
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "homeassistant.config_entries" and alias.asname:
                        scope[alias.asname] = alias.name

    def resolve(relative, node, seen=()):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        if isinstance(node, ast.Attribute):
            if resolve(relative, node.value, seen) == "homeassistant.config_entries":
                return node.attr
        if isinstance(node, ast.Name):
            key = (relative, node.id)
            if key in seen:
                return None
            if key in classes:
                return key
            value = bindings.get(relative, {}).get(node.id)
            if isinstance(value, tuple):
                return resolve(*value, seen=(*seen, key))
            return value
        return None

    def is_flow(relative, owner, kind, seen=()):
        key = (relative, owner.name)
        if key in seen:
            return False
        for base in owner.bases:
            value = resolve(relative, base)
            if value == kind:
                return True
            if isinstance(value, tuple) and value in classes:
                if is_flow(value[0], classes[value], kind, (*seen, key)):
                    return True
        return False

    registered = {}
    for (relative, _), owner in classes.items():
        if not is_flow(relative, owner, "ConfigFlow"):
            continue
        for method in owner.body:
            if not isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if method.name != "async_get_supported_subentry_types":
                continue
            returns = [node for node in ast.walk(method) if isinstance(node, ast.Return)]
            for node in returns:
                if not isinstance(node.value, ast.Dict):
                    errors.append(
                        ("HA-11", relative, "Unresolved subentry type registration requires review")
                    )
                    continue
                for type_node, class_node in zip(node.value.keys, node.value.values):
                    subentry_type = resolve(relative, type_node)
                    handler = resolve(relative, class_node)
                    if (
                        not isinstance(subentry_type, str)
                        or not subentry_type
                        or not isinstance(handler, tuple)
                        or handler not in classes
                        or not is_flow(handler[0], classes[handler], "ConfigSubentryFlow")
                    ):
                        errors.append(
                            (
                                "HA-11",
                                relative,
                                "Unresolved subentry type registration requires review",
                            )
                        )
                        continue
                    registered.setdefault(handler, set()).add(subentry_type)
            if not returns:
                errors.append(
                    ("HA-11", relative, "Unresolved subentry type registration requires review")
                )
    namespaces = {}
    for (relative, name), owner in classes.items():
        if is_flow(relative, owner, "ConfigSubentryFlow"):
            types = registered.get((relative, name))
            if not types:
                errors.append(
                    ("HA-11", relative, f"Unresolved subentry translation namespace for {name}")
                )
            paths = [("config_subentries", value) for value in sorted(types or ())]
        else:
            options = (
                owner.name.endswith("OptionsFlow")
                or is_flow(relative, owner, "OptionsFlow")
                or is_flow(relative, owner, "OptionsFlowWithConfigEntry")
            )
            paths = [("options" if options else "config",)]
        for child in ast.walk(owner):
            namespaces[(relative, id(child))] = paths
    return namespaces


def translation_errors(root, component, platforms, trees, safe_path, actions=()):
    errors, documents = [], {}
    for name in ("strings.json", "translations/en.json", "translations/ko.json"):
        relative = component + "/" + name
        try:
            documents[name] = inventory.load_json(safe_path(root, relative))
        except (ValueError, OSError) as error:
            errors.append(("HA-11", relative, str(error)))
    if len(documents) != 3:
        return errors
    english, korean = documents["translations/en.json"], documents["translations/ko.json"]
    try:
        scaffold.validate_translations(english, korean)
        scaffold.validate_translations(documents["strings.json"], english)
    except ValueError as error:
        errors.append(("HA-11", component + "/translations/ko.json", str(error)))
    if documents["strings.json"] != english:
        errors.append(
            (
                "HA-11",
                component + "/translations/en.json",
                "English deployment translations must match strings.json source",
            )
        )
    for name, data in documents.items():
        if any(
            isinstance(value, str)
            and value
            in {
                "TODO: Implement the actual configuration flow.",
                "TODO: 실제 설정 흐름을 구현하세요.",
            }
            for value in leaves(data)
        ):
            errors.append(
                (
                    "HA-11",
                    component + "/" + name,
                    "Central translation authoring scaffold is unfinished",
                )
            )

    def require(keys, relative):
        value = documents["strings.json"]
        for key in keys:
            if not isinstance(value, dict) or key not in value:
                errors.append(
                    ("HA-11", relative, "Missing actual code translation key: " + ".".join(keys))
                )
                return
            value = value[key]

    namespaces = flow_namespaces(trees, errors)
    for relative, tree in trees.items():
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in {"async_show_form", "async_abort"}
            ):
                label, section = (
                    ("step_id", "step")
                    if node.func.attr == "async_show_form"
                    else ("reason", "abort")
                )
                for keyword in node.keywords:
                    if (
                        keyword.arg == label
                        and isinstance(keyword.value, ast.Constant)
                        and isinstance(keyword.value.value, str)
                    ):
                        for namespace in namespaces.get((relative, id(node)), [("config",)]):
                            require((*namespace, section, keyword.value.value), relative)
            if isinstance(node, (ast.Assign, ast.AnnAssign)):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                if (
                    any(
                        isinstance(target, ast.Name) and target.id == "_attr_translation_key"
                        for target in targets
                    )
                    and isinstance(node.value, ast.Constant)
                    and isinstance(node.value.value, str)
                    and Path(relative).stem in platforms
                ):
                    require(("entity", Path(relative).stem, node.value.value), relative)
    service_file = safe_path(root, component + "/services.yaml")
    if service_file.is_file():
        try:
            services = yaml.safe_load(service_file.read_text(encoding="utf-8"))
            if not isinstance(services, dict) or not services:
                raise ValueError("Actual action metadata is unfinished or empty")
            if any(not isinstance(name, str) or UNFINISHED.search(name) for name in services):
                raise ValueError("Actual action names are required")
            for name in sorted(set(actions) - services.keys()):
                errors.append(
                    (
                        "HA-11",
                        component + "/services.yaml",
                        f"Registered action {name!r} is missing metadata",
                    )
                )
            for name in sorted(set(actions) | services.keys()):
                if not isinstance(name, str) or UNFINISHED.search(name):
                    raise ValueError("Actual action names are required")
                require(("services", name), component + "/services.yaml")
        except (ValueError, OSError, yaml.YAMLError) as error:
            errors.append(("HA-11", component + "/services.yaml", str(error)))
    return errors


def leaves(value):
    if isinstance(value, dict):
        for child in value.values():
            yield from leaves(child)
    else:
        yield value


def reference_errors(root, safe_path, config=None):
    errors = []
    try:
        document = safe_path(root, "STANDARDS.md").read_text(encoding="utf-8")
    except (ValueError, OSError) as error:
        return [("GOV-01", "STANDARDS.md", str(error))]
    from bluetooth_documents import visible_markdown

    recorded = (config or {}).get("standards")
    if isinstance(recorded, dict) and recorded.get("kind") == "release":
        try:
            from . import reference

            recorded = reference.validate(recorded)
        except ValueError as error:
            return [("GOV-02", ".hass-standards.json", str(error))]
        release_lines = re.findall(
            r"^\s*(?:-\s*)?(?:Standards release|표준 릴리스)\s*:\s*`?(v[0-9]+\.[0-9]+\.[0-9]+)`?\s*$",
            visible_markdown(document),
            re.M,
        )
        sha_lines = re.findall(
            r"^\s*(?:-\s*)?(?:Resolved standards SHA|해석한 표준 커밋 SHA)\s*:\s*`?([0-9a-f]{40})`?\s*$",
            visible_markdown(document),
            re.M,
        )
        if release_lines != [recorded["tag"]] or sha_lines != [recorded["resolved_sha"]]:
            return [
                (
                    "GOV-02",
                    "STANDARDS.md",
                    "Release tag and resolved SHA must match .hass-standards.json",
                )
            ]
        ref, action_ref = recorded["resolved_sha"], recorded["tag"]
    else:
        ref, action_ref = None, None
    refs = re.findall(
        r"^\s*(?:-\s*)?(?:참조 커밋 SHA|Reviewed standards SHA|Standards ref)\s*:\s*`?([0-9a-f]{40})`?\s*$",
        visible_markdown(document),
        re.M,
    )
    if action_ref is None and len(set(refs)) != 1:
        return [
            (
                "GOV-02",
                "STANDARDS.md",
                "Record one reviewed full standards SHA in the reference field",
            )
        ]
    if action_ref is None:
        ref = refs[0]
        action_ref = ref
    release_fields = re.findall(
        r"^\s*(?:-\s*)?Reviewed release standards SHA\s*:\s*(.*?)\s*$",
        visible_markdown(document),
        re.M,
    )
    # A ZIP caller follows the primary reviewed release by default. The older
    # scoped full-SHA field remains an explicit compatibility override.
    release_ref = action_ref
    if release_fields:
        if len(release_fields) != 1 or not re.fullmatch(
            r"(?:[0-9a-f]{40}|`[0-9a-f]{40}`)", release_fields[0]
        ):
            return [("GOV-02", "STANDARDS.md", "Record one full reviewed release standards SHA")]
        release_ref = release_fields[0].strip("`")
    for path in sorted(safe_path(root, ".github/workflows").glob("*.yml")):
        relative = path.relative_to(root).as_posix()
        try:
            data = yaml.safe_load(safe_path(root, relative).read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                continue
            for job in data.get("jobs", {}).values():
                if not isinstance(job, dict):
                    continue
                use = job.get("uses", "")
                if isinstance(use, str) and use.startswith(
                    "eigger/hass-repo-standards/.github/workflows/"
                ):
                    if not use.endswith("@" + action_ref):
                        errors.append(
                            (
                                "GOV-02",
                                relative,
                                "Reusable workflow SHA must equal the reviewed STANDARDS SHA",
                            )
                        )
                    if (
                        any(name in use for name in ("python-tests.yml@", "dependency-update.yml@"))
                        and job.get("with", {}).get("standards-ref") != ref
                    ):
                        errors.append(
                            (
                                "GOV-02",
                                relative,
                                "standards-ref must equal the reviewed reusable workflow SHA",
                            )
                        )
                for step in job.get("steps", []):
                    use = step.get("uses", "") if isinstance(step, dict) else ""
                    expected_ref = (
                        release_ref
                        if path.name == "release.yml"
                        and isinstance(use, str)
                        and use.startswith("eigger/hass-repo-standards/actions/release-zip@")
                        else action_ref
                    )
                    if (
                        isinstance(use, str)
                        and use.startswith("eigger/hass-repo-standards/actions/")
                        and not use.endswith("@" + expected_ref)
                    ):
                        errors.append(
                            (
                                "GOV-02",
                                relative,
                                "Composite action SHA must equal the reviewed STANDARDS SHA",
                            )
                        )
        except (ValueError, OSError, yaml.YAMLError) as error:
            errors.append(("CI-01", relative, str(error)))
    return errors
