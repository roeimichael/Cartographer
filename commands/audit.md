---
description: Audit a codebase end-to-end — graph build, segment, review, synthesize, optionally fix.
argument-hint: "[project-path]"
---

Run the cartographer audit on `$1` (or the current working directory if no path given).

Invoke the cartographer skill (`skills/cartographer/SKILL.md`) and walk through Phase 0 (scope + clarifying questions) → Phase 1–3.5 (scripted) → Phase 4 (review subagents in waves of ≤5) → Phase 5–6 (synthesis + final report) → Phase 7 (fix application, opt-in).

Pause at each gate (A: segments, B: specialists + cost, D: post-review triage, Phase 7 opt-in). Do not skip gates.
