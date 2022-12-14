from collections import defaultdict
from pathlib import Path

import pytest

from obsidian_github_formatter.index import (
    FileFormat,
    Index,
    IndexLine,
)
from obsidian_github_formatter.index import TreeElements as TE
from obsidian_github_formatter.index import (
    build_index,
    render_doc_link,
    render_index_line,
    render_summary,
)

from . import _test_stub_path


def test_index() -> None:
    assert repr(Index.create(_test_stub_path)) == "\n".join(
        (
            "stub",
            "├──  foo",
            "│ . ├──  OTHER FOO.md",
            "│ . └──  foo.md",
            "└──  bar",
            ". . ├──  bar baz",
            ". . │ . ├──  baz.txt",
            ". . │ . ├──  other baz.png",
            ". . │ . └──  baz.jpg",
            ". . └──  bar_file.md",
            "",
            "{'directories': 3, 'markdown': 3, 'other': 1, 'image': 2}",
        )
    )


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("foo/foo.md", "[foo.md](foo/foo.md)"),
        ("bar/bar baz/other baz.png", "[other baz.png](<bar/bar baz/other baz.png>)"),
    ],
)
def test_render_doc_link(path: str, expected: str) -> None:
    path = Path(path)
    assert render_doc_link(path) == expected


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        (
            IndexLine((TE.space, TE.branch, TE.tee), Path("foo/foo.md")),
            ". . │ . ├── [foo.md](foo/foo.md)",
        ),
        (
            IndexLine((TE.space, TE.last), Path("bar/bar baz/other baz.png")),
            ". . └── [other baz.png](<bar/bar baz/other baz.png>)",
        ),
    ],
)
def test_render_line(line: IndexLine, expected: str) -> None:
    assert render_index_line(line) == expected


def test_render_summary() -> None:
    summary = defaultdict(
        int,
        {
            FileFormat.directory: 3,
            FileFormat.markdown: 7,
            FileFormat.video: 3,
            FileFormat.pdf: 1,
        },
    )
    expected = "\n".join(
        (
            "",
            "| File Format | Count |",
            "| :---        |  ---: |",
            "| directories | 3 |",
            "| markdown | 7 |",
            "| image | 0 |",
            "| audio | 0 |",
            "| video | 3 |",
            "| pdf | 1 |",
            "| other | 0 |",
            "",
        )
    )
    assert render_summary(summary) == expected


def test_build_index() -> None:
    expected = "\n".join(
        (
            "",
            "# Index",
            "",
            "<sub>Do not edit this file, it is auto-generated.</sub>",
            "",
            "**stub**",
            "├── [foo](foo)",
            "│ . ├── [OTHER FOO.md](<foo/OTHER FOO.md>)",
            "│ . └── [foo.md](foo/foo.md)",
            "└── [bar](bar)",
            ". . ├── [bar baz](<bar/bar baz>)",
            ". . │ . ├── [baz.txt](<bar/bar baz/baz.txt>)",
            ". . │ . ├── [other baz.png](<bar/bar baz/other baz.png>)",
            ". . │ . └── [baz.jpg](<bar/bar baz/baz.jpg>)",
            ". . └── [bar_file.md](bar/bar_file.md)",
            "",
            "## Summary",
            "",
            "| File Format | Count |",
            "| :---        |  ---: |",
            "| directories | 3 |",
            "| markdown | 3 |",
            "| image | 2 |",
            "| audio | 0 |",
            "| video | 0 |",
            "| pdf | 0 |",
            "| other | 1 |",
            "",
        )
    )
    actual = build_index(_test_stub_path)
    assert actual == expected
