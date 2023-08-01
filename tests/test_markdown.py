from unittest import mock

from obsidian_github_formatter import markdown
from obsidian_github_formatter.index import Index


@mock.patch("obsidian_github_formatter.markdown._read_file")
@mock.patch("obsidian_github_formatter.markdown._save_file")
def test_process_file_wet_run(_save_file: mock.MagicMock, _read_file: mock.MagicMock, index: Index) -> None:
    _read_file.return_value = "\n".join(
        (
            "FOO BAR",
            "foo [[OTHER FOO]] bar!",
        )
    )
    markdown.process_file("foo/bar.md", index)
    _save_file.assert_called_once_with(
        "foo/bar.md",
        "\n".join(
            (
                "FOO BAR",
                "foo [OTHER FOO](/foo/OTHER FOO.md) bar!",
            )
        ),
        make_backups=False,
    )


@mock.patch("obsidian_github_formatter.markdown._read_file")
@mock.patch("obsidian_github_formatter.markdown._print")
def test_process_file_dry_run(_print: mock.MagicMock, _read_file: mock.MagicMock, index: Index) -> None:
    _read_file.return_value = "\n".join(
        (
            "FOO BAR",
            "foo [[OTHER FOO]] bar!",
        )
    )
    markdown.process_file("foo/bar.md", index, dry_run=True)
    assert _print.call_args_list[0][0] == ("\x1b[33mFile 'foo/bar.md' would be modified. Here's the diff:\x1b[39m",)
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
                "\x1b[32m+foo [OTHER FOO](/foo/OTHER FOO.md) bar!",
            )
        ),
    )
