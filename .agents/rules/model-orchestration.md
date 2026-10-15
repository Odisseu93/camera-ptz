# Subagent Model Selection & Quota Efficiency

- **Flash / Flash-Lite (`Model: "flash"` / `"flash_lite"`)**:
  - Use for routine tasks: code formatting, writing tests, single-file edits, documentation updates, git tasks, and targeted research.
  - Minimizes latency and conserves API quota.
- **Pro / Inherit (`Model: "pro"` / `"inherit"`)**:
  - Reserve for complex architectural decisions, security audits, and multi-subsystem integrations.
- **Workflow Strategy**:
  - Break down larger features into small, well-scoped subtasks and delegate to `flash` subagents.
