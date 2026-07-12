# Architecture

## Data flow

```mermaid
flowchart LR
  A[ArXiv] --> D[Normalize and deduplicate]
  B[OpenAlex] --> D
  C[DBLP venues] --> D
  D --> E[Semantic Scholar enrichment]
  E --> F[LLM relevance scoring]
  F --> G[Open-access resolver]
  G --> H[MinerU or PyMuPDF]
  H --> I[Deep paper analysis]
  I --> J[Git-backed knowledge]
  I --> K[WeCom cards]
  J --> L[Weekly synthesis]
  J --> M[Local GBrain]
  K --> N[Like or ignore feedback]
  N --> F
```

## Component roles

| Component | Responsibility |
| --- | --- |
| ArXiv | Recent preprints, abstracts, canonical PDF access |
| OpenAlex | Broad topic discovery, metadata, citations, related works, OA locations |
| DBLP | Venue-focused discovery for RecSys, SIGIR, WSDM, KDD, WWW, and CIKM |
| Semantic Scholar | Abstract/TLDR backfill and citation metadata |
| GitHub matching | Verify official or author-linked implementation repositories |
| MinerU | Structured cloud PDF extraction; optional |
| PyMuPDF | Local PDF text fallback |
| Deep LLM | Scoring, translation, deep analysis, weekly synthesis |
| GitHub Actions | Daily and weekly scheduling, secrets, durable execution |
| WeCom | Overview plus one complete card per paper |
| Feedback Worker | Signed one-click feedback that creates auditable GitHub Issues |
| GBrain | Optional local hybrid and semantic search over committed knowledge |

## Durable state

- `knowledge/index.jsonl`: deduplicated machine-readable records.
- `knowledge/papers/`: mobile-friendly Markdown research reports.
- `knowledge/graph.json`: citation and related-work edges.
- `knowledge/feedback.json`: synchronized preferences.
- `knowledge/reports/weekly/`: weekly evidence-aware synthesis.

Treat Git as the durable source of truth. GitHub Actions caches are accelerators,
not authoritative storage.
