# Configuration

## Required GitHub secrets

| Secret | Purpose | Typical value |
| --- | --- | --- |
| `CHEAP_LLM_API_KEY` | Paper scoring and lightweight tasks | Provider API key |
| `CHEAP_LLM_BASE_URL` | OpenAI-compatible endpoint | `https://api.deepseek.com` |
| `CHEAP_LLM_MODEL_NAME` | Scoring model | `deepseek-chat` |
| `SMART_LLM_API_KEY` | Deep analysis and synthesis | Provider API key |
| `SMART_LLM_BASE_URL` | OpenAI-compatible endpoint | Same provider endpoint |
| `SMART_LLM_MODEL_NAME` | Analysis model | `deepseek-chat` |
| `WECHAT_WEBHOOK_URL` | WeCom group robot delivery | Robot webhook URL |

The configuration script also sets temperatures and enables notifications.

`OPENALEX_EMAIL` is strongly recommended for polite-pool identification but is
not required for a first run.

## Optional secrets

| Secret | Enables |
| --- | --- |
| `MINERU_API_KEY` | MinerU structured PDF extraction |
| `CORE_API_KEY` | CORE open-access full-text lookup |
| `OPENALEX_API_KEY` | Higher OpenAlex limits when available |
| `SEMANTIC_SCHOLAR_API_KEY` | Higher Semantic Scholar limits |
| `FEEDBACK_API_URL` | One-click feedback endpoint |
| `FEEDBACK_SIGNING_SECRET` | HMAC signatures for feedback URLs |

## Research topics

Edit the deployed repository's `configs/config.json`. Preserve the schema and
adjust:

- primary keywords and weights;
- supporting and exclusion keywords;
- score threshold;
- lookback period and source limits;
- target ArXiv categories and DBLP venues;
- notification Top N.

Start narrow enough that a human can read the daily output. Expand after
reviewing one week of false positives and missed papers.

## Security

- Enter secrets through `getpass`, `gh secret set`, or `wrangler secret put`.
- Use a fine-grained GitHub token for the feedback Worker. Grant only the target
  repository and Issues read/write.
- Rotate any credential pasted into chat, terminal history, or screenshots.
- Never commit `.env`, `wrangler.toml` with sensitive values, or token files.
- Keep the HMAC signing secret identical in Worker and GitHub Actions.
