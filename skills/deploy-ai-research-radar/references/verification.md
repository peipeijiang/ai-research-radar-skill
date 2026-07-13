# Verification and Troubleshooting

## First-run audit

1. Run `python scripts/verify_deployment.py --repo OWNER/REPO`.
2. Trigger `daily-run.yml` manually with a seven-day search window.
3. Watch the run with `gh run watch` and inspect failed step logs if needed.
4. Confirm `knowledge/index.jsonl` and at least one paper Markdown page changed.
5. Confirm WeCom received one overview plus individual complete paper cards.
6. Open a deep report on mobile and verify native Markdown sections render.
7. Click feedback once and confirm a `paper-feedback` Issue appears.
8. Run a local GBrain exact-title search after synchronization.

## Common failures

| Symptom | Check |
| --- | --- |
| No papers | Date window, topic keywords, ArXiv categories, OpenAlex email |
| Shallow summaries | PDF URL/provenance, MinerU token, PyMuPDF fallback, analysis basis |
| Fabricated metrics | Ensure full PDF text is supplied and prompts prohibit unsupported facts |
| WeCom truncation | One card per paper, UTF-8 byte budget, continuation cards |
| Feedback opens Issue form | `FEEDBACK_API_URL` and matching signing secret are absent or stale |
| Feedback Worker 403 | HMAC secrets differ; rotate and update both stores |
| Feedback Worker 502 | GitHub token lacks Issues read/write or repository access |
| GBrain sync hangs | Stop active `gbrain serve`; PGLite permits one writer |
| Duplicate papers | Normalize titles across sources before persistence |
| Wrong GitHub code | Reject surveys/awesome lists without paper or author authority evidence |

Never fix a failed run by printing credentials. Inspect secret names, HTTP
status codes, and provider diagnostics instead.
