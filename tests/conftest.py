from pathlib import Path

import pytest

from obsidian_github_formatter.index import Index


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
