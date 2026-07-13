# Missing-PDF Resolution

Use this ordered, lawful resolution chain for every qualified paper without a
working PDF URL.

## Resolution order

1. Keep a PDF already supplied by ArXiv, OpenAlex, DBLP enrichment, or another
   configured source.
2. Search ArXiv by DOI and normalized title. Accept an exact DOI match, or a
   high title similarity with author-surname overlap. Copy the ArXiv ID,
   abstract, categories, landing page, and PDF URL into the paper record.
3. Inspect OpenAlex open-access locations. Prefer a direct repository PDF.
4. When OpenAlex provides a repository landing page, fetch that public page and
   extract a directly linked PDF.
5. Query Unpaywall by DOI. Prefer `url_for_pdf`; otherwise inspect a repository
   landing page returned by Unpaywall.
6. Query CORE by DOI, or by title when DOI is unavailable, and use its download
   or source-full-text URL.
7. Record the provider, license/version when available, and URL in
   `fulltext_provenance`.
8. Download and parse with MinerU when configured; automatically fall back to
   PyMuPDF when MinerU is unavailable or fails.
9. If no PDF can be recovered or parsed, analyze only the abstract and set
   `_analysis_basis` to `abstract`. Explicitly state that datasets, metrics,
   baselines, losses, and implementation details absent from the abstract are
   unknown.

## Current boundary

The template follows author and institutional repository pages surfaced by
OpenAlex or Unpaywall. It does not perform unrestricted search-engine crawling
of arbitrary author homepages. Add a search provider only when the user accepts
its API, cost, privacy, and reproducibility implications.

Do not integrate Sci-Hub or other paywall-bypass sources. Research use does not
remove access-control or copyright constraints.

## Implementation contract

The deployed template must retain:

- `SearchAgent._resolve_missing_arxiv_versions`
- `ArxivSource.find_by_title`
- `SearchAgent._resolve_missing_open_access`
- `OpenAccessResolver.from_openalex_locations`
- `OpenAccessResolver.from_unpaywall`
- `OpenAccessResolver.from_core`
- `AnalysisAgent.deep_analyze` with explicit full-text/abstract basis
- MinerU-to-PyMuPDF fallback

The deployment audit checks these markers so a stale or incomplete template is
not reported as production-ready.
