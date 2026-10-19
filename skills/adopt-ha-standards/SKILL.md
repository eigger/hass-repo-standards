---
name: adopt-ha-standards
description: Inspect, review, adopt or update the shared repository standards in an existing Home Assistant custom integration while preserving its implementation and support range. Use for standards adoption or re-review; new integration generation belongs to create-ha-integration.
---

# Adopt shared Home Assistant standards

Use the central tools to inspect and plan changes to the existing integration. Read [the workflow](references/workflow.md) for this task.

Use an independently confirmed central checkout and reviewed full SHA with contract version 1. Resolve these from the request and STANDARDS.md, checking the actual recorded revision and exceptions. Do not infer the checkout from this installed skill's location. Read central AGENTS.md and relevant rules at the reviewed SHA.

Review-only requests stop after inspect/plan. Apply within the requested scope and preserve user changes, device code, README bodies, regression fixtures, CI extensions and the supported minimum. Do not install central agent instructions into the target. Missing facts, conflicts and CLI failures remain explicit; an existing standards request does not authorize a new feature or release.
