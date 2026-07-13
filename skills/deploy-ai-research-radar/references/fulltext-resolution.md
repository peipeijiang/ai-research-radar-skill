# Missing-PDF Resolution

Use this ordered, lawful resolution chain for every qualified paper without a
verified, parseable PDF. A non-empty publisher URL is only a candidate, not
proof of full-text access.

## Resolution order

1. Try a PDF already supplied by ArXiv, OpenAlex, DBLP enrichment, or another
   configured source. If download or parsing fails, continue this chain.
2. Search ArXiv by DOI and normalized title. Accept an exact DOI match, or a
   high title similarity with author-surname overlap. Copy the ArXiv ID,
   abstract, categories, landing page, and PDF URL into the paper record.
3. Inspect OpenAlex open-access locations. Prefer a direct repository PDF.
4. When OpenAlex provides a repository landing page, fetch that public page and
   extract a directly linked PDF.
5. Query Unpaywall by DOI. Prefer `url_for_pdf`; otherwise inspect a repository
   landing page returned by Unpaywall.
6. Query OpenReview by exact normalized title and accept its public submission
   PDF when the title matches.
7. Query CORE by DOI, or by title when DOI is unavailable, and use its download
   or source-full-text URL.
8. Inspect a title-matched implementation repository README for an explicitly
   linked paper PDF. Accept only a GitHub-hosted file from that repository and
   record `github_author_repository` provenance; reject paper collections.
9. Record the provider, license/version when available, and URL in
   `fulltext_provenance`.
10. Download and parse with MinerU when configured; automatically fall back to
   PyMuPDF when MinerU is unavailable or fails.
11. If no PDF can be recovered or parsed, analyze only the abstract and set
   `_analysis_basis` to `abstract`. Explicitly state that datasets, metrics,
   baselines, losses, and implementation details absent from the abstract are
   unknown.

## Evidence delivery

- Count `full_text` and `abstract` analyses separately in the WeCom overview.
- Put a warning-colored message directly below every abstract-only card title:
  the full text was not obtained, and experimental details, results, and
  limitations may be incomplete.
- Represent paper limitations and evidence limitations as separate readable
  labels. Never render a Python or JSON dictionary in the card.
- If a public PDF is found later, run `reanalyze-paper.yml` through
  `scripts/reanalyze_paper.sh`; require the replacement analysis basis to be
  `full_text` before committing knowledge.

## Current boundary

The template follows author and institutional repository pages surfaced by
OpenAlex or Unpaywall, exact-title OpenReview records, and paper PDFs explicitly
linked by title-matched GitHub repositories. It does not perform unrestricted
search-engine crawling of arbitrary author homepages. Add a search provider
only when the user accepts its API, cost, privacy, and reproducibility
implications.

Do not integrate Sci-Hub or other paywall-bypass sources. Research use does not
remove access-control or copyright constraints.

## Implementation contract

The deployed template must retain:

- `SearchAgent._resolve_missing_arxiv_versions`
- `ArxivSource.find_by_title`
- `SearchAgent._resolve_missing_open_access`
- `OpenAccessResolver.from_openalex_locations`
- `OpenAccessResolver.from_unpaywall`
- `OpenAccessResolver.from_openreview`
- `OpenAccessResolver.from_core`
- `GitHubCodeEnricher.find_paper_pdf`
- `AnalysisAgent.deep_analyze` with explicit full-text/abstract basis
- MinerU-to-PyMuPDF fallback
- `reanalyze-paper.yml` and `scripts/reanalyze_paper.py`
- warning-colored abstract-only WeCom cards and basis counts in the overview

The deployment audit checks these markers so a stale or incomplete template is
not reported as production-ready.
