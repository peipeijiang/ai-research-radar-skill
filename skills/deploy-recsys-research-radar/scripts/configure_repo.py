#!/usr/bin/env python3
"""Configure research-radar GitHub Actions secrets without exposing values."""

from __future__ import annotations

import argparse
import getpass
import os
import shutil
import subprocess
import sys


PROMPTS = (
    ("CHEAP_LLM_API_KEY", "LLM API key", True, True, ""),
    ("CHEAP_LLM_BASE_URL", "LLM base URL", True, False, "https://api.deepseek.com"),
    ("CHEAP_LLM_MODEL_NAME", "Scoring model", True, False, "deepseek-chat"),
    ("SMART_LLM_API_KEY", "Deep-analysis API key (Enter reuses scoring key)", True, True, ""),
    ("SMART_LLM_BASE_URL", "Deep-analysis base URL", True, False, "https://api.deepseek.com"),
    ("SMART_LLM_MODEL_NAME", "Deep-analysis model", True, False, "deepseek-chat"),
    ("OPENALEX_EMAIL", "OpenAlex contact email (recommended)", False, False, ""),
    ("WECHAT_WEBHOOK_URL", "WeCom robot webhook", True, True, ""),
    ("MINERU_API_KEY", "MinerU API token (optional)", False, True, ""),
    ("CORE_API_KEY", "CORE API key (optional)", False, True, ""),
    ("OPENALEX_API_KEY", "OpenAlex API key (optional)", False, True, ""),
    ("SEMANTIC_SCHOLAR_API_KEY", "Semantic Scholar API key (optional)", False, True, ""),
)


def run(*args: str, input_text: str | None = None) -> None:
    subprocess.run(args, input=input_text, text=True, check=True)


def read_value(name: str, label: str, required: bool, secret: bool, default: str, non_interactive: bool) -> str:
    value = os.getenv(name, "")
    if value:
        return value
    if non_interactive:
        if required:
            raise SystemExit(f"Missing required environment variable: {name}")
        return ""
    suffix = f" [{default}]" if default else ""
    reader = getpass.getpass if secret else input
    value = reader(f"{label}{suffix}: ").strip()
    return value or default


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, help="GitHub repository in OWNER/REPO form")
    parser.add_argument("--non-interactive", action="store_true")
    args = parser.parse_args()
    if "/" not in args.repo:
        parser.error("--repo must use OWNER/REPO format")
    if not shutil.which("gh"):
        raise SystemExit("GitHub CLI is required")
    run("gh", "auth", "status")

    values: dict[str, str] = {}
    for spec in PROMPTS:
        values[spec[0]] = read_value(*spec, args.non_interactive)
    if not values["SMART_LLM_API_KEY"]:
        values["SMART_LLM_API_KEY"] = values["CHEAP_LLM_API_KEY"]
    if not values["SMART_LLM_BASE_URL"]:
        values["SMART_LLM_BASE_URL"] = values["CHEAP_LLM_BASE_URL"]

    values.update(
        {
            "CHEAP_LLM_TEMPERATURE": os.getenv("CHEAP_LLM_TEMPERATURE", "0.1"),
            "SMART_LLM_TEMPERATURE": os.getenv("SMART_LLM_TEMPERATURE", "0.1"),
            "ENABLE_NOTIFICATIONS": "true",
        }
    )
    missing = [name for name, _, required, _, _ in PROMPTS if required and not values[name]]
    if missing:
        raise SystemExit("Missing required values: " + ", ".join(missing))

    configured = []
    for name, value in values.items():
        if not value:
            continue
        run("gh", "secret", "set", name, "--repo", args.repo, input_text=value)
        configured.append(name)
    print(f"Configured {len(configured)} GitHub Actions secrets for {args.repo}")
    print("Values were sent through stdin and were not written to disk.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
