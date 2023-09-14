from unittest import mock

from obsidian_github_formatter.cache import Cache
from obsidian_github_formatter.links import (
    process_file,
    repair_links,
    substitute_wikilink_format,
)


class TestSubstituteWikilinkFormat:
    def test_base(self, cache: Cache) -> None:
        assert substitute_wikilink_format("[[bar.jpg]]", cache) == "[bar.jpg](/foo/bar.jpg)"

    def test_with_prefix(self, cache: Cache) -> None:
        cache.add_values(link_prefix="/prefix")
        assert substitute_wikilink_format("[[bar.jpg]]", cache) == "[bar.jpg](/prefix/foo/bar.jpg)"

    def test_with_title(self, cache: Cache) -> None:
        assert substitute_wikilink_format("[[bar.jpg|Title]]", cache) == "[Title](/foo/bar.jpg)"

    def test_with_space(self, cache: Cache) -> None:
        assert substitute_wikilink_format("[[OTHER FOO]]", cache) == "[OTHER FOO](</foo/OTHER FOO.md>)"

    def test_in_submodule(self, cache: Cache) -> None:
        assert substitute_wikilink_format("[[other baz.png]]", cache) == (
            "[other baz.png]"
            "(<https://raw.githubusercontent.com/lhaze/obsidian-github-formatter-test-submodule/master/bar/bar baz/other baz.png>)"
        )


class TestRepairLinks:
    def test_md(self, cache: Cache) -> None:
        assert repair_links("foo [[bar_file]] baz", cache) == "foo [bar_file](/bar/bar_file.md) baz"

    def test_image(self, cache: Cache) -> None:
        assert repair_links("foo ![[bar.jpg]] baz", cache) == "foo ![bar.jpg](/foo/bar.jpg) baz"

    def test_with_title(self, cache: Cache) -> None:
        assert repair_links("foo ![[bar.jpg|Title]] baz", cache) == "foo ![Title](/foo/bar.jpg) baz"


class TestProcessFile:
    @mock.patch("obsidian_github_formatter.links.read_file")
    @mock.patch("obsidian_github_formatter.links._print")
    def test_process_file_dry_run(self, _print: mock.MagicMock, read_file: mock.MagicMock, cache: Cache) -> None:
        cache.add_values(dry_run=True)
        read_file.return_value = "\n".join(
            (
                "FOO BAR",
                "foo [[OTHER FOO]] bar!",
            )
        )
        process_file("foo/bar.md", cache)
        assert _print.call_args_list[0][0] == (
            "\x1b[33mFile 'foo/bar.md' would be modified. Here's the diff:\x1b[39m",
        )
        assert _print.call_args_list[1][0] == (
            "\n".join(
                (
                    "\x1b[31m--- ",
                    "",
                    "\x1b[32m+++ ",
                    "",
                    "\x1b[39m@@ -1,2 +1,2 @@",
                    "",
                    "\x1b[39m FOO BAR",
                    "\x1b[31m-foo [[OTHER FOO]] bar!",
                    "\x1b[32m+foo [OTHER FOO](</foo/OTHER FOO.md>) bar!",
                )
            ),
        )

    @mock.patch("obsidian_github_formatter.links.read_file")
    @mock.patch("obsidian_github_formatter.links.save_file")
    def test_process_file_wet_run(self, save_file: mock.MagicMock, read_file: mock.MagicMock, cache: Cache) -> None:
        read_file.return_value = "\n".join(
            (
                "FOO BAR",
                "foo [[OTHER FOO]] bar!",
            )
        )
        process_file("foo/bar.md", cache)
        save_file.assert_called_once_with(
            "foo/bar.md",
            "\n".join(
                (
                    "FOO BAR",
                    "foo [OTHER FOO](</foo/OTHER FOO.md>) bar!",
                )
            ),
            make_backups=False,
        )
