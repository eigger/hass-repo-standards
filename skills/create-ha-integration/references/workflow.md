# New integration workflow

In commands, `<central>` is a confirmed central checkout, `<sha>` its reviewed full 40-character SHA, `<target>` the authorized missing/empty output path, and `<work>` an existing directory outside the target. An immutable release additionally needs exact `<release>` and successful `<work>/release-verification.json`; its tools still run from `<sha>`. Substitute actual confirmed paths; these are interface examples, not execution evidence.

## Establish the source and input

1. Confirm central `git rev-parse HEAD` equals `<sha>`, its execution assets are clean and `templates/integration/contract.json` has `schema_version: 1`. Use the same revision's rules, schemas, templates and tools. Ask for a missing checkout/ref rather than inferring a path from the skill install directory. The CLI also enforces the revision and dirty-asset checks.
2. Read `<central>/AGENTS.md`, README.md, docs/adoption.md, docs/checklist.md, docs/home-assistant.md and docs/testing.md for first adoption. Read only the relevant CLI/input sections of docs/template-skill-usage.md. Use docs/adoption.md for review/status scope; T1–T6 design/history is not required for routine generation.
3. Collect actual design decisions as `value`/`source` input against `<central>/schemas/integration-input.schema.json`: repository/remote/default branch, domain/manifest, bilingual common text, actual license, configuration/platforms/features and separate minimum/current HA/Python/plugin environments. Use the usage document's schema example as syntax only. Missing device/client/entry/flow/action facts are questions or pending work, never invented defaults. Keep new dependencies in the declaration locations required by docs/dependencies.md.

## Inspect, plan and route the request

```text
python3 "<central>/scripts/manage_integration.py" inspect "<target>" --output "<work>/inventory.json"
python3 "<central>/scripts/manage_integration.py" plan "<target>" --mode create --input "<work>/input.json" --standards-ref <sha> --output "<work>/plan.json"
# Published immutable release only:
python3 "<central>/scripts/manage_integration.py" verify-release --repository eigger/hass-repo-standards --tag <release> --resolved-sha <sha> --output "<work>/release-verification.json"
python3 "<central>/scripts/manage_integration.py" plan "<target>" --mode create --input "<work>/input.json" --standards-ref <sha> --release-tag <release> --release-verification "<work>/release-verification.json" --output "<work>/release-plan.json"
```

Inventory is observations, not a replacement for sourced input. Read command exit status, pending/conflicts and each operation/diff. Nonempty targets must use the existing-adoption workflow; do not erase them to fit create. For review-only requests, report the plan and remaining facts and stop here.

If the request includes generation and the plan has no conflicts, apply without re-requesting the same authorized scope:

```text
python3 "<central>/scripts/manage_integration.py" apply "<target>" --plan "<work>/plan.json" --journal "<work>/journal.json"
```

An error stops dependent steps; report its actual rule/path or required input and correct the cause before replanning. Never change a failure into success. A partial apply retains the journal and its `.plan.json` anchor; use the documented `recover <target> --journal "<work>/journal.json"` only to recover that transaction, preserving later user edits. See the central usage document for its guards and limits.

After generation, plan the same input in **adopt** mode and inspect that operations are empty; create is intentionally invalid on a populated target. Remaining pending work does not disappear with an empty diff.

## Complete actual behavior and verify

The generated files are authoring scaffolds. Follow docs/home-assistant.md and docs/testing.md to complete the actual client/entry/flow/platform and external-boundary fixtures; retain real HA setup/platform/unload tests. Use central renderers for common structure, not manual substitutes. A request limited to skeleton generation leaves those device tasks pending rather than expanding its scope.

Use real requirement/import observations to select conditional guidance: docs/bluetooth-documentation.md for blesession and docs/payload-documentation.md for imagespec, plus docs/documentation.md and docs/dependencies.md as applicable. Read those exact central revision sources instead of copying their contracts here. Actual payload actions/production adapters/device conditions must come from real implementation; if unavailable, record pending work. Do not send device commands to validate examples.

```text
python3 "<central>/scripts/check_integration.py" "<target>" --check
```

Run the applicable real HA domain tests using each exact minimum/current environment and the payload contract where applicable, following the central documents. Static check success is not HA behavior or translation-meaning validation. The primary agent implements and verifies by default; use GOV-05 in docs/adoption.md to select self-review or independent review; report missing environments and failed/skipped checks honestly.

Record this run's reviewed SHA, actual target commit, commands, installed versions, results, exceptions, CI links and limits in STANDARDS.md/ADOPTION_CHECKLIST.md using central templates. Do not reuse past PASS. Follow the central adoption-status procedure only for the authorized target row. The final report distinguishes generated structure, real behavior, static/HA evidence, remaining work and any central status not updated. This skill does not authorize external installation, commit/push/PR, workflow dispatch, releases or unrelated repositories.
