# Development and inspection

**English** | [한국어](development.ko.md)

**Creating this repository does not change existing repository files or CI.** Install development dependencies before running these inspection and validation commands:

```bash
python3 -m pip install -r requirements_dev.txt
python3 scripts/audit_repositories.py --root .. --output /tmp/hass-ci-audit.json
python3 scripts/audit_repositories.py --github-owner eigger --output /tmp/hass-ci-remote.json
python3 -m unittest discover -s tests -v
python3 scripts/check_repository.py
```

Badges are updated only inside their managed block. Read the [usage instructions](documentation.md) first.

```bash
python3 scripts/sync_badges.py ../hass-example --check
```

Follow the [central template instructions](../templates/integration/USAGE.md) for adoption and checks. README content outside managed regions remains unchanged.

```bash
python3 scripts/check_integration.py ../hass-example
```

The shared Validate checker also enforces DOC-07 for integrations using blesession: bilingual local troubleshooting documents, fixed section/table structure and language/source/support links. Its offline checks do not verify hardware, translations, diagnostics semantics or remote issue-template availability. Common user instructions live in blesession; the central repository keeps authoring rules and templates.

Run the local integration checker with Python matching or newer than the target integration’s syntax. The standalone standards caller example uses Python 3.14 to parse current integration and test sources. This is a tooling interpreter choice; it does not raise the integration’s minimum HA/Python support or remove minimum-version tests. Central tool-only unit tests retain Python 3.9 compatibility separately.

For imagespec integrations, DOC-08 requires the actual HA/renderer contract in the [payload authoring rules](payload-documentation.md); static Validate checks do not replace execution. Each HA job uses its resolver-installed current or exact minimum package unchanged. `actions/check-payload` installs no packages. For local reproduction, connect the reviewed central scripts through PYTHONPATH and run the domain scaffold with the `hass_standards_payload` plugin in that same environment, using the variables and command in the authoring rules. Do not replace the scaffold with a passing plain-pytest test. Publish common guides to imagespec’s actual default branch and verify their URLs before publishing central policy. Local drafts, central-tool tests and hardware validation are separate evidence.


## Manifest dependency automation validation (2026-11-16)

Codex root implements the opt-in controller/caller/installer on base `9ef8dd408d36602aaa3d97024fe6dc54a836b3c5`; no existing updater input or permission is changed. The implementation plan is to centralize same-major manifest-only bot validation, test and independently review the privileged boundary, publish REL-06 v1.3.0, then bootstrap the 12 detected consumers. This is a scoped CI feature, not an integration support-minimum change.

Local macOS arm64 / Python 3.14.5 / packaging26.3 / PyYAML6.0.3 / Ruff0.17.4: `TMPDIR=/private/tmp python -m unittest discover -s tests -v` **291 tests PASS (81.913s)**; the 14 new manifest behavior/workflow fixtures pass separately. Initial use of macOS's symlinked default temporary directory failed the existing symlink guards; canonical TMPDIR rerun passed without guard changes. `python3 scripts/check_repository.py` passes 42 documents/22 workflows/contracts; Ruff check/format114 files, diff check and checksum-verified actionlint1.7.12 pass.

GOV-05 independent `review_compat` review found and resolved immutable-tree verification, mutable dispatch ref, non-atomic branch deletion and installer input gaps. Final review has no blocking findings; independently reran all14 new tests and exercised real Git SHA-leased deletion in a temporary bare repository (unchanged tip deleted, advanced tip rejected/preserved). REST merge expected-base limitation is documented in dependency-automation.md rather than claimed atomic. No remote controller run or hardware validation is claimed by these local results. Exact PR head, central CI and release attestation are recorded in the rollout PR; consumer CI/release results are recorded per consumer.
