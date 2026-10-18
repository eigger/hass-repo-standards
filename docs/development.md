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
