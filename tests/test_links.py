from obsidian_github_formatter.index import Index
from obsidian_github_formatter.links import (
    repair_links,
    substitute_wikilink_format,
)


class TestSubstituteWikilinkFormat:
    def test_base(self, index: Index) -> None:
        assert substitute_wikilink_format("[[bar.jpg]]", index) == "[bar.jpg](/foo/bar.jpg)"

    def test_with_prefix(self, index: Index) -> None:
        assert substitute_wikilink_format("[[bar.jpg]]", index, prefix="/prefix") == "[bar.jpg](/prefix/foo/bar.jpg)"

    def test_with_title(self, index: Index) -> None:
        assert substitute_wikilink_format("[[Title|bar.jpg]]", index) == "[Title](/foo/bar.jpg)"

    def test_with_space(self, index: Index) -> None:
        assert substitute_wikilink_format("[[OTHER FOO]]", index) == "[OTHER FOO](</foo/OTHER FOO.md>)"


class TestRepairLinks:
    def test_md(self, index: Index) -> None:
        assert repair_links("foo [[bar_file]] baz", index) == "foo [bar_file](/bar/bar_file.md) baz"

    def test_image(self, index: Index) -> None:
        assert repair_links("foo ![[bar.jpg]] baz", index) == "foo ![bar.jpg](/foo/bar.jpg) baz"

    def test_with_title(self, index: Index) -> None:
        assert repair_links("foo ![[Title|bar.jpg]] baz", index) == "foo ![Title](/foo/bar.jpg) baz"
