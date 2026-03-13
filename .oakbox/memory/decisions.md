# Architectural Decisions Log

Append new decisions at the bottom of this file. Format:

```
## FEAT-<id>: <title> (<date>)
- **Decision:** <what was decided>
- **Rationale:** <why>
- **Alternatives considered:** <what else was discussed>
```

---

## FEAT-000: Project Scaffolding (2026-03-13)
- **Decision:** Use a file-based pipeline with markdown status tracking
- **Rationale:** Keeps everything in the repo, readable by both humans and AI agents, no external dependencies
- **Alternatives considered:** Database-backed state, external task management tools
