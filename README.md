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
| [Template and skill implementation plan](docs/template-skill-plan.md) | Contracts, templates, CLI and skills; T1–T6 implemented and independently verified; T6 PR CI passed, with merge status tracked in [PR #7](https://github.com/eigger/hass-repo-standards/pull/7) (Korean) |
| [Template and skill usage](docs/template-skill-usage.md) | Inspection, planning, application/recovery, static checks and explicit skill installation; device behavior requires implementation (Korean) |
| [Template and skill validation](docs/template-skill-validation.md) | Stage status, commands, environments, evidence and remaining work (Korean) |
| [Integration adoption checklist](docs/checklist.md) | Status, evidence, compatible environments, exceptions |
| [Home Assistant development](docs/home-assistant.md) | Core-like structure, configuration, async, entities, BLE |
| [HACS and distribution](docs/hacs.md) | manifest, hacs.json, versions, packaging |
| [README and badges](docs/documentation.md) | English README.md, Korean README.ko.md, badge rules |
| [Testing and compatibility](docs/testing.md) | tests/components/domain, real HA fixtures/loading, minimum versions |
| [CI rules](docs/ci.md) | Shared workflows, permissions, events, timeouts, extensions |
| [Dependency management](docs/dependencies.md) | Declarations, additions, HA test dependencies, updates, minimums |
| [Payload documentation rules](docs/payload-documentation.md) | Required bilingual device guides and executable HA/imagespec examples; common [English](https://github.com/eigger/imagespec/blob/main/docs/payload.md) / [한국어](https://github.com/eigger/imagespec/blob/main/docs/payload.ko.md) guide owned by imagespec |
| [Bluetooth documentation rules](docs/bluetooth-documentation.md) | Authoring requirements and user-guide links |
| [Bluetooth proxy user guide](https://github.com/eigger/blesession/blob/main/docs/bluetooth.md) | Common user guide maintained in blesession ([한국어](https://github.com/eigger/blesession/blob/main/docs/bluetooth.ko.md)); [common troubleshooting](https://github.com/eigger/blesession/blob/main/docs/troubleshooting.md) |
| [Releases and maintenance](docs/releases.md) | Versions, changelogs, migration, support status |
| [Repository CI inventory](docs/ci-audit.md) | Local hass* workflow comparison and migration plan |
| [Initial implementation validation](docs/validation.md) | Test environment and verified scope |
| [Official references](docs/sources.md) | Sources and verification dates |

Applicable integrations record one to three product categories and the evidence for their selection under [HA-02](docs/home-assistant.md#통합-제품-카테고리-ha-02); entity, system and virtual integrations omit the key with a recorded reason. This is project policy; upstream currently treats a missing category as optional/a HACS warning. Categories are never inferred from entity platforms.

HACS custom integrations use implementation and test structures similar to Core. Every integration provides an English README.md and a Korean README.ko.md, linked to each other. HACS Default integrations and ZIP-distributed Custom integrations show Downloads across all GitHub release assets; Custom integrations without ZIP distribution use a dynamic Usage badge from their manifest domain before Analytics data becomes available. Both provide a repository-specific My Home Assistant HACS badge in their installation guidance. Missing data or a failed request does not mean zero installs.

The hass-kibble pilot completed adoption, real HA validation, and the README language and Usage follow-up. The hass-catprinter second pilot also completed adoption and independent minimum/current HA and final CI validation. Other integrations follow the scope and order recorded in the central status table.

## Starting work in a repository

Request “Apply the shared standards from eigger/hass-repo-standards” (or “hass-repo-standards 공통 규칙 적용해줘”), providing the central checkout path or repository URL when needed. The agent reads the central [AGENTS.md](AGENTS.md), relevant rules, and checklist directly for that adoption task. The primary agent implements and verifies changes by default; [GOV-05](docs/adoption.md#채택) defines when independent review is required. For follow-up work, read the changed rules and relevant sections, and update central status at the start, end, or a meaningful state change.

Do not copy, generate, append, or install the central AGENTS.md or its contents as an agent entry file in the integration, even under another filename. Do not reinstall it without a separate user request. Preserve existing repository-specific instructions. Record the reviewed standards SHA and exceptions in STANDARDS.md and the verification evidence for that adoption in ADOPTION_CHECKLIST.md; past PASS results do not validate later changes.

Managed README regions, the test foundation, and shared CI must follow central templates and automated checks. Each repository retains its remaining README structure and content. English and Korean versions carry the same structure and information, with translation meaning reviewed according to GOV-05. Deviations require a central template change or explicit user approval before application, with evidence and scope recorded. The agent requests approval; CI does not wait for approval.

blesession owns common Bluetooth proxy recommendations, setup and troubleshooting. This repository maintains authoring rules, bilingual device-specific troubleshooting templates and their shared Validate checks. Reading the general proxy guide does not require installing blesession. Existing central guide URLs remain as move notices.

## Shared CI

| File | Purpose |
|---|---|
| [.github/workflows/validate-integration.yml](.github/workflows/validate-integration.yml) | Parallel HACS and Hassfest validation |
| [.github/workflows/python-tests.yml](.github/workflows/python-tests.yml) | Ruff, Python matrix, manifest installation, HA component requirements, pytest |
| [.github/workflows/dependency-update.yml](.github/workflows/dependency-update.yml) | Stable package lookup, manifest update, one update PR |
| [actions/python-environment](actions/python-environment/action.yml) | Consistent Python dependencies for test/browser jobs |
| [actions/update-manifest](actions/update-manifest/action.yml) | Updates for imagespec, blesession, and other packages |

See [templates/integration](templates/integration/USAGE.md) for callers. Shared workflows check out the calling repository. Paths, Python, dependencies, HA components, and excluded checks are inputs. Browser, card, Android, and add-on builds remain in their repositories.

[Development and inspection](docs/development.md) covers local setup, audit commands, tests, and badge checks.

## Support

- [Issues](https://github.com/eigger/hass-repo-standards/issues): Report bugs or request features.

Questions currently also use Issues. Discussions is disabled.

## License

Released under the [MIT License](LICENSE).
