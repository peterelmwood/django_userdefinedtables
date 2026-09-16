"""Tests for scripts/release.py. Run with: python -m unittest discover -s scripts -p 'test_*.py'"""

import unittest

import release

REPO = release.REPO_URL

CHANGELOG = """# Changelog

## [Unreleased]

### Added
- A new thing

## [0.0.14] - 2022

### Added
- Initial release

[Unreleased]: https://github.com/peterelmwood/django_userdefinedtables/compare/v0.0.14...HEAD
[0.0.14]: https://github.com/peterelmwood/django_userdefinedtables/releases/tag/v0.0.14
"""


class BumpVersionTests(unittest.TestCase):
    def test_levels(self):
        self.assertEqual(release.bump_version("0.0.14", "patch"), "0.0.15")
        self.assertEqual(release.bump_version("0.0.14", "minor"), "0.1.0")
        self.assertEqual(release.bump_version("0.0.14", "major"), "1.0.0")
        self.assertEqual(release.bump_version("1.2.3", "minor"), "1.3.0")

    def test_rejects_unknown_level(self):
        with self.assertRaises(ValueError):
            release.bump_version("0.0.14", "huge")


class InitVersionTests(unittest.TestCase):
    INIT = '"""doc"""\n\n__version__ = "0.0.14"\n\nVERSION = __version__\n'

    def test_read_and_set(self):
        self.assertEqual(release.read_version(self.INIT), "0.0.14")
        updated = release.set_version(self.INIT, "0.0.15")
        self.assertEqual(release.read_version(updated), "0.0.15")
        self.assertIn("VERSION = __version__", updated)

    def test_missing_version_raises(self):
        with self.assertRaises(RuntimeError):
            release.read_version("nothing here")


class RollChangelogTests(unittest.TestCase):
    def test_moves_unreleased_under_new_version(self):
        rolled = release.roll_changelog(CHANGELOG, "0.0.14", "0.0.15", "2026-09-16")
        self.assertIn(
            "## [Unreleased]\n\n## [0.0.15] - 2026-09-16\n\n### Added\n- A new thing\n\n## [0.0.14] - 2022", rolled
        )
        self.assertIn("[Unreleased]: {}/compare/v0.0.15...HEAD".format(REPO), rolled)
        self.assertIn("[0.0.15]: {}/compare/v0.0.14...v0.0.15".format(REPO), rolled)
        self.assertIn("[0.0.14]: {}/releases/tag/v0.0.14".format(REPO), rolled)
        self.assertEqual(rolled.count("[Unreleased]:"), 1)

    def test_empty_unreleased_section_gets_a_note(self):
        text = (
            "# Changelog\n\n## [Unreleased]\n\n## [0.0.14] - 2022\n\n- old\n\n[Unreleased]: x/compare/v0.0.14...HEAD\n"
        )
        rolled = release.roll_changelog(text, "0.0.14", "0.0.15", "2026-09-16")
        expected = "## [0.0.15] - 2026-09-16\n\n" + release.EMPTY_SECTION_NOTE + "\n\n## [0.0.14]"
        self.assertIn(expected, rolled)

    def test_unreleased_is_last_section_and_links_missing(self):
        text = "# Changelog\n\n## [Unreleased]\n\n- first ever change\n"
        rolled = release.roll_changelog(text, "0.0.0", "0.0.1", "2026-09-16")
        self.assertIn("## [Unreleased]\n\n## [0.0.1] - 2026-09-16\n\n- first ever change\n", rolled)
        expected_tail = "[Unreleased]: {0}/compare/v0.0.1...HEAD\n[0.0.1]: {0}/compare/v0.0.0...v0.0.1\n".format(REPO)
        self.assertTrue(rolled.endswith(expected_tail), rolled)

    def test_missing_unreleased_raises(self):
        with self.assertRaises(RuntimeError):
            release.roll_changelog("# Changelog\n\n## [0.0.14]\n", "0.0.14", "0.0.15", "2026-09-16")

    def test_roundtrip_is_idempotent_on_headings(self):
        once = release.roll_changelog(CHANGELOG, "0.0.14", "0.0.15", "2026-09-16")
        twice = release.roll_changelog(once, "0.0.15", "0.0.16", "2026-09-17")
        self.assertIn("## [Unreleased]\n\n## [0.0.16] - 2026-09-17\n\n" + release.EMPTY_SECTION_NOTE, twice)
        self.assertIn("## [0.0.15] - 2026-09-16\n\n### Added\n- A new thing", twice)


class ReleaseNotesTests(unittest.TestCase):
    def test_extracts_section_body_without_links(self):
        rolled = release.roll_changelog(CHANGELOG, "0.0.14", "0.0.15", "2026-09-16")
        self.assertEqual(release.release_notes(rolled, "0.0.15"), "### Added\n- A new thing\n")
        self.assertEqual(release.release_notes(rolled, "0.0.14"), "### Added\n- Initial release\n")

    def test_missing_section_raises(self):
        with self.assertRaises(RuntimeError):
            release.release_notes(CHANGELOG, "9.9.9")


if __name__ == "__main__":
    unittest.main()
