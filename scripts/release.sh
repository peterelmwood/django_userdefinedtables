#!/usr/bin/env bash
# Driver for .github/workflows/release.yml: finish any release that was started
# but not completed, then cut a new one if anything has merged since.
#
# Requires: git (on a full clone of main), gh (authenticated), python with
# scripts/release.py, build, twine (TWINE_USERNAME/TWINE_PASSWORD set).
# Environment: GH_REPO (owner/name), PR_NUMBER (the merged PR that triggered
# the run), PR_LABELS_JSON (that PR's labels as they were in the merge event,
# a JSON array of names), PR_MERGE_SHA (its merge commit), optionally
# TWINE_REPOSITORY_URL.
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
#      PR merged into main whose merge commit is in v<current>..HEAD (a
#      GraphQL query of merged PRs ordered by last update, newest first,
#      paginated only until a PR last updated before the range start appears,
#      then filtered by git ancestry, so squash, merge, and rebase merges all
#      count; before the first tagged release the range starts at the commit
#      that introduced the current version), bump,
#      commit, tag, push atomically (retrying from the fresh origin/main if the
#      push is rejected), then finish that release as in step 2. Each PR's
#      labels are taken as they were at its merge time, reconstructed from
#      its label timeline in the same query, so relabelling a PR after the
#      merge changes nothing; the triggering PR's labels from the merge event
#      (PR_LABELS_JSON) are included as well when its merge commit
#      (PR_MERGE_SHA) lies in the range.
#
# A "release commit" is recognised by three things together: the subject
# "Release vX.Y.Z" where X.Y.Z is the version in the version file, the
# committer identity this script uses, and the commit touching the version
# file. An ordinary commit that merely reuses the subject does not qualify.
#
# Code from the repository (the build backend, setup.py, scripts/release.py)
# is always run with the PyPI and GitHub credentials stripped from the
# environment; only twine, gh, and this script's own git fetch/push see them.
# The checkout is made with persist-credentials disabled, so the token is
# never written to .git/config; git is authenticated per command instead.
# Any API failure aborts the run rather than being interpreted as "no labels":
# the run is idempotent, so the fix is simply to re-run it.
set -euo pipefail
# Without this, `set -e` is not inherited by $(...) subshells, so a failing
# gh call inside a command substitution would be silently ignored.
shopt -s inherit_errexit

: "${GH_REPO:?GH_REPO (owner/name) is required}"
: "${PR_NUMBER:?PR_NUMBER is required}"
PR_LABELS_JSON="${PR_LABELS_JSON:-[]}"
PR_MERGE_SHA="${PR_MERGE_SHA:-}"
# Merged PRs are listed newest-updated first, 100 per page, until a PR last
# updated before the range start appears (every PR merged in the range was
# updated after it, so nothing in the range can follow). If that many pages
# go by without one, the run aborts rather than guess.
PR_QUERY_PAGE_SIZE=100
PR_QUERY_MAX_PAGES=10
# Overridable so the script can be exercised without a real build backend.
RELEASE_BUILD_CMD="${RELEASE_BUILD_CMD:-python -m build --sdist --wheel --outdir}"
MAX_PUSH_ATTEMPTS=3
DIST_NAME="django_userdefinedtables"
VERSION_FILE="userdefinedtables/__init__.py"
RELEASE_BOT_NAME="${RELEASE_BOT_NAME:-github-actions[bot]}"
RELEASE_BOT_EMAIL="${RELEASE_BOT_EMAIL:-41898282+github-actions[bot]@users.noreply.github.com}"

# Run repository code without the publishing credentials in its environment.
untrusted() { env -u TWINE_USERNAME -u TWINE_PASSWORD -u GH_TOKEN -u GITHUB_TOKEN "$@"; }

# git with the GitHub token supplied for this one command only (the same
# header actions/checkout would have persisted), never written to config.
git_auth() {
  local header
  header="AUTHORIZATION: basic $(printf 'x-access-token:%s' "${GH_TOKEN:-}" | base64 -w0)"
  git -c "http.https://github.com/.extraheader=${header}" "$@"
}

tag_exists() { git rev-parse -q --verify "refs/tags/v$1" >/dev/null; }

# True when commit $2 (default HEAD) is a release commit for version $1 made
# by this script: matching subject, our committer identity, and a change to
# the version file. See the header for why all three are required.
is_release_commit() {
  local version="$1" ref="${2:-HEAD}"
  [ "$(git log -1 --format=%s "${ref}")" = "Release v${version}" ] || return 1
  [ "$(git log -1 --format=%ce "${ref}")" = "${RELEASE_BOT_EMAIL}" ] || return 1
  git diff-tree --no-commit-id --name-only -r "${ref}" | grep -qxF "${VERSION_FILE}"
}

# True when commit $1 lies in $2..HEAD (reachable from HEAD, not from $2).
in_range() {
  git merge-base --is-ancestor "$1" HEAD 2>/dev/null || return 1
  ! git merge-base --is-ancestor "$1" "$2" 2>/dev/null
}

# One page of merged PRs against main, newest-updated first, as TSV rows
# "number\toid\tupdatedAt\tlabels-json" followed by "PAGEINFO\t<hasNextPage>\t<cursor>".
# oid is "null" when GitHub records no merge commit. labels-json is a JSON
# array of the label names the PR carried *when it was merged*, rebuilt from
# its labeled/unlabeled timeline up to mergedAt (JSON keeps names with
# commas or other punctuation intact). Uses GraphQL directly because
# `gh pr list` cannot order by update time, and the coverage rule below
# depends on that order. Consistent (not the search index). $1 is the page
# cursor, empty for the first page (sent as GraphQL null, not "").
merged_prs_page() {
  local after="$1" query
  local -a cursor=()
  [ -n "${after}" ] && cursor=(-f "after=${after}")
  query='query($owner: String!, $name: String!, $first: Int!, $after: String) {
    repository(owner: $owner, name: $name) {
      pullRequests(states: MERGED, baseRefName: "main", first: $first, after: $after,
                   orderBy: {field: UPDATED_AT, direction: DESC}) {
        pageInfo { hasNextPage endCursor }
        nodes {
          number updatedAt mergedAt mergeCommit { oid }
          timelineItems(itemTypes: [LABELED_EVENT, UNLABELED_EVENT], first: 100) {
            nodes {
              __typename
              ... on LabeledEvent { createdAt label { name } }
              ... on UnlabeledEvent { createdAt label { name } }
            }
          }
        }
      }
    }
  }'
  gh api graphql -f query="${query}" -f owner="${GH_REPO%/*}" -f name="${GH_REPO#*/}" \
    -F first="${PR_QUERY_PAGE_SIZE}" "${cursor[@]}" \
    --jq '
      def labels_at_merge:
        .mergedAt as $m
        | [.timelineItems.nodes[] | select(.createdAt <= $m)]
        | sort_by(.createdAt)
        | reduce .[] as $e ([];
            if $e.__typename == "LabeledEvent" then (. + [$e.label.name] | unique)
            else (. - [$e.label.name]) end);
      .data.repository.pullRequests
      | (.nodes[] | [.number, (.mergeCommit.oid // "null"), .updatedAt, (labels_at_merge | tojson)] | @tsv),
        (["PAGEINFO", (.pageInfo.hasNextPage | tostring), (.pageInfo.endCursor // "")] | @tsv)'
}

# The commit that landed PR $1 on main when GitHub records no merge commit:
# the last commit of the PR, across all pages of its commit list.
last_commit_of_pr() {
  gh api --paginate "repos/${GH_REPO}/pulls/$1/commits" --jq '.[].sha' | tail -n 1
}

# Seconds since the epoch for an ISO-8601 timestamp (any UTC offset).
epoch() { date -u -d "$1" +%s; }

# "<number>\t<labels>" for every PR merged into main whose landing commit
# lies in $1..HEAD. Pages through merged PRs newest-updated first and stops
# at the first PR last updated before the range start: every PR merged in
# the range was updated after it, so none can follow. Git ancestry decides
# membership, so squash, merge, and rebase merges all count. Any API failure,
# or running out of pages before coverage is proven, returns non-zero.
merged_prs_in_range() {
  local since="$1" since_epoch rows number oid updated labels after="" page=0 covered=0 has_next found=""
  # Compare as epoch seconds: GitHub timestamps are UTC ("Z") while git
  # keeps the commit's own offset, so the strings are not comparable.
  since_epoch=$(git log -1 --format=%ct "${since}")
  while [ "${covered}" -eq 0 ]; do
    page=$((page + 1))
    if [ "${page}" -gt "${PR_QUERY_MAX_PAGES}" ]; then
      echo "::error::More than $((PR_QUERY_MAX_PAGES * PR_QUERY_PAGE_SIZE)) merged pull requests updated since the range start; cannot prove the range is covered" >&2
      return 1
    fi
    rows=$(merged_prs_page "${after}") || {
      echo "::error::Could not list merged pull requests (page ${page})" >&2
      return 1
    }
    has_next=false
    # Labels come last so an unlabelled PR (empty field) still parses. The
    # loop is deliberately not piped anywhere: its variables must survive it.
    while IFS=$'\t' read -r number oid updated labels; do
      [ -n "${number}" ] || continue
      if [ "${number}" = "PAGEINFO" ]; then
        has_next="${oid}"; after="${updated}"; continue
      fi
      if [ "$(epoch "${updated}")" -lt "${since_epoch}" ]; then covered=1; continue; fi
      if [ "${oid}" = "null" ]; then
        oid=$(last_commit_of_pr "${number}") || {
          echo "::error::Could not read the commits of pull request #${number}" >&2
          return 1
        }
      fi
      in_range "${oid}" "${since}" || continue
      found+="${number}"$'\t'"${labels}"$'\n'
    done <<<"${rows}"
    [ "${has_next}" = "true" ] || covered=1
  done
  sort -un <<<"${found}" | sed '/^$/d'
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
  prs=$(merged_prs_in_range "${since}") || return 1
  echo "PRs merged since v$1: $(cut -f1 <<<"${prs}" | tr '\n' ' ')" >&2
  # One JSON array of merge-time label names per PR, one per line.
  labels=$(cut -f2 <<<"${prs}")
  # The triggering PR's labels as of the merge event, as a second source for
  # the same snapshot. Its merge commit decides whether it belongs to this
  # release (it may have shipped in an earlier one); without a merge commit
  # to check, include them regardless.
  if [ -z "${PR_MERGE_SHA}" ] || in_range "${PR_MERGE_SHA}" "${since}"; then
    labels+=$'\n'"${PR_LABELS_JSON}"
  fi
  untrusted python scripts/release.py level <<<"${labels}"
}

# Expected artifact names for a version.
expected_assets() { echo "${DIST_NAME}-$1.tar.gz" "${DIST_NAME}-$1-py3-none-any.whl"; }

# Returns 0 when the GitHub release for $1 exists with every expected asset
# (finish_release only creates the release after the PyPI upload succeeded,
# so a full asset set implies the earlier steps are done too), 1 when the
# release is missing or incomplete, and 2 when GitHub could not be asked:
# an API error must not be mistaken for a missing release.
release_is_complete() {
  local have name
  if ! have=$(gh release view "v$1" --json assets --jq '.assets[].name' 2>&1); then
    if grep -qi "not found" <<<"${have}"; then
      return 1
    fi
    echo "::error::Could not query the GitHub release v$1: ${have}" >&2
    return 2
  fi
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
  untrusted twine check "${work}"/dist/*
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

# Complete the release of $1 if this script started it and it is not done.
# Aborts (non-zero) if GitHub cannot say whether it is done.
ensure_finished() {
  local state=0
  if tag_exists "$1" && is_release_commit "$1" "v$1"; then
    release_is_complete "$1" || state=$?
    case "${state}" in
      0) echo "Release v$1 is complete" ;;
      1) finish_release "$1" ;;
      *) return 1 ;;
    esac
  fi
}

main() {
  git config user.name "${RELEASE_BOT_NAME}"
  git config user.email "${RELEASE_BOT_EMAIL}"
  git_auth fetch --quiet origin main --tags
  git reset --quiet --hard origin/main
  local current version level attempt
  current=$(untrusted python scripts/release.py current)

  # 1. Tag a release commit that lost its tag.
  if is_release_commit "${current}" && ! tag_exists "${current}"; then
    echo "main's head is the release commit for v${current} but the tag is missing; tagging it"
    git tag -a "v${current}" -m "v${current}"
    git_auth push origin "refs/tags/v${current}"
  fi

  # 2. Complete the current version if this workflow started it and it is
  #    not finished.
  ensure_finished "${current}"

  # 3. Cut a new release if anything merged since.
  for attempt in $(seq 1 "${MAX_PUSH_ATTEMPTS}"); do
    git_auth fetch --quiet origin main --tags
    git reset --quiet --hard origin/main
    current=$(untrusted python scripts/release.py current)
    if is_release_commit "${current}"; then
      # Also covers a push that GitHub accepted but whose response was lost:
      # the retry lands here with the release commit at the head, so make
      # sure that version is finished before declaring there is nothing to do.
      ensure_finished "${current}"
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
    if git_auth push --atomic origin "HEAD:refs/heads/main" "refs/tags/v${version}"; then
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
