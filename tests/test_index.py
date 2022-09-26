from obsidian_github_formatter.index import Index

from . import _test_stub_path


def test_index() -> None:
    assert repr(Index.create(_test_stub_path)) == "\n".join(
        (
            "stub",
            "├──  foo",
            "│   ├──  OTHER FOO.md",
            "│   └──  foo.md",
            "└──  bar",
            "    ├──  baz",
            "    │   ├──  baz.txt",
            "    │   ├──  other baz.png",
            "    │   └──  baz.jpg",
            "    └──  bar_file.md",
            "",
            "3 directories, 6 files",
        )
    )
