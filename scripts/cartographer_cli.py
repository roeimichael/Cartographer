#!/usr/bin/env python3
"""
Unified `cartographer` CLI — thin dispatcher over the per-phase scripts.

Usage:
    cartographer map      <project>   [--output DIR]   # Phase 1
    cartographer pipelines <map.json> [--output-dir D] # Phase 1.5
    cartographer openapi  <map.json>  [--output-dir D] # Phase 1.6 (extract)
    cartographer trace    <map.json>  [--output-dir D] # Phase 1.6 (per-endpoint)
    cartographer segment  <map.json>  [--output FILE]  # Phase 2
    cartographer waves    <segments>  --map M --output O   # Phase 3
    cartographer match    <wave_plan> --segments S --agents-dir A   # Phase 3.5
    cartographer synth    <reports/>  --map M --output O   # Phase 5
    cartographer apply    <backlog.md>  [--output FILE]   # Phase 7 (planner)
    cartographer finalize <pre|post>  --root R [--test-cmd "pytest"]
    cartographer status   <output_dir>                # progress heartbeat
    cartographer install  --integrations a,b [--execute --allow-skill-install]
    cartographer run      <project> [--readonly]     # full scripted pipeline (1 → 3.5)

Phases 4 and 7-dispatch run inside Claude Code, not from the CLI.
"""
from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

COMMANDS = {
    "map": "map_project",
    "pipelines": "trace_pipelines",
    "openapi": "extract_openapi",
    "trace": "trace_endpoints",
    "segment": "classify_segments",
    "waves": "plan_waves",
    "match": "match_specialists",
    "synth": "synthesize",
    "apply": "apply_backlog",
    "finalize": "finalize_fixes",
    "status": "cartographer_status",
    "install": "install_specialist",
}


def _help() -> int:
    print(__doc__, file=sys.stderr)
    return 0


def _run_pipeline(args: list[str]) -> int:
    """Wrap run_pipeline.sh — works on POSIX shells; on Windows users should
    invoke individual phases."""
    import subprocess
    sh = SCRIPT_DIR.parent / "run_pipeline.sh"
    if not sh.exists():
        print(f"run_pipeline.sh not found at {sh}", file=sys.stderr)
        return 1
    return subprocess.call(["bash", str(sh), *args])


def main() -> int:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        return _help()

    cmd, rest = sys.argv[1], sys.argv[2:]

    if cmd == "run":
        return _run_pipeline(rest)

    module = COMMANDS.get(cmd)
    if module is None:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        return _help() or 2

    # Re-exec the per-phase script. Each script uses argparse and reads sys.argv.
    sys.argv = [module, *rest]
    mod = __import__(module)
    if hasattr(mod, "main"):
        rc = mod.main()
        return rc if isinstance(rc, int) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
