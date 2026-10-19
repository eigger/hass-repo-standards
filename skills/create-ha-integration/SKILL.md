---
name: create-ha-integration
description: Create a new Home Assistant custom integration using the shared repository contract and templates. Use for an explicitly new integration or review of its generation plan; existing integration adoption belongs to adopt-ha-standards.
---

# Create a Home Assistant integration

Generate the common foundation with the central tools, then distinguish unfinished device implementation from validated behavior. Read [the workflow](references/workflow.md) for this task.

Use an independently confirmed central checkout and reviewed full SHA with contract version 1. Resolve these from the request or confirmed project records; do not derive the checkout from this installed skill's location. Read the central AGENTS.md and relevant rules at that SHA. The skill contains no copied templates or authority to change other repositories.

Use create only for a missing or empty target. Review-only requests stop after inspect/plan. Apply only within the requested scope; missing facts, conflicts and CLI failures remain explicit. Existing implementations belong to the adoption skill.
