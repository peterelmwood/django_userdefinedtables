#!/usr/bin/env bash
# Driver for .github/workflows/release.yml: finish any release that was started
# but not completed, then cut a new one if anything has merged since.
#
# Requires: git (on a full clone of main), gh (authenticated), python with
# scripts/release.py, build, twine (TWINE_USERNAME/TWINE_PASSWORD set).
# Environment: GH_REPO (owner/name), PR_NUMBER (the merged PR that triggered
# the run), optionally TWINE_REPOSITORY_URL.
#
# Every step is idempotent, so the whole script is safe to re-run:
#   1. If main's head is one of our "Release vX.Y.Z" commits and the tag is
#      missing (cannot normally happen: commit and tag are pushed atomically),
#      tag it.
#   2. If the current version has a tag made by this workflow, make sure it is
#      finished: build from the tag, upload with --skip-existing, create the
#      GitHub release if missing, upload any missing assets. This completes a
#      release whose earlier run failed after the push, even if other merges
#      have landed on main since.
#   3. If main's head is not a release commit, something has merged since the
#      last release: compute the bump level from the release:* labels of every
#      PR whose commits are in v<current>..HEAD (found through the commits API,
#      so squash, merge, and rebase merges all count), bump, commit, tag, push
#      atomically (retrying from the fresh origin/main if the push is
#      rejected), then finish that release as in step 2.
set -euo pipefail

: "${GH_REPO:?GH_REPO (owner/name) is required}"
: "${PR_NUMBER:?PR_NUMBER is required}"
# Overridable so the script can be exercised without a real build backend.
RELEASE_BUILD_CMD="${RELEASE_BUILD_CMD:-python -m build --sdist --wheel --outdir}"
MAX_PUSH_ATTEMPTS=3

tag_exists() { git rev-parse -q --verify "refs/tags/v$1" >/dev/null; }
head_subject() { git log -1 --format=%s "${1:-HEAD}"; }
is_release_commit() { [ "$(head_subject "${2:-HEAD}")" = "Release v$1" ]; }

# Numbers of every PR associated with a commit in the given revision range.
prs_in_range() {
  local sha
  for sha in $(git rev-list "$1"); do
    gh api "repos/${GH_REPO}/commits/${sha}/pulls" --jq '.[].number' 2>/dev/null || true
  done | sort -un
}

# Comma-separated labels of the given PR numbers.
labels_of_prs() {
  local n
  for n in "$@"; do
    gh pr view "$n" --json labels --jq '[.labels[].name] | join(",")'
  done | paste -sd, -
}

# Bump level implied by everything merged since the release of $1.
bump_level_since() {
  local prs
  if tag_exists "$1"; then
    prs=$(prs_in_range "v$1..HEAD")
  else
    # No tag to measure from (only before the first automated release): the
    # triggering PR is the only thing we know was merged.
    prs="$PR_NUMBER"
  fi
  echo "PRs merged since v$1: ${prs:-none}" >&2
  # shellcheck disable=SC2086
  python scripts/release.py level --labels "$(labels_of_prs $prs)"
}

# Build, upload, and create the GitHub release for an already-tagged version.
finish_release() {
  local version="$1" work
  work=$(mktemp -d)
  echo "Finishing release v${version}"
  git -c advice.detachedHead=false worktree add --quiet --detach "${work}/src" "v${version}"
  (cd "${work}/src" && ${RELEASE_BUILD_CMD} "${work}/dist")
  twine check "${work}"/dist/*
  twine upload --non-interactive --skip-existing "${work}"/dist/*
  if ! gh release view "v${version}" >/dev/null 2>&1; then
    (cd "${work}/src" && python scripts/release.py notes "${version}") > "${work}/notes.md"
    gh release create "v${version}" --title "v${version}" --notes-file "${work}/notes.md"
  fi
  local have file
  have=$(gh release view "v${version}" --json assets --jq '.assets[].name')
  for file in "${work}"/dist/*; do
    if ! grep -qxF "$(basename "${file}")" <<<"${have}"; then
      gh release upload "v${version}" "${file}"
    fi
  done
  git worktree remove --force "${work}/src"
  rm -rf "${work}"
}

main() {
  git fetch --quiet origin main --tags
  git reset --quiet --hard origin/main
  local current version level attempt
  current=$(python scripts/release.py current)

  # 1. Tag a release commit that lost its tag.
  if is_release_commit "${current}" && ! tag_exists "${current}"; then
    echo "main's head is the release commit for v${current} but the tag is missing; tagging it"
    git tag -a "v${current}" -m "v${current}"
    git push origin "refs/tags/v${current}"
  fi

  # 2. Complete the current version if this workflow started it.
  if tag_exists "${current}" && is_release_commit "${current}" "v${current}"; then
    finish_release "${current}"
  fi

  # 3. Cut a new release if anything merged since.
  for attempt in $(seq 1 "${MAX_PUSH_ATTEMPTS}"); do
    git fetch --quiet origin main --tags
    git reset --quiet --hard origin/main
    current=$(python scripts/release.py current)
    if is_release_commit "${current}"; then
      echo "Nothing merged since v${current}; nothing to release"
      return 0
    fi
    level=$(bump_level_since "${current}")
    version=$(python scripts/release.py bump "${level}")
    echo "Attempt ${attempt}: ${current} -> ${version} (${level})"
    git add userdefinedtables/__init__.py CHANGELOG.md
    git commit --quiet -m "Release v${version}" -m "Triggered by #${PR_NUMBER}."
    git tag -a "v${version}" -m "v${version}"
    if git push --atomic origin "HEAD:refs/heads/main" "refs/tags/v${version}"; then
      finish_release "${version}"
      return 0
    fi
    echo "Push rejected (main advanced?); retrying from the new origin/main"
    git tag -d "v${version}"
  done
  echo "::error::Could not push the release commit after ${MAX_PUSH_ATTEMPTS} attempts"
  return 1
}

main "$@"
