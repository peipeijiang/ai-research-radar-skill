#!/usr/bin/env python3
"""Audit workflows, secret names, knowledge output, and feedback health."""

from __future__ import annotations

import argparse
import base64
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

FEATURE_MARKERS = {
    "src/sources/search_agent.py": (
        "_resolve_missing_arxiv_versions",
        "_resolve_missing_open_access",
    ),
    "src/sources/arxiv_source.py": ("find_by_title",),
    "src/enrichers/open_access.py": (
        "from_openalex_locations",
        "from_unpaywall",
        "from_openreview",
        "from_core",
    ),
    "src/enrichers/github_code.py": (
        "find_paper_pdf",
        "github_author_repository",
    ),
    "src/sources/institutional_rss_source.py": (
        "InstitutionalRssSource",
        "official_institution_rss",
    ),
    "src/sources/worldbank_source.py": (
        "WorldBankSource",
        "worldbank_documents_api",
    ),
    "src/sources/repec_series_source.py": (
        "class RepecSeriesSource",
        "freedownload",
        "current_year_links",
        "repec_free_fulltext",
    ),
    "src/agents/analysis_agent.py": (
        'analysis_basis = "full_text" if pdf_text else "abstract"',
        "PyMuPDF",
    ),
    "src/notifications/notifier.py": (
        "未获取论文正文",
        "RESEARCH_FIELD_NAME",
        'response_data.get("errcode"',
        "return delivery_succeeded",
    ),
    "scripts/reanalyze_paper.py": (
        "fallback_to_abstract=False",
        'analysis.get("_analysis_basis") != "full_text"',
    ),
    ".github/workflows/reanalyze-paper.yml": (
        "name: Reanalyze One Paper",
    ),
}


def output(*args: str) -> str:
    return subprocess.check_output(args, text=True).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--feedback-url", default="")
    parser.add_argument("--require-custom-topics", action="store_true")
    args = parser.parse_args()

    failures = []
    workflows = output("gh", "workflow", "list", "--repo", args.repo)
    for name in (
        "ArXiv Daily Research",
        "Weekly Research Synthesis",
        "Reanalyze One Paper",
    ):
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

    missing_features = []
    for path, markers in FEATURE_MARKERS.items():
        try:
            payload = json.loads(output("gh", "api", f"repos/{args.repo}/contents/{path}"))
            source = base64.b64decode(payload["content"]).decode("utf-8")
            missing_features.extend(
                f"{path}:{marker}" for marker in markers if marker not in source
            )
        except (subprocess.CalledProcessError, KeyError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
            missing_features.append(path)
    print(f"[{'OK' if not missing_features else 'FAIL'}] evidence and delivery contract")
    if missing_features:
        failures.append("missing full-text features: " + ", ".join(missing_features))

    if args.require_custom_topics:
        try:
            payload = json.loads(
                output("gh", "api", f"repos/{args.repo}/contents/configs/config.json")
            )
            config_text = base64.b64decode(payload["content"]).decode("utf-8")
            profile = json.loads(config_text).get("research_profile") or {}
            custom_topics = (
                profile.get("configured_by") == "deploy-ai-research-radar"
                and bool(profile.get("field_name"))
                and bool(profile.get("field_slug"))
            )
        except (subprocess.CalledProcessError, KeyError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
            custom_topics = False
        print(f"[{'OK' if custom_topics else 'FAIL'}] user-defined research profile")
        if not custom_topics:
            failures.append("research topics still use an unconfirmed template profile")

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
