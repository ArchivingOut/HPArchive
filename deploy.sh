#!/usr/bin/env bash
# Usage: ./deploy.sh <github-username> [repo-name]   (default repo name: HPArchive)
set -e
USER_=${1:?usage: ./deploy.sh <github-username> [repo-name]}; REPO=${2:-HPArchive}
[ -d .git ] || { git init -b main; git add -A; git commit -m "Initial commit: HPArchive"; }
if command -v gh >/dev/null 2>&1; then
  gh repo create "$USER_/$REPO" --public --source=. --remote=origin --push
  gh api -X POST "repos/$USER_/$REPO/pages" -f build_type=workflow >/dev/null 2>&1 || true
  echo "Live soon at: https://$USER_.github.io/$REPO/  (watch the Actions tab)"
else
  echo "GitHub CLI not found. Create an empty public repo $USER_/$REPO on github.com, then run:"
  echo "  git remote add origin https://github.com/$USER_/$REPO.git && git push -u origin main"
  echo "Then: Settings > Pages > Source: GitHub Actions. Site: https://$USER_.github.io/$REPO/"
fi
