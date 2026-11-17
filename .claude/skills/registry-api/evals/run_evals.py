"""Run the registry-api evals with and without the skill, and record the results.

For every eval and every configuration (with_skill, without_skill):
  1. Copy services/registry-service into a fresh, git-initialised scratch repo.
  2. Run `claude -p` in that copy with the eval prompt. The with_skill run is
     told to read SKILL.md first. Tools are limited to an explicit allowlist.
  3. Run `uv run pytest` in the copy, independently of what the agent claimed.
  4. Save the agent's answer, timing, pytest output and the diff it produced.

Results go to .claude/skills/registry-api-workspace/iteration-N/. The real
registry-service is never modified.

Usage:
  python .claude/skills/registry-api/evals/run_evals.py
  python .claude/skills/registry-api/evals/run_evals.py --only 1,3 --jobs 4
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parent
SKILL_DIR = EVALS_DIR.parent
REPO_ROOT = SKILL_DIR.parents[2]
SERVICE_DIR = REPO_ROOT / "services" / "registry-service"
# Keep results out of .claude/: the harness denies agent writes under it, which breaks the runs.
WORKSPACE = REPO_ROOT / "registry-api-evals"
IGNORED = shutil.ignore_patterns(".venv", ".pytest_cache", "__pycache__")

# Only what an endpoint task needs. Shell access is limited to uv, git and pytest.
ALLOWED_TOOLS = ["Read", "Write", "Edit", "Glob", "Grep",
                 "Bash(uv run pytest:*)", "Bash(uv sync:*)", "Bash(git:*)", "Bash(ls:*)"]


def run(cmd, cwd, timeout):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)


def next_iteration():
    existing = [int(m.group(1)) for p in WORKSPACE.glob("iteration-*")
                if (m := re.fullmatch(r"iteration-(\d+)", p.name))]
    return max(existing, default=0) + 1


def build_prompt(task, config):
    if config == "with_skill":
        return (f"Before you start, read the project conventions in {SKILL_DIR / 'SKILL.md'} "
                f"and follow them.\n\nTask: {task}")
    return task


def total_tokens(usage):
    keys = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
    return sum(usage.get(k, 0) for k in keys)


def run_one(ev, config, iteration, timeout):
    run_dir = WORKSPACE / f"iteration-{iteration}" / f"eval-{ev['id']}" / config
    if run_dir.exists():
        shutil.rmtree(run_dir)
    repo = run_dir / "repo"
    shutil.copytree(SERVICE_DIR, repo, ignore=IGNORED)
    run_dir.joinpath("eval_metadata.json").write_text(json.dumps(
        {"eval_id": ev["id"], "config": config, "prompt": ev["prompt"]}, indent=2))

    # Baseline commit so the diff afterwards shows only what the agent changed.
    run(["git", "init", "-q"], repo, 60)
    run(["git", "add", "-A"], repo, 60)
    run(["git", "-c", "user.name=eval", "-c", "user.email=eval@local",
         "commit", "-q", "-m", "baseline"], repo, 60)

    start = time.time()
    try:
        proc = run(["claude", "-p", build_prompt(ev["prompt"], config),
                    "--output-format", "json",
                    "--allowedTools", *ALLOWED_TOOLS], repo, timeout)
        agent_out = proc.stdout
    except subprocess.TimeoutExpired:
        agent_out = ""
    wall = time.time() - start

    try:
        result = json.loads(agent_out)
    except json.JSONDecodeError:
        result = {"result": agent_out, "is_error": True}
    usage = result.get("usage", {})
    duration_ms = result.get("duration_ms", int(wall * 1000))
    timing = {"total_tokens": total_tokens(usage),
              "duration_ms": duration_ms,
              "total_duration_seconds": round(duration_ms / 1000, 1)}
    run_dir.joinpath("timing.json").write_text(json.dumps(timing, indent=2))
    run_dir.joinpath("response.md").write_text(str(result.get("result", "")))
    run_dir.joinpath("agent_raw.json").write_text(json.dumps(result, indent=2))

    pytest = run(["uv", "run", "pytest", "-q"], repo, 600)
    run_dir.joinpath("pytest.txt").write_text(pytest.stdout + pytest.stderr)

    run(["git", "add", "-A"], repo, 60)
    diff = run(["git", "diff", "--cached", "--no-color"], repo, 60).stdout
    run_dir.joinpath("changes.diff").write_text(diff)
    changed = run(["git", "diff", "--cached", "--name-only"], repo, 60).stdout.split()

    summary = {"eval_id": ev["id"], "config": config, "is_error": bool(result.get("is_error")),
               "pytest_passed": pytest.returncode == 0, "changed_files": changed, **timing}
    run_dir.joinpath("run.json").write_text(json.dumps(summary, indent=2))
    status = "PASS" if summary["pytest_passed"] else "FAIL"
    print(f"[{status}] eval-{ev['id']} {config}: {len(changed)} files changed, "
          f"{timing['total_duration_seconds']}s, {timing['total_tokens']} tokens", flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", help="comma-separated eval ids to run, e.g. 1,3")
    parser.add_argument("--iteration", type=int, help="iteration number (default: next free)")
    parser.add_argument("--configs", default="with_skill,without_skill")
    parser.add_argument("--jobs", type=int, default=2, help="parallel runs (default 2)")
    parser.add_argument("--timeout", type=int, default=900, help="seconds per agent run")
    args = parser.parse_args()

    evals = json.loads((EVALS_DIR / "evals.json").read_text())["evals"]
    if args.only:
        wanted = {int(x) for x in args.only.split(",")}
        evals = [e for e in evals if e["id"] in wanted]
    configs = args.configs.split(",")
    iteration = args.iteration or next_iteration()

    jobs = [(ev, cfg) for ev in evals for cfg in configs]
    print(f"iteration-{iteration}: {len(jobs)} runs, {args.jobs} at a time", flush=True)
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results = list(pool.map(lambda j: run_one(j[0], j[1], iteration, args.timeout), jobs))

    out = WORKSPACE / f"iteration-{iteration}" / "summary.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2))
    passed = sum(r["pytest_passed"] for r in results)
    print(f"\n{passed}/{len(results)} runs passed pytest. Summary: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
