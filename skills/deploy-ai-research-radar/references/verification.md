# Verification and Troubleshooting

## First-run audit

1. Run `python scripts/verify_deployment.py --repo OWNER/REPO`.
2. Trigger `daily-run.yml` manually with a seven-day search window.
3. Watch the run with `gh run watch` and inspect failed step logs if needed.
4. Confirm `knowledge/index.jsonl` and at least one paper Markdown page changed.
5. Confirm WeCom received one overview plus individual complete paper cards.
   The overview must count full-text and abstract-only analyses separately.
   Every abstract-only card must show a warning near the title.
6. Open a deep report on mobile and verify native Markdown sections render.
7. Click feedback once and confirm a `paper-feedback` Issue appears.
8. Run a local GBrain exact-title search after synchronization.
9. For an abstract-only paper with a newly found public PDF, run
   `scripts/reanalyze_paper.sh --watch` and confirm its basis becomes
   `full_text` without a new discovery run.

## Common failures

| Symptom | Check |
| --- | --- |
| No papers | Date window, topic keywords, ArXiv categories, OpenAlex email |
| Shallow summaries | PDF URL/provenance, MinerU token, PyMuPDF fallback, analysis basis |
| Publisher PDF exists but analysis is abstract-only | Treat the URL as unverified; continue OpenReview, CORE, and author-GitHub recovery |
| Fabricated metrics | Ensure full PDF text is supplied and prompts prohibit unsupported facts |
| Missing evidence warning | Check `_analysis_basis` and the WeCom abstract-only warning marker |
| WeCom truncation | One card per paper, UTF-8 byte budget, continuation cards |
| Action says notification completed but nothing arrived | Check webhook JSON `errcode`, per-card error logs, and network timeout diagnostics |
| Feedback opens Issue form | `FEEDBACK_API_URL` and matching signing secret are absent or stale |
| Feedback Worker 403 | HMAC secrets differ; rotate and update both stores |
| Feedback Worker 502 | GitHub token lacks Issues read/write or repository access |
| GBrain sync hangs | Stop active `gbrain serve`; PGLite permits one writer |
| Duplicate papers | Normalize titles across sources before persistence |
| Wrong GitHub code | Reject surveys/awesome lists without paper or author authority evidence |

Never fix a failed run by printing credentials. Inspect secret names, HTTP
status codes, and provider diagnostics instead.
