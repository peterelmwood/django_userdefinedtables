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
#   2. If the current version has a tag made by this workflow and its GitHub
#      release is not complete (missing, or missing an asset), finish it: build
#      from the tag, upload with --skip-existing, create the GitHub release if
#      missing, upload any missing assets. This completes a release whose
#      earlier run failed after the push, even if other merges have landed on
#      main since. A complete release is left alone, so a routine run does not
#      rebuild old artifacts or depend on the old version being reachable.
#   3. If main's head is not a release commit, something has merged since the
#      last release: compute the bump level from the release:* labels of every
#      PR whose commits are in v<current>..HEAD (found through the commits API,
#      so squash, merge, and rebase merges all count; before the first tagged
#      release the range starts at the commit that introduced the current
#      version), bump, commit, tag, push atomically (retrying from the fresh
#      origin/main if the push is rejected), then finish that release as in
#      step 2.
#
# Code from the repository (the build backend, setup.py, scripts/release.py)
# is always run with the PyPI and GitHub credentials stripped from the
# environment; only twine and gh see them. Any API failure aborts the run
# rather than being interpreted as "no labels": the run is idempotent, so the
# fix is simply to re-run it.
set -euo pipefail
# Without this, `set -e` is not inherited by $(...) subshells, so a failing
# gh call inside a command substitution would be silently ignored.
shopt -s inherit_errexit

: "${GH_REPO:?GH_REPO (owner/name) is required}"
: "${PR_NUMBER:?PR_NUMBER is required}"
# Overridable so the script can be exercised without a real build backend.
RELEASE_BUILD_CMD="${RELEASE_BUILD_CMD:-python -m build --sdist --wheel --outdir}"
MAX_PUSH_ATTEMPTS=3
DIST_NAME="django_userdefinedtables"
VERSION_FILE="userdefinedtables/__init__.py"

# Run repository code without the publishing credentials in its environment.
untrusted() { env -u TWINE_USERNAME -u TWINE_PASSWORD -u GH_TOKEN -u GITHUB_TOKEN "$@"; }

tag_exists() { git rev-parse -q --verify "refs/tags/v$1" >/dev/null; }
head_subject() { git log -1 --format=%s "${1:-HEAD}"; }
is_release_commit() { [ "$(head_subject "${2:-HEAD}")" = "Release v$1" ]; }

# Numbers of every PR associated with a commit in the given revision range.
# Any API failure makes this return non-zero, which aborts the run.
prs_in_range() {
  local sha found="" numbers
  for sha in $(git rev-list "$1"); do
    numbers=$(gh api "repos/${GH_REPO}/commits/${sha}/pulls" --jq '.[].number') || {
      echo "::error::Could not list pull requests for commit ${sha}" >&2
      return 1
    }
    found+="${numbers}"$'\n'
  done
  sort -un <<<"${found}" | sed '/^$/d'
}

# Comma-separated labels of the given PR numbers. Any lookup failure aborts.
labels_of_prs() {
  local n labels all=""
  for n in "$@"; do
    labels=$(gh pr view "$n" --json labels --jq '[.labels[].name] | join(",")') || {
      echo "::error::Could not read labels of pull request #${n}" >&2
      return 1
    }
    all+=",${labels}"
  done
  echo "${all#,}"
}

# Bump level implied by everything merged since the release of $1.
bump_level_since() {
  local since prs labels
  if tag_exists "$1"; then
    since="v$1"
  else
    # No tag to measure from (only before the first automated release):
    # count from the commit that introduced the current version string.
    since=$(git log --format=%H -S"__version__ = \"$1\"" -- "${VERSION_FILE}" | tail -n 1)
    echo "No tag v$1; counting merges since ${since} (the commit that set that version)" >&2
  fi
  prs=$(prs_in_range "${since}..HEAD") || return 1
  echo "PRs merged since v$1: $(tr '\n' ' ' <<<"${prs:-none}")" >&2
  # shellcheck disable=SC2086
  labels=$(labels_of_prs ${prs}) || return 1
  untrusted python scripts/release.py level --labels "${labels}"
}

# Expected artifact names for a version.
expected_assets() { echo "${DIST_NAME}-$1.tar.gz" "${DIST_NAME}-$1-py3-none-any.whl"; }

# A release is complete once its GitHub release exists with every expected
# asset: finish_release only creates the release after the PyPI upload has
# succeeded, so a full asset set implies the earlier steps are done too.
release_is_complete() {
  local have name
  have=$(gh release view "v$1" --json assets --jq '.assets[].name' 2>/dev/null) || return 1
  for name in $(expected_assets "$1"); do
    grep -qxF "${name}" <<<"${have}" || return 1
  done
}

# Build, upload, and create the GitHub release for an already-tagged version.
finish_release() {
  local version="$1" work
  work=$(mktemp -d)
  echo "Finishing release v${version}"
  git -c advice.detachedHead=false worktree add --quiet --detach "${work}/src" "v${version}"
  (cd "${work}/src" && untrusted ${RELEASE_BUILD_CMD} "${work}/dist")
  twine check "${work}"/dist/*
  twine upload --non-interactive --skip-existing "${work}"/dist/*
  if ! gh release view "v${version}" >/dev/null 2>&1; then
    (cd "${work}/src" && untrusted python scripts/release.py notes "${version}") > "${work}/notes.md"
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
  current=$(untrusted python scripts/release.py current)

  # 1. Tag a release commit that lost its tag.
  if is_release_commit "${current}" && ! tag_exists "${current}"; then
    echo "main's head is the release commit for v${current} but the tag is missing; tagging it"
    git tag -a "v${current}" -m "v${current}"
    git push origin "refs/tags/v${current}"
  fi

  # 2. Complete the current version if this workflow started it and it is
  #    not finished.
  if tag_exists "${current}" && is_release_commit "${current}" "v${current}"; then
    if release_is_complete "${current}"; then
      echo "Release v${current} is complete"
    else
      finish_release "${current}"
    fi
  fi

  # 3. Cut a new release if anything merged since.
  for attempt in $(seq 1 "${MAX_PUSH_ATTEMPTS}"); do
    git fetch --quiet origin main --tags
    git reset --quiet --hard origin/main
    current=$(untrusted python scripts/release.py current)
    if is_release_commit "${current}"; then
      echo "Nothing merged since v${current}; nothing to release"
      return 0
    fi
    level=$(bump_level_since "${current}") || {
      echo "::error::Could not determine the bump level; nothing was pushed. Re-run the workflow." >&2
      return 1
    }
    version=$(untrusted python scripts/release.py bump "${level}")
    echo "Attempt ${attempt}: ${current} -> ${version} (${level})"
    git add "${VERSION_FILE}" CHANGELOG.md
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
