#!/usr/bin/env bash
set -euo pipefail

REPO=""
CHECKOUT=""
WORKER_NAME="recsys-research-feedback"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="$2"; shift 2 ;;
    --checkout) CHECKOUT="$2"; shift 2 ;;
    --worker-name) WORKER_NAME="$2"; shift 2 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

if [[ ! "$REPO" =~ ^[^/]+/[^/]+$ || ! -d "$CHECKOUT/feedback-worker" ]]; then
  echo "Usage: deploy_feedback_worker.sh --repo OWNER/REPO --checkout PATH [--worker-name NAME]" >&2
  exit 2
fi
for command in gh npx openssl; do
  command -v "$command" >/dev/null 2>&1 || { echo "Missing command: $command" >&2; exit 1; }
done
if [[ -z "${GITHUB_ISSUES_TOKEN:-}" ]]; then
  read -r -s -p "Fine-grained GitHub token (Issues read/write): " GITHUB_ISSUES_TOKEN
  printf '\n'
fi
if [[ -z "$GITHUB_ISSUES_TOKEN" ]]; then
  echo "Error: GitHub token is required." >&2
  exit 1
fi

pushd "$CHECKOUT/feedback-worker" >/dev/null
npx --yes wrangler whoami >/dev/null
deploy_output="$(npx --yes wrangler deploy --config wrangler.toml.example \
  --name "$WORKER_NAME" --var "GITHUB_REPOSITORY:$REPO" 2>&1)" || {
  printf '%s\n' "$deploy_output" >&2
  echo "Deployment failed. Run 'npx wrangler login' and register a workers.dev subdomain first." >&2
  exit 1
}
printf '%s\n' "$deploy_output"
worker_url="$(printf '%s\n' "$deploy_output" | grep -Eo 'https://[^[:space:]]+\.workers\.dev' | tail -n 1)"
if [[ -z "$worker_url" ]]; then
  echo "Error: could not determine workers.dev URL from deployment output." >&2
  exit 1
fi

signing_file="$(mktemp)"
trap 'rm -f "$signing_file"' EXIT
openssl rand -hex 32 > "$signing_file"
chmod 600 "$signing_file"
printf '%s' "$GITHUB_ISSUES_TOKEN" | npx --yes wrangler secret put GITHUB_TOKEN --name "$WORKER_NAME"
npx --yes wrangler secret put FEEDBACK_SIGNING_SECRET --name "$WORKER_NAME" < "$signing_file"
gh secret set FEEDBACK_SIGNING_SECRET --repo "$REPO" < "$signing_file"
gh secret set FEEDBACK_API_URL --repo "$REPO" --body "$worker_url"
popd >/dev/null

echo "One-click feedback deployed: $worker_url"
echo "Health check: $worker_url/health"
