#!/usr/bin/env bash
set -euo pipefail

SOURCE="peipeijiang/arxiv-daily-researcher"
TARGET=""
VISIBILITY="private"
DESTINATION=""
KEEP_KNOWLEDGE=false

usage() {
  cat <<'EOF'
Usage: bootstrap_repository.sh --target OWNER/REPO [options]

Options:
  --source OWNER/REPO       Template repository
  --visibility private|public
  --destination PATH        Local checkout path (default: ./REPO)
  --keep-knowledge          Preserve template knowledge instead of starting empty
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --source) SOURCE="$2"; shift 2 ;;
    --target) TARGET="$2"; shift 2 ;;
    --visibility) VISIBILITY="$2"; shift 2 ;;
    --destination) DESTINATION="$2"; shift 2 ;;
    --keep-knowledge) KEEP_KNOWLEDGE=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ ! "$TARGET" =~ ^[^/]+/[^/]+$ ]]; then
  echo "Error: --target must use OWNER/REPO format." >&2
  exit 2
fi
if [[ "$VISIBILITY" != "private" && "$VISIBILITY" != "public" ]]; then
  echo "Error: --visibility must be private or public." >&2
  exit 2
fi
for command in git gh; do
  command -v "$command" >/dev/null 2>&1 || {
    echo "Error: required command '$command' is unavailable." >&2
    exit 1
  }
done
gh auth status >/dev/null 2>&1 || {
  echo "Error: authenticate first with 'gh auth login'." >&2
  exit 1
}
if gh repo view "$TARGET" >/dev/null 2>&1; then
  echo "Error: GitHub repository already exists: $TARGET" >&2
  exit 1
fi

repo_name="${TARGET#*/}"
DESTINATION="${DESTINATION:-$PWD/$repo_name}"
if [[ -e "$DESTINATION" ]]; then
  echo "Error: destination already exists: $DESTINATION" >&2
  exit 1
fi

git clone --depth 1 "https://github.com/$SOURCE.git" "$DESTINATION"
rm -rf "$DESTINATION/.git"
if [[ "$KEEP_KNOWLEDGE" != true ]]; then
  rm -rf "$DESTINATION/knowledge/papers" "$DESTINATION/knowledge/reports"
  mkdir -p "$DESTINATION/knowledge/papers"
  : > "$DESTINATION/knowledge/index.jsonl"
  printf '{\n  "nodes": {},\n  "edges": []\n}\n' > "$DESTINATION/knowledge/graph.json"
  printf '{\n  "liked": [],\n  "ignored": []\n}\n' > "$DESTINATION/knowledge/feedback.json"
fi
git -C "$DESTINATION" init -b main
git -C "$DESTINATION" add .
git -C "$DESTINATION" -c user.name="Research Radar Bootstrap" \
  -c user.email="research-radar@users.noreply.github.com" \
  commit -m "chore: initialize AI research radar"
gh repo create "$TARGET" "--$VISIBILITY" --source "$DESTINATION" --remote origin --push

echo "Created: https://github.com/$TARGET"
echo "Checkout: $DESTINATION"
