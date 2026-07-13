#!/usr/bin/env bash
set -euo pipefail

REPO=""
PAPER_ID=""
PDF_URL=""
PROVIDER="manual_verified_open_access"
WATCH=false

usage() {
  cat <<'EOF'
Usage: reanalyze_paper.sh --repo OWNER/REPO --paper-id ID --pdf-url HTTPS_URL [options]

Options:
  --provider LABEL   Full-text provenance label
  --watch            Wait for the GitHub Actions run and return its status
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="$2"; shift 2 ;;
    --paper-id) PAPER_ID="$2"; shift 2 ;;
    --pdf-url) PDF_URL="$2"; shift 2 ;;
    --provider) PROVIDER="$2"; shift 2 ;;
    --watch) WATCH=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ ! "$REPO" =~ ^[^/]+/[^/]+$ ]]; then
  echo "Error: --repo must use OWNER/REPO format." >&2
  exit 2
fi
if [[ -z "$PAPER_ID" || ! "$PDF_URL" =~ ^https:// ]]; then
  echo "Error: --paper-id and a public HTTPS --pdf-url are required." >&2
  exit 2
fi
command -v gh >/dev/null 2>&1 || { echo "Error: GitHub CLI is required." >&2; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "Error: authenticate with gh first." >&2; exit 1; }

run_url="$(gh workflow run reanalyze-paper.yml --repo "$REPO" \
  -f "paper_id=$PAPER_ID" \
  -f "pdf_url=$PDF_URL" \
  -f "provider=$PROVIDER")"
printf 'Triggered: %s\n' "$run_url"

if [[ "$WATCH" == true ]]; then
  run_id="${run_url##*/}"
  gh run watch "$run_id" --repo "$REPO" --exit-status
fi
