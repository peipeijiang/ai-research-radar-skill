---
name: deploy-ai-research-radar
description: Deploy, configure, verify, or repair a GitHub-hosted AI research radar for any academic field. Use this skill whenever a user wants automated paper discovery, custom research topics, ArXiv/OpenAlex/DBLP ingestion, lawful full-text recovery, evidence-labeled LLM analysis, MinerU parsing, daily or weekly WeCom delivery, Git-backed knowledge, GBrain semantic search, GitHub code matching, citation expansion, one-click paper feedback, or single-paper reanalysis, even when they describe only part of that workflow.
---

# Deploy AI Research Radar

Build from the maintained template at `peipeijiang/arxiv-daily-researcher`. Keep
credentials in GitHub or Worker secrets; never write them into tracked files.

## Workflow

1. Confirm the target GitHub owner/repository, visibility, timezone, research
   topics, LLM provider, notification channel, and optional integrations.
2. Read [references/architecture.md](references/architecture.md) when explaining
   components, changing sources, or tailoring the research flow.
   Read [references/source-selection.md](references/source-selection.md) before
   choosing discovery sources for a new academic field.
3. Read [references/configuration.md](references/configuration.md) before
   collecting keys or configuring GitHub Actions.
4. Read [references/fulltext-resolution.md](references/fulltext-resolution.md)
   whenever PDF recovery, evidence quality, or abstract fallback matters.
5. Create an independent deployment repository:

   ```bash
   bash scripts/bootstrap_repository.sh --target OWNER/REPO --visibility private
   ```

   Start with an empty knowledge index by default. Use `--keep-knowledge` only
   when intentionally cloning an existing research library.

6. Configure the user's research field before any run. Do not silently retain
   the template's recommendation-systems defaults:

   ```bash
   python scripts/configure_topics.py --checkout /path/to/deployed/repo
   ```

   Provide an ASCII `--field-slug` when the display name is non-Latin. The
   configured field name must appear in daily and weekly titles; the slug is
   stored in knowledge tags.
7. Configure GitHub Actions secrets interactively:

   ```bash
   python scripts/configure_repo.py --repo OWNER/REPO
   ```

   For automation, export the same secret names and add `--non-interactive`.
8. Optionally deploy one-click feedback after the user provides a fine-grained
   GitHub token limited to the deployment repository with Issues read/write:

   ```bash
   GITHUB_ISSUES_TOKEN=... bash scripts/deploy_feedback_worker.sh \
     --repo OWNER/REPO --checkout /path/to/deployed/repo
   ```

9. Trigger `daily-run.yml` with `gh workflow run`, watch it to completion, and
   inspect both the WeCom messages and committed `knowledge/` pages.
   Confirm the overview reports separate full-text and abstract-only counts.
   Every card without verified full text must show a warning-colored evidence
   limitation near its title.
10. Run the deterministic audit:

   ```bash
   python scripts/verify_deployment.py --repo OWNER/REPO --require-custom-topics
   ```

11. Read [references/verification.md](references/verification.md) when a run
    fails, content is shallow, PDF access is missing, or feedback is not saved.
12. When a lawful public PDF is found after abstract fallback, reanalyze only
    that paper instead of rerunning discovery:

   ```bash
   bash scripts/reanalyze_paper.sh \
     --repo OWNER/REPO \
     --paper-id 'STORED_PAPER_ID' \
     --pdf-url 'https://public.example/paper.pdf' \
     --provider author_repository \
     --watch
   ```

## Deployment Decisions

- Default to a private deployment repository unless the user explicitly wants
  public research output.
- Use OpenAI-compatible model settings; do not hard-code a provider. DeepSeek
  is a practical default for scoring and synthesis.
- Treat ArXiv, OpenAlex, and DBLP as discovery sources with different roles;
  deduplicate by normalized title before analysis.
- Select field-native sources instead of enabling DBLP universally. For banking
  and macro policy, prefer central-bank and multilateral-institution feeds,
  EconStor, and configured RePEc free working-paper series alongside ArXiv and
  OpenAlex.
- Resolve full text through lawful open-access sources: ArXiv, OpenAlex
  repositories, Unpaywall, OpenReview, CORE, then title-matched author or
  institutional pages and official GitHub repositories.
- Do not treat the presence of a publisher PDF URL as proof that it can be
  downloaded or parsed. Continue the open-access chain after access failure.
- Use MinerU when configured and PyMuPDF as the local fallback.
- Keep one paper per WeCom message. Split oversized sections without ellipses or
  data loss.
- Mark every non-full-text card prominently and distinguish paper limitations
  from limitations caused by missing evidence.
- Validate both HTTP status and platform response codes for webhook delivery;
  never report a failed notification as complete.
- Keep GitHub Issue feedback as the fallback when the Worker is unavailable.
- Keep GBrain optional and local. Sync only after GitHub knowledge has been
  committed; respect PGLite's single-writer constraint.

## Completion Criteria

Do not declare success until all requested items pass:

- GitHub Actions workflow succeeds.
- At least one paper reaches `knowledge/papers/` with native Markdown analysis.
- The research context, keywords, OpenAlex terms, and ArXiv categories match
  the user's stated field rather than the template defaults.
- The deployment begins with no template papers, and daily/weekly titles use
  the configured research field name.
- Missing-PDF resolution includes ArXiv title/DOI lookup and the lawful
  OpenAlex/Unpaywall/OpenReview/CORE/author-GitHub chain before abstract fallback.
- WeCom receives an overview and individual paper cards.
- The overview counts full-text versus abstract-only cards, and every
  abstract-only card contains a warning that results and limitations may be
  incomplete.
- Deep-report and original-paper links open correctly.
- `reanalyze-paper.yml` can replace one abstract analysis with verified
  full-text analysis without fetching a new daily batch.
- Webhook application errors and per-card failures are visible in Action logs.
- Feedback either records in one click or opens the safe Issue fallback.
- No secret appears in Git history, logs, reports, or the final response.
