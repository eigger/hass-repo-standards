# Home Assistant Repository Standards

**English** | [한국어](README.ko.md)

Shared development, documentation, HACS, CI, dependency, and release rules for Home Assistant custom integrations, with reusable workflows. This repository uses **main and commit history**, without tags or GitHub Releases.

Detailed rules are maintained in Korean; code identifiers, logs, and CI job names use English. Official requirements are distinguished from project policy. Existing repositories migrate gradually and record the reviewed standards commit and any exceptions.

## Rules

| Document | Scope |
|---|---|
| [Adoption and change management](docs/adoption.md) | Required/recommended rules, migration, exceptions |
| [Central adoption status](docs/adoption-status.md) | Progress, changes, verification/review evidence, remaining work |
| [Recommended adoption order](docs/adoption-plan.md) | Pilot and phased adoption for 22 eligible HA integrations |
| [Integration adoption checklist](docs/checklist.md) | Status, evidence, compatible environments, exceptions |
| [Home Assistant development](docs/home-assistant.md) | Core-like structure, configuration, async, entities, BLE |
| [HACS and distribution](docs/hacs.md) | manifest, hacs.json, versions, packaging |
| [README and badges](docs/documentation.md) | English README.md, Korean README.ko.md, badge rules |
| [Testing and compatibility](docs/testing.md) | tests/components/domain, real HA fixtures/loading, minimum versions |
| [CI rules](docs/ci.md) | Shared workflows, permissions, events, timeouts, extensions |
| [Dependency management](docs/dependencies.md) | Declarations, additions, HA test dependencies, updates, minimums |
| [Shared Bluetooth setup](docs/bluetooth.md) | Proxy configuration, recommended devices/revisions, blesession documentation |
| [Releases and maintenance](docs/releases.md) | Versions, changelogs, migration, support status |
| [Repository CI inventory](docs/ci-audit.md) | Local hass* workflow comparison and migration plan |
| [Initial implementation validation](docs/validation.md) | Test environment and verified scope |
| [Official references](docs/sources.md) | Sources and verification dates |

HACS custom integrations use implementation and test structures similar to Core. Every integration provides an English README.md and a Korean README.ko.md, linked to each other. Add a dynamic Usage badge from its manifest domain before Analytics data becomes available; a missing result or failed request does not mean zero installs.

The hass-kibble pilot completed adoption, real HA validation, and the README language and Usage follow-up. The hass-catprinter second pilot also completed adoption and independent minimum/current HA and final CI validation. Other integrations follow the scope and order recorded in the central status table.

## Starting work in a repository

Install the [AGENTS.md entry template](templates/integration/AGENTS.md), then request “Apply the shared standards” (or “공통 규칙 적용해줘”). The instructions require reading the central AGENTS.md, relevant rules, and checklist. Separate subagents implement and independently review/verify changes; the coordinating agent integrates results and updates the central status. The entry instructions were applied and verified in hass-kibble; they are not automatically installed elsewhere.

## Shared CI

| File | Purpose |
|---|---|
| [.github/workflows/validate-integration.yml](.github/workflows/validate-integration.yml) | Parallel HACS and Hassfest validation |
| [.github/workflows/python-tests.yml](.github/workflows/python-tests.yml) | Ruff, Python matrix, manifest installation, HA component requirements, pytest |
| [.github/workflows/dependency-update.yml](.github/workflows/dependency-update.yml) | Stable package lookup, manifest update, one update PR |
| [actions/python-environment](actions/python-environment/action.yml) | Consistent Python dependencies for test/browser jobs |
| [actions/update-manifest](actions/update-manifest/action.yml) | Updates for imagespec, blesession, and other packages |

See [templates/integration](templates/integration/README.md) for callers. Shared workflows check out the calling repository. Paths, Python, dependencies, HA components, and excluded checks are inputs. Browser, card, Android, and add-on builds remain in their repositories.

[Development and inspection](docs/development.md) covers local setup, audit commands, tests, and badge checks.

## Support and license

Use [Issues](https://github.com/eigger/hass-repo-standards/issues) for bug reports, questions, and feature requests. Discussions is currently disabled.

Released under the [MIT License](LICENSE).
