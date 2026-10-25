# Existing integration workflow

`<central>` is a separately confirmed central checkout, `<sha>` the reviewed full 40-character SHA, `<target>` the authorized existing integration and `<work>` an existing directory outside it. An immutable release additionally needs exact `<release>` and successful `<work>/release-verification.json`; its tools still run from `<sha>`. Substitute actual confirmed paths; these are interface examples, not evidence.

## Read the actual baseline

1. Read target-specific instructions, user changes, STANDARDS.md's previous full SHA and exceptions. Resolve the requested central checkout/ref from confirmed records; never infer it relative to the installed skill. If changing standards revision, review the old rules/exceptions and the new revision's impact before recording the new SHA.
2. Confirm central HEAD is `<sha>`, execution assets are clean and `templates/integration/contract.json` has `schema_version: 1`. Read central AGENTS.md and follow docs/adoption.md for first-adoption versus follow-up reading, review and status scope. Read only the relevant CLI/input sections of docs/template-skill-usage.md; T1–T6 design/history is not required for routine adoption. Obtain only missing facts, not repeated confirmation of authorized scope.
3. Read actual origin/default/current branch, single manifest domain, hacs/README support declarations, dependencies and current regression/CI paths. Keep existing minimum HA and its compatible Python/plugin environment separate from current tests. A latest-test request does not authorize raising the minimum. The inventory and schema identify conflicts and unanswered facts; do not choose convenient versions to silence them.

## Inspect and plan before writing

```text
python3 "<central>/scripts/manage_integration.py" inspect "<target>" --output "<work>/inventory.json"
python3 "<central>/scripts/manage_integration.py" plan "<target>" --mode adopt --input "<work>/input.json" --standards-ref <sha> --output "<work>/plan.json"
# Published immutable release only:
python3 "<central>/scripts/manage_integration.py" verify-release --repository eigger/hass-repo-standards --tag <release> --resolved-sha <sha> --output "<work>/release-verification.json"
python3 "<central>/scripts/manage_integration.py" plan "<target>" --mode adopt --input "<work>/input.json" --standards-ref <sha> --release-tag <release> --release-verification "<work>/release-verification.json" --output "<work>/release-plan.json"
```

Build sourced input from actual observations against `<central>/schemas/integration-input.schema.json`, using docs/template-skill-usage.md for field syntax. Inventory JSON is not directly interchangeable with that input. Read pending/conflicts, guards and all diffs. Existing bodies, implementation, fixtures, unique badges and CI conditions must remain. Missing boundaries or incompatible fixed content need an explicit migration plan; do not overwrite them to satisfy a template.

For review-only requests, stop at inspect/plan and report findings with missing evidence. If adoption/update is requested, apply within that scope after resolving conflicts:

```text
python3 "<central>/scripts/manage_integration.py" apply "<target>" --plan "<work>/plan.json" --journal "<work>/journal.json"
```

A nonzero CLI result stops dependent actions. Report and fix the actual cause, then regenerate a plan; do not suppress failure or hand-edit planned content. A partial transaction preserves journal and `.plan.json` anchor for documented `recover <target> --journal "<work>/journal.json"`. Recovery rejects later user edits. Follow central usage for guards/limits; never reset/clean the repository to recover.

Replan in adopt mode with unchanged input and revision to confirm no additional operations. Preserve unresolved implementation/validation pending even when the diff is empty. Do not add unsupported functionality merely because a checklist contains an item.

## Conditional contracts and verification

Read docs/home-assistant.md, docs/testing.md and docs/dependencies.md at the reviewed revision for actual implementation/real HA tests. Common README/test/CI format comes from the tools; existing device content, regressions and support are not replaced by new scaffold examples.

Select conditional docs from actual requirement/import observations: docs/bluetooth-documentation.md for blesession, docs/payload-documentation.md for imagespec and docs/documentation.md for bilingual managed areas. Keep real device conditions/actions/examples and production adapters; absent facts remain pending. Existing condition-specific documents are not deleted merely because a library condition changes. Do not send device commands or replace installed packages after payload validation.

```text
python3 "<central>/scripts/check_integration.py" "<target>" --check
```

Run affected regression tests and real HA domain loading/setup/platform/unload in exact minimum and current environments according to central testing rules. Use the actual installed payload versions/contract where applicable. Static structure/translation-key checks do not prove HA behavior, translation meaning or hardware operation. Use docs/adoption.md for affected verification scope, review selection and evidence links. Documentation-only follow-ups do not require rebuilding HA environments when behavior, dependencies and support declarations are unaffected. Missing tools/environments and skipped/failed checks stay explicit.

Append this review's evidence to ADOPTION_CHECKLIST.md and record/link the reviewed SHA and exceptions in STANDARDS.md using central templates, preserving earlier history without reusing its PASS. Follow the latest central adoption-status procedure for only the authorized target row; a local edit is not a remote update. Report changes, real commands/versions/results, target commit/CI, central status and remaining work. This skill does not grant installation, commit/push/PR, workflow dispatch, release or unrelated-repository authority.
