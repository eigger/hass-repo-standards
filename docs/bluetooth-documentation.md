# Bluetooth documentation rules for integration authors

This is a developer reference for DOC-07. User-facing READMEs must link to the [English setup guide](bluetooth.md) or [Korean setup guide](bluetooth.ko.md), never to this authoring guide or a library implementation contract. Keep the README introduction short; put device-specific instructions in the integration’s usage and troubleshooting documents. The default user guide is English, with a corresponding Korean version and language switch links.

## Content and ownership

- Link users to the shared setup guide for proxy selection, flashing, Home Assistant registration and common troubleshooting. Keep purchase links in that shared guide rather than duplicating them in every integration.
- Document supported models/firmware, wake-up/power requirements, pairing/bonding/authentication, other applications holding a connection, transfer restrictions and actual local/proxy validation. Preserve unverified scope; another integration’s hardware results do not validate this one.
- Separate proxy firmware configuration from integration options. BLE ESL Retry Count, Debounce and image transfer settings are not universal defaults. Do not invent retry, diagnostics or timeout features to fill a template.
- Distinguish advertisement discovery, active scanning and active GATT connections. Passive scanning does not itself prevent GATT connections. Keep default scan interval/window unless a real model requirement justifies a change.
- If common setup is reproduced locally, record the shared source and review date and maintain both languages. Review current manufacturer/ESPHome support, exact board revision, power and antenna options before recommending hardware. Do not present marketplace listings as official support evidence.

## Device-specific troubleshooting

Use [BLE ESL troubleshooting](https://github.com/eigger/hass-ble-esl/blob/main/docs/troubleshooting.md) as an organizational example: identify the failing stage, show the actual diagnostic path, then request useful evidence. Do not copy its ESL-only sensors, actions, retries, debounce or timeouts into unrelated integrations.

Provide model-specific wake-up, power, authentication and other-app conditions alongside the [shared troubleshooting](bluetooth.md#troubleshooting). Cover discovery, connection, session/authentication, transport loss, unreturned writes and completion confirmation as applicable. Retry/backoff, connection lifetime, bonding and transfer pacing belong to the actual integration policy; blesession does not guarantee automatic reconnection or retries for every error. Do not impose a universal timeout or RSSI threshold.

Describe only diagnostics and logging paths the integration really exposes. Where available, map `failed_stage`, `failed_detail`, `likely_cause_key`, `error`, `via`, `via_type`, `rssi`, `paths` and `via_unconfirmed` to the integration’s user-facing errors. Do not promise these fields in every integration. Distinguish the best advertisement receiver from the confirmed connection route; label an unconfirmed route as an estimate.

Request Home Assistant/integration/ESPHome/blesession versions when available, device and proxy models/revisions, connection method, failure time/stage and reproduction steps. Keep successes and failures separate. Explain the actual logger name, collect only the reproduction interval and turn debug logging off afterward. Remove addresses, credentials, tokens and personal data from public logs, traces and diagnostics.

The developer boundary is documented in the [blesession contract](https://github.com/eigger/blesession/blob/main/docs/contract.md) and [adoption guide](https://github.com/eigger/blesession/blob/main/docs/adopting.md). These are implementation references, not the setup destination for end users.

## README link examples

English `README.md`:

```markdown
For a remote Bluetooth connection, follow the [Bluetooth proxy setup guide](https://github.com/eigger/hass-repo-standards/blob/main/docs/bluetooth.md).
See the integration’s device preparation and troubleshooting document for model-specific requirements.
```

Korean `README.ko.md`:

```markdown
원격 Bluetooth 연결은 [Bluetooth proxy 설정 안내](https://github.com/eigger/hass-repo-standards/blob/main/docs/bluetooth.ko.md)를 따르세요.
모델별 준비 조건은 이 통합의 기기 준비와 문제 해결 문서를 확인하세요.
```

Add the integration’s actual local troubleshooting link, using the matching language or an explicit language label. This central guide does not authorize edits to other repositories by itself.
