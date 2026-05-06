---
description: Build the dependency + call graph + Mermaid diagrams only — no review subagents, no cost.
argument-hint: "[project-path]"
---

Run only the deterministic scripted phases (1, 1.5, 1.6, 2, 3, 3.5) of cartographer on `$1` (or current directory).

Use `bash run_pipeline.sh $1` (or `--readonly` if the user prefers `~/.cartographer/<hash>/` over polluting their repo).

Output what was produced — `project-map.json`, `pipelines.mmd`, `class_diagram.mmd`, `segments.mmd`, `endpoints.md`, etc. — and stop. Do NOT proceed to Phase 4 unless the user explicitly asks for a full audit (use `/cartographer:audit` for that).
