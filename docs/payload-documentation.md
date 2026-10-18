# imagespec payload documentation rules for integration authors

DOC-08 is project policy. imagespec owns the common [English payload guide](https://github.com/eigger/imagespec/blob/main/docs/payload.md) and [Korean payload guide](https://github.com/eigger/imagespec/blob/main/docs/payload.ko.md): syntax, elements, properties, common examples, colors, rotation and dithering. Do not maintain a second common reference here or replace a working integration's existing instructions with generic library examples. Reading the guide does not require installing the library. The library guide's bare payload is not a runnable HA action wrapper.

## Integration-owned documents

Every imagespec-using integration must provide `docs/payload.md` and `docs/payload.ko.md`, applying the [English template](../templates/integration/docs/payload.md) and [Korean template](../templates/integration/docs/payload.ko.md). Keep these H2 headings in order; use H3 for model-specific additions:

| English | 한국어 |
|---|---|
| Common payload guide | 공통 payload 안내 |
| Using payloads in this integration | 이 통합에서 payload 사용 |
| Minimal working example | 최소 동작 예제 |
| Device output settings | 기기 출력 설정 |
| Supported features and limitations | 지원 기능과 제한 |
| Troubleshooting | 문제 해결 |

Describe the actual HA action name, target, payload path, dimensions/palette, font availability and device limitations. Explain actual HA template/font/history processing and unavailable capabilities without inventing features. Preserve existing README content, device examples and model-specific restrictions. Add language-matched README→payload document links and document→README/language-switch/common-guide links. Troubleshooting links to existing local troubleshooting or the integration's existing Issues/issue template; do not duplicate reporting forms or create a new issue template.

## Runnable action examples

Examples are actual `.yaml` files under `examples/payload/`, linked from both local payload documents. They contain this integration's real complete HA action wrapper, target and data, rather than a library-only sequence or invented universal action name. The central `minimal.yaml` scaffold is intentionally incomplete and fails validation until replaced. Every local action YAML linked anywhere in a payload document must be registered in `.hass-standards.json` and executed by the contract; unrelated repository YAML is outside this rule.

The conditional `payload` object is required when actual imagespec requirements or absolute imports are found. It is omitted from the generic `.hass-standards.json` template because a device/action/path/palette must not be invented:

```json
{
  "payload": {
    "examples": [
      {
        "path": "examples/payload/minimal.yaml",
        "payload_path": ["data", "payload"],
        "payload_format": "list",
        "expected_size": [296, 128],
        "expected_palette": ["#000000", "#ffffff"]
      }
    ]
  }
}
```

These are illustrative device values and an illustrative nested path, not defaults to impose. Read the actual integration schema/model and set the real values. `payload_path` identifies the payload after actual HA template preparation and registered schema normalization. Optional `payload_format` is `"list"` by default; use `"yaml"` when the actual action YAML supplies a YAML-string payload. After real HA/schema preparation the contract accepts that string or a list already parsed by the actual schema, decodes when needed with safe YAML loading, and compares the element list to the integration’s actual prepared payload. `PreparedPayload.payload` remains the final list from the production preparation path, not an adapter’s invented parser. Check the real action API and schema normalization without rewriting them to satisfy the checker. Real unresolved Jinja is deferred by static checks to actual HA preparation; it is not accepted as proof of a valid rendered payload. Rendered output size may differ from canvas size with device rotation policy. Use actual output colors, not a generic palette. Real Jinja expressions are permitted; unfinished `REPLACE_*`, TODO and sample-repository tokens are not.

## Executable HA and renderer contract

For imagespec integrations copy the optional central `tests/components/example/test_payload_examples.py` scaffold to the actual domain. Do not replace its failure with `pass`. The central pytest collector runs a centrally shipped test module in the caller domain's fixture scope. A plain pytest invocation without the plugin intentionally fails this scaffold. The shared workflow runs the mandatory contract first, then excludes only this scaffold from the ordinary regression run after success. A skipped, xfailed or deselected contract cannot pass.

Provide two integration-owned fixtures in the domain `conftest.py`:

- `payload_example_setup`: uses real `hass`, the real HA plugin, config entry setup and the actual registered integration action. Mock only external I/O. Do not replace HA loaders, entry managers or schemas.
- `payload_example_adapter`: a factory called with `(hass, example_metadata, normalized_action, schema_data)`. Return `hass_standards_payload.PreparedPayload(payload, context, render_options, prepare)`, using the integration's real preparation path. `prepare` is a bound/partial/async callable from the actual integration, returning its rendered PIL image without sending a device command. `context` is the actual installed imagespec `RenderContext`; `render_options` contains its real width/height and any actual rotate/rotate_mode/background/dither options. The factory may bind real function arguments; it must not reimplement rendering or return unrelated test payloads.

Import `PreparedPayload` lazily **inside the `payload_example_adapter` factory**, when the central contract actually calls it. Do not import `hass_standards_payload` or import imagespec solely for this contract at the top level of the domain `conftest.py`: ordinary regression runs and marker-inactive environments must collect without central tooling on PYTHONPATH or an otherwise inactive imagespec installation. Type-only imports may use `TYPE_CHECKING` with annotations that do not evaluate those names at runtime. Keep the integration’s genuine runtime dependencies unchanged; this instruction avoids adding a test-only collection dependency.

The central test validates the complete YAML through actual HA `SCRIPT_SCHEMA`, resolves action/target/data using HA's actual service preparation helper, and validates data against the registered service schema. It validates the real loaded integration and its actual registered action, including legitimate Core/entity-service routes when their actual target entity belongs to the loaded integration in the real entity registry; it never dispatches the HA action. It binds the declared normalized payload to the preparation result, invokes the real integration renderer and independently runs public `imagespec.validate()` and `render()` in the installed environment. Both images must match, have the documented dimensions, and use only the documented palette. Real templates, fonts and history use actual HA/integration fixtures; tests must cover these actual supported contexts without device/network access.

Provenance checks cannot prove an adapter's semantics by themselves. Independent review must verify the adapter invokes the production preparation path, shares actual context/settings and mocks only external boundaries; do not manufacture an entry/service/schema solely to pass an adoption check. The central runtime regression fixture is explicitly a tiny test integration for testing this checker, not a template for users to claim hardware support.

## Current/minimum environments and shared CI

The contract consumes the already installed imagespec; it installs no replacement package. For a range, required HA jobs collectively cover current and the exact declared minimum, with `minimum-packages` including imagespec. For one exact pin the same installed-version run may satisfy both. Preserve support minima and existing HA minimum/current jobs. If an actual old package lacks the needed public API, report its installed version and compatibility gap, repair compatibility or seek an explicit scoped exception; never silently upgrade its minimum or claim validation without execution.

Each reusable caller supplies `standards-ref` equal to its reviewed full workflow SHA. The reusable workflow preserves caller checkout, preflights a reserved tooling path, checks out that exact central SHA separately and invokes `actions/check-payload` through its local composite action. Scripts use `github.action_path`. The template's `main` is only an adoption placeholder and must be replaced after a real reviewed commit exists. Unit-profile and non-imagespec callers keep their previous behavior.

Publish the imagespec common guides first and verify their URLs, then publish the central rules/templates. Local drafts do not mean a remote guide exists. No part of this policy authorizes editing other integrations, copying AGENTS.md, pushing, issuing device commands, or changing support/version metadata outside the requested scope.

## Scope limits, exceptions and evidence

Some imagespec consumers render internally without accepting a user payload action; others use YAML setup without config entries. Do not add a payload feature, action, config entry, entity or fake registration merely to satisfy this template/contract. Record which user-documentation and executable-example items are N/A and why, using actual source/schema evidence. Adapt the central template/contract first for a generally supported pattern, or obtain an explicitly scoped user-approved DOC-08 exception before applying a deviation. A missing action or public API is not a PASS, and it does not authorize raising a support minimum.

The static checker's exception record does not automatically waive a separately running runtime contract. Confirm that the actual runtime path supports the approved scope; if not, the runtime remains blocked: record the remaining gate and repair/adapt it before claiming successful adoption. Do not suppress a required contract via an unrelated skip, deselection or package change. A declared imagespec requirement keeps DOC-08 documentation applicable even when its marker is inactive in one matrix environment. The shared workflow records that environment as N/A with no payload-version coverage, skips only the tooling checkout/runtime action, and continues ordinary HA regressions while excluding only the managed payload scaffold. Current and exact-minimum coverage must still come from compatible environments where the marker is provably active. A Python minor-only matrix value cannot prove a `python_full_version` condition requiring a patch; supply an actual compatible patch environment or record the unresolved coverage gap. Active environments missing the installed package fail with an actionable error; the contract does not install a replacement. A direct local runtime invocation in an inactive environment also cannot claim coverage. This matrix N/A is distinct from a static approved exception or a skipped required example in an active contract.

Independent review compares the YAML with the actual exposed action and target, verifies schema/template normalization and production preparation/context semantics, and distinguishes optional capabilities from required device features. It checks all declared examples executed, actual installed versions match their environments, output dimensions/palette match the device policy, existing README/examples are preserved and translations agree. Runtime checks alone cannot prove correct device support or hardware output.

## Local execution in an already resolved HA environment

Use the target integration's own compatible Python/HA/plugin environment with its manifest and test dependencies already resolved, including the actual imagespec version being checked. Set the following values to the reviewed central checkout and actual integration domain, then run from the target repository root:

```bash
export STANDARDS_CHECKOUT=/path/to/reviewed/hass-repo-standards
export PAYLOAD_REPOSITORY="$PWD"
export PAYLOAD_DOMAIN=your_actual_domain
export PYTHONPATH="$STANDARDS_CHECKOUT/scripts${PYTHONPATH:+:$PYTHONPATH}"
python -m pip check
python -m pytest -p hass_standards_payload "tests/components/$PAYLOAD_DOMAIN/test_payload_examples.py" -v
```

The path/domain above are substitution instructions, not metadata defaults. Do not install a newer renderer after resolving the environment. For ordinary regression tests, the shared workflow excludes only the exact scaffold after this contract succeeded; a direct local run of the whole domain can likewise exclude that scaffold only after a separate successful contract run. Keep other tests intact. Record the target commit, central SHA, command, actual Python/HA/plugin/imagespec versions, each example's result and relevant CI link. A central checker test using its own tiny fixture integration validates the checker, not every consumer integration.
