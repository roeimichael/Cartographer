# project-cartographer

[![CI](https://github.com/roeimichael/project-cartographer/actions/workflows/ci.yml/badge.svg)](https://github.com/roeimichael/project-cartographer/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-skill-8A2BE2)](https://claude.com/claude-code)

> Map, audit, and refactor a 1000-file codebase the way a senior engineer would — but with 17 specialist reviewers running in parallel.

A **Claude Code skill** that audits large codebases. Builds a dependency + call graph, traces pipelines from entry points, segments the repo by integration / domain, then dispatches per-segment specialist reviewers in waves. Synthesizes findings into a P0–P3 refactor backlog, optionally applies surgical fixes behind a confirmation gate.

```bash
# In Claude Code:
"audit this project"
"map out my codebase"
"find duplication across the repo"
```

The skill walks you through scope → questions → review → backlog → fixes, asking for confirmation at each gate.

## Quick install

```bash
pip install git+https://github.com/roeimichael/project-cartographer.git

# Or clone for development
git clone https://github.com/roeimichael/project-cartographer
cd project-cartographer
pip install -r requirements.txt
```

Then drop the folder into your Claude Code skills directory (location depends on your client) and trigger from inside Claude Code.

## See it in action

[`examples/stocksCorrelation/`](examples/stocksCorrelation/) — real outputs from a 134-file Python + React quant-trading project. Browse [`FINAL_REPORT.md`](examples/stocksCorrelation/FINAL_REPORT.md) for the polished deliverable, or [`outputs/`](examples/stocksCorrelation/outputs/) for raw artifacts.

## What it does — the short version

1. **Builds a multi-layer graph**: file imports + function call graph (Python AST-precise) + class hierarchy. TS path aliases resolved.
2. **Traces pipelines** from entry points (API handlers, `main()`, workers) through the call graph — produces one Mermaid flowchart per pipeline.
3. **Per-endpoint deep call trace + OpenAPI extraction** — each API endpoint gets a card with request/response schema, internal call tree, top external dependencies, and cross-endpoint reuse map.
4. **Detects functional segments** (per domain — `auth`, `watchlists`, `backtests`, ...).
5. **Matches a specialist reviewer** to each segment from a 17-strong library.
6. **Asks you what to focus on** before dispatching agents.
7. **Dispatches review subagents** in waves of ≤5.
8. **Synthesizes** duplicates, naming drift, centralization candidates, style outliers.
9. **Produces a final report** with a refactor backlog ranked P0–P3.
10. **Applies fixes** (opt-in, behind a confirmation gate) — fix subagents make surgical edits, report diffs, skip cleanly when the bug isn't where claimed.

The split between **scripts** (deterministic, ~30s for 300 files) and **subagents** (judgment, costs scale with segment count) keeps the agentic phase small. A 1000-file repo with 20 segments costs ~20 subagent invocations, not 1000 file reads.

See [CHANGELOG.md](CHANGELOG.md) for the full release history.

## Running scripted phases without Claude Code

Phases 1 → 3.5 are deterministic Python — no LLM, no API key, ~30s for 300 files. Use them standalone for CI or just to get the diagrams:

```bash
# Full scripted pipeline (Phases 1 → 3.5)
cartographer run /path/to/your/repo

# --readonly keeps outputs out of the target repo
cartographer run /path/to/your/repo --readonly

# Single phase
cartographer map /path/to/repo --output ./out
cartographer segment ./out/project-map.json --output ./out/segments.json
```

After Claude Code dispatches Phase 4 (review subagents) and reports land in `<output>/reports/`, synthesize:

```bash
cartographer synth <output>/reports/ --map <output>/project-map.json --output <output>/synthesis.json
```

## Triggering the skill in Claude Code

These phrasings all work:

- "Map out my project"
- "Audit this codebase"
- "Find duplication / inconsistencies across the repo"
- "Build a UML / dependency diagram for this project"
- "I have hundreds of files spread across {Supabase, Telegram, AI APIs, ...} — analyze them"

The skill **always asks before doing anything heavy**. Phase 0 collects scope + clarifying answers; Phase 4 dispatch is gated by an explicit cost confirmation; Phase 7 fixes are gated by a separate opt-in.

## Specialist agent library (17 roles)

| Specialist | Reviews |
|------------|---------|
| `auth-security-reviewer` | Auth flows, tokens, sessions, secrets |
| `supabase-reviewer` | Supabase client, RLS, edge functions, realtime, storage |
| `db-schema-reviewer` | Schema, migrations, indexes, raw SQL |
| `telegram-bot-reviewer` | Handlers, FSM, webhook security, rate limits |
| `ai-pipeline-reviewer` | Models, prompts, caching, token budgets, structured output |
| `backend-api-reviewer` | Endpoints, validation, response shapes |
| `data-pipeline-reviewer` | ETL/ML correctness, leakage, NaN/index, perf, reproducibility |
| `queue-worker-reviewer` | Idempotency, retries, DLQ, backpressure |
| `webhook-integration-reviewer` | Sig verification, replay, outbound timeouts |
| `frontend-ui-reviewer` | Hooks, props, state, render perf, a11y |
| `frontend-designer-reviewer` | Visual polish, motion, library recommendations |
| `mobile-reviewer` | iOS / Android / RN / Flutter — lifecycle, permissions, native bridge |
| `cli-tool-reviewer` | Flag naming, exit codes, stdout/stderr discipline, --json mode |
| `test-suite-reviewer` | Mock hygiene, flake risk, coverage shape |
| `file-storage-reviewer` | Upload safety, signed URLs, FS leaks |
| `realtime-streaming-reviewer` | Channels, broadcast scope, auth-per-message |
| `devops-config-reviewer` | Image hygiene, secrets, env drift, pins |
| `caching-reviewer` | TTL, invalidation, stampede, key collisions |
| `generalist-reviewer` | Fallback for everything else |

Each specialist is a markdown file under [`agents/`](agents/) with YAML frontmatter declaring triggers and priority. The matcher picks the highest-scoring match per segment. Override per-segment by editing `assigned_agent` in `wave_plan.json` before Phase 4.

To add a new specialist: drop a new `agents/<name>-reviewer.md` with frontmatter; the matcher auto-discovers it. See [`agents/AGENTS.md`](agents/AGENTS.md) for the catalog and [`docs/customization.md`](docs/customization.md) for the extension guide.

## Languages supported

- **Python** — precise, AST-based (full call graph + class hierarchy with bases/methods/fields)
- **JavaScript / TypeScript** — regex-based, best-effort (works for typical code; misses exotic syntax)
- **Go** — regex-based, best-effort

Tree-sitter for non-Python is on the roadmap. See [`docs/customization.md`](docs/customization.md) to add a language.

## Output structure

After a full run, the output dir contains:

```
project-map.json          full graph (files, edges, symbols, classes, calls, endpoints, integrations)
project-map.mmd           Mermaid: file-level dependency graph
class_diagram.mmd         Mermaid: classDiagram with bases, methods, fields
pipelines.json            entry → call tree per pipeline
pipelines.mmd             Mermaid: combined flowchart (top 10 pipelines)
pipelines/                one Mermaid flowchart per pipeline
openapi.json              real or synthetic OpenAPI spec
endpoints.json            per-endpoint trace summary
endpoints.md              endpoint index + cross-endpoint reuse hot-list
endpoints/                one detail card per endpoint
segments.json             segments with metadata
segments.mmd              Mermaid: segment overview
wave_plan.json            waves + specialist assignments
specialist_gaps.json      segments where no specialist matched well
scope.json                user's Phase 0 answers (goal, skip-paths, ...)
reports/                  per-segment specialist review reports
synthesis.json            cross-cutting findings + aggregated agent findings
synthesis.md              human-readable synthesis
FINAL_REPORT.md           consolidated deliverable
backlog.md                refactor backlog (Phase 7 input)
fix_reports/              per-fix diff reports (after Phase 7)
```

## Design notes

- **Why scripts + subagents?** Deterministic work (parsing, graph algos, fuzzy matching) is cheap as a script and unreliable as an LLM call. Judgment work (interpreting code, recommending refactors) is what subagents are for.
- **Why waves of 5?** Empirically, 30 agents at once thrashes context limits. Waves of 5 with strict schemas keep memory bounded and let later waves reference earlier results.
- **Why per-segment?** A subagent reviewing one well-defined segment produces a tight, structured report. A subagent told to "review the whole repo" produces vague prose.
- **Why explicit gates?** A 75-segment audit costs real money. The user should see segments + specialist assignments + cost estimate before any subagent fires. Single-shot opt-in is too coarse.
- **Why no embeddings?** Function-name fuzzy matching catches most cross-segment duplication. Embeddings shine for semantic body matching (different syntax, same intent) — that's a roadmap item, not core.

## License

MIT — see [LICENSE](LICENSE).

## Status

**v0.8** — release candidate. Roadmap:

- Skills.sh dynamic specialist install (currently: gaps surfaced, install is manual)
- Tree-sitter for JS/TS call resolution
- Semantic dedup via code-specialized embeddings (optional)
- Incremental re-run mode (re-analyze only changed segments)
- Phase 7 polish: branch creation, test running after fixes, unified diff summary
- More specialists: graphql-api, grpc, notebook, docs, cicd

## Contributing

Specialist roles, integration detectors, and language parsers are all designed for easy extension. See [`docs/customization.md`](docs/customization.md). PRs welcome.
