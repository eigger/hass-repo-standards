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
