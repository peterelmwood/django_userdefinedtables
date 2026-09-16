#!/usr/bin/env python3
"""Release helpers used by .github/workflows/release.yml.

    python scripts/release.py bump <major|minor|patch> [--date YYYY-MM-DD]
        Bump ``__version__`` in userdefinedtables/__init__.py, move the
        ``[Unreleased]`` section of CHANGELOG.md under the new version, and
        print the new version.

    python scripts/release.py notes <version>
        Print the CHANGELOG.md section for ``version`` (used as the GitHub
        release body).

The module has no third-party dependencies so the workflow can run it with
a bare interpreter. Tests live in scripts/test_release.py.
"""

import argparse
import datetime
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
INIT_PATH = ROOT / "userdefinedtables" / "__init__.py"
CHANGELOG_PATH = ROOT / "CHANGELOG.md"
REPO_URL = "https://github.com/peterelmwood/django_userdefinedtables"

LEVELS = ("major", "minor", "patch")
VERSION_RE = re.compile(r'^__version__ = "(?P<version>\d+\.\d+\.\d+)"$', re.M)
UNRELEASED_HEADING = "## [Unreleased]"
EMPTY_SECTION_NOTE = "- Maintenance release with no user-facing changes."


def bump_version(version, level):
    """Return ``version`` bumped at ``level`` per semantic versioning."""
    if level not in LEVELS:
        raise ValueError("level must be one of {}, got {!r}".format(", ".join(LEVELS), level))
    major, minor, patch = (int(part) for part in version.split("."))
    if level == "major":
        return "{}.0.0".format(major + 1)
    if level == "minor":
        return "{}.{}.0".format(major, minor + 1)
    return "{}.{}.{}".format(major, minor, patch + 1)


def read_version(init_text):
    match = VERSION_RE.search(init_text)
    if not match:
        raise RuntimeError("Unable to find __version__ in {}".format(INIT_PATH))
    return match.group("version")


def set_version(init_text, new_version):
    return VERSION_RE.sub('__version__ = "{}"'.format(new_version), init_text, count=1)


def roll_changelog(changelog_text, old_version, new_version, date):
    """Turn the ``[Unreleased]`` section into ``[new_version] - date`` and refresh the link references."""
    if UNRELEASED_HEADING not in changelog_text:
        raise RuntimeError("CHANGELOG.md has no '{}' section".format(UNRELEASED_HEADING))

    head, _, rest = changelog_text.partition(UNRELEASED_HEADING)
    next_heading = re.search(r"^## ", rest, re.M)
    body = rest[: next_heading.start()] if next_heading else rest
    tail = rest[next_heading.start() :] if next_heading else ""

    # Link references sit at the very end of the file; keep them out of the section body.
    link_re = re.compile(r"^\[[^\]]+\]: \S+$", re.M)
    if not next_heading:
        first_link = link_re.search(body)
        if first_link:
            tail = body[first_link.start() :]
            body = body[: first_link.start()]

    if not body.strip():
        body = "\n\n{}\n\n".format(EMPTY_SECTION_NOTE)

    new_heading = "## [{}] - {}".format(new_version, date)
    rolled = "{}{}\n\n{}{}".format(head, UNRELEASED_HEADING, new_heading, body.rstrip("\n") + "\n\n")

    unreleased_link = "[Unreleased]: {}/compare/v{}...HEAD".format(REPO_URL, new_version)
    version_link = "[{}]: {}/compare/v{}...v{}".format(new_version, REPO_URL, old_version, new_version)
    old_link_re = re.compile(r"^\[Unreleased\]: \S+$", re.M)
    if old_link_re.search(tail):
        tail = old_link_re.sub("{}\n{}".format(unreleased_link, version_link), tail, count=1)
    else:
        tail = tail.rstrip("\n") + "\n\n{}\n{}\n".format(unreleased_link, version_link)
    return rolled + tail


def release_notes(changelog_text, version):
    """Return the body of the ``[version]`` section, without its heading."""
    pattern = re.compile(r"^## \[{}\][^\n]*\n(?P<body>.*?)(?=^## |\Z)".format(re.escape(version)), re.M | re.S)
    match = pattern.search(changelog_text)
    if not match:
        raise RuntimeError("CHANGELOG.md has no section for version {}".format(version))
    body = match.group("body")
    body = re.sub(r"^\[[^\]]+\]: \S+$", "", body, flags=re.M)
    return body.strip() + "\n"


def cmd_bump(args):
    init_text = INIT_PATH.read_text()
    old_version = read_version(init_text)
    new_version = bump_version(old_version, args.level)
    date = args.date or datetime.date.today().isoformat()
    INIT_PATH.write_text(set_version(init_text, new_version))
    CHANGELOG_PATH.write_text(roll_changelog(CHANGELOG_PATH.read_text(), old_version, new_version, date))
    print(new_version)


def cmd_notes(args):
    sys.stdout.write(release_notes(CHANGELOG_PATH.read_text(), args.version))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    bump = sub.add_parser("bump", help="bump the version and roll the changelog")
    bump.add_argument("level", choices=LEVELS)
    bump.add_argument("--date", help="release date, YYYY-MM-DD (default: today)")
    bump.set_defaults(func=cmd_bump)
    notes = sub.add_parser("notes", help="print the changelog section for a version")
    notes.add_argument("version")
    notes.set_defaults(func=cmd_notes)
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
