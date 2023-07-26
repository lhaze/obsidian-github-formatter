from pathlib import Path

import pytest

from obsidian_github_formatter.index import Index
from obsidian_github_formatter.links import (
    repair_links,
    substitute_wikilink_format,
)


@pytest.fixture(scope="session")
def index() -> Index:
    return Index(
        file_map={
            "OTHER FOO": [Path("foo/OTHER FOO.md")],
            "bar.jpg": [Path("foo/bar.jpg")],
            "bar_file": [Path("bar/bar_file.md")],
            "bar_file.md": [Path("bar/bar_file.md")],
            "baz.txt": [Path("bar/bar baz/baz.txt")],
            "foo": [Path("foo/foo.md"), Path("bar/foo.md")],
            "foo.md": [Path("foo/foo.md"), Path("bar/foo.md")],
            "other baz.png": [Path("bar/bar baz/other baz.png")],
        },
        root=None,  # type: ignore
        lines=None,  # type: ignore
        summary=None,  # type: ignore
    )


class TestSubstituteWikilinkFormat:
    @pytest.mark.parametrize(
        ("wikilink", "expected_link"),
        [
            ("[[OTHER FOO]]", "[OTHER FOO](/foo/OTHER FOO.md)"),
            ("[[bar.jpg]]", "[bar.jpg](/foo/bar.jpg)"),
        ],
    )
    def test_base(self, wikilink: str, expected_link: str, index: Index) -> None:
        assert substitute_wikilink_format(wikilink, index) == expected_link

    def test_with_prefix(self, index: Index) -> None:
        assert substitute_wikilink_format("[[bar.jpg]]", index, prefix="/prefix") == "[bar.jpg](/prefix/foo/bar.jpg)"

    def test_with_title(self, index: Index) -> None:
        assert substitute_wikilink_format("[[Title|bar.jpg]]", index) == "[Title](/foo/bar.jpg)"


class TestRepairLinks:
    def test_md(self, index: Index) -> None:
        assert repair_links("foo [[bar_file]] baz", index) == "foo [bar_file](/bar/bar_file.md) baz"

    def test_image(self, index: Index) -> None:
        assert repair_links("foo ![[bar.jpg]] baz", index) == "foo ![bar.jpg](/foo/bar.jpg) baz"
