#!/usr/bin/env python3
"""Replace template topics with a user-defined academic research profile."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import json5
except ImportError as exc:
    raise SystemExit("Install the template dependencies first: pip install json5") from exc


def split_values(value: str) -> list[str]:
    return [item.strip() for item in value.replace("，", ",").split(",") if item.strip()]


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def ask(current: str, prompt: str, required: bool = True) -> str:
    value = current.strip() if current else input(f"{prompt}: ").strip()
    if required and not value:
        raise SystemExit(f"A value is required for: {prompt}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Configure arbitrary research topics in configs/config.json"
    )
    parser.add_argument("--checkout", type=Path, required=True)
    parser.add_argument("--field-name", default="")
    parser.add_argument("--field-slug", default="", help="ASCII knowledge tag")
    parser.add_argument("--keywords", default="", help="Comma-separated relevance keywords")
    parser.add_argument("--arxiv-categories", default="", help="Comma-separated ArXiv categories")
    parser.add_argument("--openalex-terms", default="", help="Defaults to keywords")
    parser.add_argument("--dblp-venues", default="", help="Optional comma-separated DBLP venues")
    parser.add_argument("--dblp-title-terms", default="", help="Defaults to keywords")
    parser.add_argument("--research-context", default="")
    args = parser.parse_args()

    path = args.checkout.resolve() / "configs" / "config.json"
    if not path.exists():
        raise SystemExit(f"Template config not found: {path}")

    field_name = ask(args.field_name, "Research field name")
    keywords_text = ask(args.keywords, "Keywords, comma-separated")
    categories_text = ask(args.arxiv_categories, "ArXiv categories, comma-separated")
    keywords = split_values(keywords_text)
    categories = split_values(categories_text)
    if not keywords or not categories:
        raise SystemExit("At least one keyword and one ArXiv category are required")

    openalex_terms = split_values(args.openalex_terms) or keywords
    field_slug = slugify(args.field_slug) or slugify(field_name)
    if not field_slug:
        field_slug = slugify(openalex_terms[0] if openalex_terms else keywords[0])
    field_slug = field_slug or "academic-research"
    dblp_venues = split_values(args.dblp_venues)
    dblp_terms = split_values(args.dblp_title_terms) or keywords
    context = args.research_context.strip() or (
        f"Continuously track current academic research in {field_name}. "
        f"Prioritize methodological novelty, reliable experiments, public code, "
        f"reproducible details, and work related to: {', '.join(keywords)}."
    )

    data = json5.loads(path.read_text(encoding="utf-8"))
    data.setdefault("data_sources", {}).setdefault("openalex", {})["search_terms"] = openalex_terms
    dblp = data["data_sources"].setdefault("dblp", {})
    dblp["venues"] = dblp_venues
    dblp["title_terms"] = dblp_terms
    enabled = data["data_sources"].setdefault("enabled", ["arxiv", "openalex"])
    enabled = [source for source in enabled if source != "dblp"]
    if dblp_venues:
        enabled.append("dblp")
    data["data_sources"]["enabled"] = list(dict.fromkeys(enabled))
    data.setdefault("target_domains", {})["domains"] = categories
    keyword_config = data.setdefault("keywords", {})
    keyword_config.setdefault("primary_keywords", {})["keywords"] = keywords
    keyword_config["research_context"] = context
    data["research_profile"] = {
        "field_name": field_name,
        "field_slug": field_slug,
        "configured_at": datetime.now(timezone.utc).isoformat(),
        "configured_by": "deploy-ai-research-radar",
    }

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Configured research field: {field_name}")
    print(f"Knowledge field tag: {field_slug}")
    print(f"Keywords: {len(keywords)} | ArXiv categories: {len(categories)}")
    print(f"OpenAlex terms: {len(openalex_terms)} | DBLP venues: {len(dblp_venues)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
