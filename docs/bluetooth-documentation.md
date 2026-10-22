# Bluetooth documentation rules for integration authors

This is a developer reference for DOC-07. User-facing READMEs must link to the [English setup guide](https://github.com/eigger/blesession/blob/main/docs/bluetooth.md) or [Korean setup guide](https://github.com/eigger/blesession/blob/main/docs/bluetooth.ko.md), never to this authoring guide or a library implementation contract. Keep the managed header introduction to one line. The integration owns the structure of its remaining README content; preserve existing device instructions and do not move them merely to apply common standards. Link the actual user setup and troubleshooting guidance. The default user guide is English, with a corresponding Korean version and language switch links.

## Content and ownership

- Link users to the shared setup guide for proxy selection, flashing, Home Assistant registration and common troubleshooting. Keep purchase links in that shared guide rather than duplicating them in every integration.
- Document supported models/firmware, wake-up/power requirements, pairing/bonding/authentication, other applications holding a connection, transfer restrictions and actual local/proxy validation. Preserve unverified scope; another integration’s hardware results do not validate this one.
- Separate proxy firmware configuration from integration options. BLE ESL Retry Count, Debounce and image transfer settings are not universal defaults. Do not invent retry, diagnostics or timeout features to fill a template.
- Distinguish advertisement discovery, active scanning and active GATT connections. Passive scanning does not itself prevent GATT connections. Keep default scan interval/window unless a real model requirement justifies a change.
- blesession owns the public common proxy device recommendations, setup, Home Assistant registration and general troubleshooting. Link to that source instead of maintaining a second common guide here or in each integration. Reading the general guide never requires installing blesession; integrations that do not use the library may use it too. Manufacturer support and exact board revisions remain evidence for recommendations, not marketplace listings.

## Device-specific troubleshooting

The fixed bilingual template and automated checks below apply to blesession-using integrations. Proxy-only integrations retain the existing manually reviewed DOC-07 setup links and model conditions; general proxy support alone is not evidence of blesession use.

Every blesession-using integration must provide `docs/troubleshooting.md` and `docs/troubleshooting.ko.md` using the [English device template](../templates/integration/docs/troubleshooting.md) and [Korean device template](../templates/integration/docs/troubleshooting.ko.md). Fixed H2 headings, in order:

| English | 한국어 |
|---|---|
| Common troubleshooting | 공통 문제 해결 |
| Device-specific checks | 기기별 확인 사항 |
| Symptoms and actions | 증상과 조치 |
| Diagnostics and logs | 진단 및 로그 |
| If the problem persists | 문제가 계속되는 경우 |

Use H3 headings for device-specific additions. The symptoms table has `Symptom / Failing stage / Checks / Action` (Korean: `증상 / 실패 단계 / 확인 사항 / 조치`). Replace every scaffold placeholder with actual information or honest N/A and a reason. Preserve existing model-specific troubleshooting while fitting it into these sections; do not delete content or replace it with generic boilerplate.

The first section links to matching-language common troubleshooting in blesession. Each document links back to its matching README and to the other language. The last section links to the integration's existing Issues or issue template and reuses its reporting instructions; do not duplicate a reporting form or create a new issue template for this task. English and Korean READMEs must link to their respective local troubleshooting page and to the matching-language blesession proxy guide. Preserve existing README sections and notices when adding these links.

Provide model-specific wake-up, power, authentication and other-app conditions alongside the [shared troubleshooting](https://github.com/eigger/blesession/blob/main/docs/troubleshooting.md). Cover discovery, connection, session/authentication, transport loss, unreturned writes and completion confirmation as applicable. Retry/backoff, connection lifetime, bonding and transfer pacing belong to the actual integration policy; blesession does not guarantee automatic reconnection or retries for every error. Do not impose a universal timeout or RSSI threshold.

Describe only diagnostics and logging paths the integration really exposes. Where available, map `failed_stage`, `failed_detail`, `likely_cause_key`, `error`, `via`, `via_type`, `rssi`, `paths` and `via_unconfirmed` to the integration’s user-facing errors. Do not promise these fields in every integration. Distinguish the best advertisement receiver from the confirmed connection route; label an unconfirmed route as an estimate.

Request Home Assistant/integration/ESPHome/blesession versions when available, device and proxy models/revisions, connection method, failure time/stage and reproduction steps. Keep successes and failures separate. Explain the actual logger name, collect only the reproduction interval and turn debug logging off afterward. Remove addresses, credentials, tokens and personal data from public logs, traces and diagnostics.

The developer boundary is documented in the [blesession contract](https://github.com/eigger/blesession/blob/main/docs/contract.md) and [adoption guide](https://github.com/eigger/blesession/blob/main/docs/adopting.md). These are implementation references, not the setup destination for end users.

## README link examples

English `README.md`:

```markdown
For a remote Bluetooth connection, follow the [Bluetooth proxy setup guide](https://github.com/eigger/blesession/blob/main/docs/bluetooth.md).
See [device-specific troubleshooting](docs/troubleshooting.md) for model-specific requirements.
```

Korean `README.ko.md`:

```markdown
원격 Bluetooth 연결은 [Bluetooth proxy 설정 안내](https://github.com/eigger/blesession/blob/main/docs/bluetooth.ko.md)를 따르세요.
모델별 준비 조건은 이 통합의 [문제 해결](docs/troubleshooting.ko.md)을 확인하세요.
```

Add the integration’s actual local troubleshooting link, using the matching language or an explicit language label. This central guide does not authorize edits to other repositories by itself.

## Enforcement and review

The shared Validate action detects blesession from the manifest's parsed Python requirement identity (including extras, operators and environment markers) or an actual absolute Python import. It checks both documents, fixed headings/order, populated symptom table, mandatory language/source/README/Issues links and unfinished placeholders. Comments and code blocks cannot stand in for rendered headings, links or section content. The checker does not establish diagnostic accuracy, valid hardware advice, verified routes or correct translation: review compares the installed library API, device behavior, existing issue destination and both languages, with independent review required according to GOV-05. Use the existing DOC-07 exception procedure for an approved difference; record the exact rule and affected file, never treat a missing language as passing through an exception for another file.
