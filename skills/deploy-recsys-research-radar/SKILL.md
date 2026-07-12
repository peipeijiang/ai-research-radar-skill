---
name: deploy-recsys-research-radar
description: Deploy, configure, verify, or repair a GitHub-hosted AI research radar for recommendation-systems papers. Use this skill whenever a user wants automated paper discovery, ArXiv/OpenAlex/DBLP ingestion, LLM scoring and PDF analysis, MinerU parsing, daily or weekly WeCom delivery, Git-backed knowledge, GBrain semantic search, GitHub code matching, citation expansion, or one-click paper feedback, even when they describe only part of that workflow.
---

# Deploy Recsys Research Radar

Build from the maintained template at `peipeijiang/arxiv-daily-researcher`. Keep
credentials in GitHub or Worker secrets; never write them into tracked files.

## Workflow

1. Confirm the target GitHub owner/repository, visibility, timezone, research
   topics, LLM provider, notification channel, and optional integrations.
2. Read [references/architecture.md](references/architecture.md) when explaining
   components, changing sources, or tailoring the research flow.
3. Read [references/configuration.md](references/configuration.md) before
   collecting keys or configuring GitHub Actions.
4. Create an independent deployment repository:

   ```bash
   bash scripts/bootstrap_repository.sh --target OWNER/REPO --visibility private
   ```

5. Edit `configs/config.json` in the deployed repository to reflect the user's
   research topics and scoring weights. Preserve its existing schema.
6. Configure GitHub Actions secrets interactively:

   ```bash
   python scripts/configure_repo.py --repo OWNER/REPO
   ```

   For automation, export the same secret names and add `--non-interactive`.
7. Optionally deploy one-click feedback after the user provides a fine-grained
   GitHub token limited to the deployment repository with Issues read/write:

   ```bash
   GITHUB_ISSUES_TOKEN=... bash scripts/deploy_feedback_worker.sh \
     --repo OWNER/REPO --checkout /path/to/deployed/repo
   ```

8. Trigger `daily-run.yml` with `gh workflow run`, watch it to completion, and
   inspect both the WeCom messages and committed `knowledge/` pages.
9. Run the deterministic audit:

   ```bash
   python scripts/verify_deployment.py --repo OWNER/REPO
   ```

10. Read [references/verification.md](references/verification.md) when a run
    fails, content is shallow, PDF access is missing, or feedback is not saved.

## Deployment Decisions

- Default to a private deployment repository unless the user explicitly wants
  public research output.
- Use OpenAI-compatible model settings; do not hard-code a provider. DeepSeek
  is a practical default for scoring and synthesis.
- Treat ArXiv, OpenAlex, and DBLP as discovery sources with different roles;
  deduplicate by normalized title before analysis.
- Resolve full text through lawful open-access sources: ArXiv, OpenAlex
  repositories, Unpaywall, CORE, then author or institutional pages.
- Use MinerU when configured and PyMuPDF as the local fallback.
- Keep one paper per WeCom message. Split oversized sections without ellipses or
  data loss.
- Keep GitHub Issue feedback as the fallback when the Worker is unavailable.
- Keep GBrain optional and local. Sync only after GitHub knowledge has been
  committed; respect PGLite's single-writer constraint.

## Completion Criteria

Do not declare success until all requested items pass:

- GitHub Actions workflow succeeds.
- At least one paper reaches `knowledge/papers/` with native Markdown analysis.
- WeCom receives an overview and individual paper cards.
- Deep-report and original-paper links open correctly.
- Feedback either records in one click or opens the safe Issue fallback.
- No secret appears in Git history, logs, reports, or the final response.
