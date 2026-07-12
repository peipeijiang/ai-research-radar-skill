#!/usr/bin/env python3
"""Audit workflows, secret names, knowledge output, and feedback health."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys


REQUIRED_SECRETS = {
    "CHEAP_LLM_API_KEY",
    "CHEAP_LLM_BASE_URL",
    "CHEAP_LLM_MODEL_NAME",
    "SMART_LLM_API_KEY",
    "SMART_LLM_BASE_URL",
    "SMART_LLM_MODEL_NAME",
    "WECHAT_WEBHOOK_URL",
}


def output(*args: str) -> str:
    return subprocess.check_output(args, text=True).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--feedback-url", default="")
    args = parser.parse_args()

    failures = []
    workflows = output("gh", "workflow", "list", "--repo", args.repo)
    for name in ("ArXiv Daily Research", "Weekly Research Synthesis"):
        ok = name in workflows
        print(f"[{'OK' if ok else 'FAIL'}] workflow: {name}")
        if not ok:
            failures.append(f"missing workflow {name}")

    secret_lines = output("gh", "secret", "list", "--repo", args.repo).splitlines()
    names = {line.split()[0] for line in secret_lines if line.split()}
    missing = sorted(REQUIRED_SECRETS - names)
    print(f"[{'OK' if not missing else 'FAIL'}] required secret names")
    if missing:
        failures.append("missing secrets: " + ", ".join(missing))

    try:
        content = output("gh", "api", f"repos/{args.repo}/contents/knowledge/index.jsonl")
        has_knowledge = bool(json.loads(content).get("sha"))
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        has_knowledge = False
    print(f"[{'OK' if has_knowledge else 'WARN'}] committed knowledge index")

    if args.feedback_url:
        try:
            if not shutil.which("curl"):
                raise RuntimeError("curl is required for the feedback health check")
            health = output(
                "curl", "-fsS", "--retry", "3", "--retry-all-errors",
                args.feedback_url.rstrip("/") + "/health",
            )
            healthy = json.loads(health).get("ok") is True
        except (subprocess.CalledProcessError, json.JSONDecodeError, RuntimeError):
            healthy = False
        print(f"[{'OK' if healthy else 'FAIL'}] feedback worker health")
        if not healthy:
            failures.append("feedback worker is unhealthy")

    if failures:
        print("\nDeployment audit failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("\nDeployment audit passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
