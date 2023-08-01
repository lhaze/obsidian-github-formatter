#!/usr/bin/env python
import difflib
import os
import shutil
import typing as t

import click

from .bash_utils import (
    color_diff,
    color_header,
)
from .index import Index
from .links import repair_links


def process_file(filename: str, index: Index, dry_run: bool = False, make_backups: bool = False) -> None:
    original_text = _read_file(filename)
    formatted_text = format_markdown(original_text, index)
    if original_text != formatted_text:
        if not dry_run:
            _save_file(filename, formatted_text, make_backups=make_backups)
        else:
            _print(color_header(f"File '{filename}' would be modified. Here's the diff:"))
            diff = difflib.unified_diff(original_text.splitlines(), formatted_text.splitlines())
            _print("\n".join(color_diff(diff)))


def _read_file(filename: str) -> str:  # pragma: no cover
    with open(filename, "r") as f:
        return f.read()


_BACKUP_EXTENSION = "~"


def _save_file(filename: str, contents: str, make_backups: bool = False) -> None:  # pragma: no cover
    if make_backups:
        shutil.copyfile(filename, f"{filename}.{_BACKUP_EXTENSION}")
    with open(filename, "w") as f:
        f.write(contents)


def _print(text: str) -> None:  # pragma: no cover
    print(color_header(text))


def format_markdown(contents: str, index: Index) -> str:
    return repair_links(contents, index)


@click.command()
@click.option("--dry-run", is_flag=True, help="Show what would be changed and do not modify any files.")
@click.option("--make-backups", is_flag=True, help="Copies the backfile before changes are to be mmade.")
@click.option(
    "--root",
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    default=os.getcwd(),
    help="Root of the repo.",
)
@click.argument("filenames", nargs=-1, type=click.Path(exists=True))
def _main(dry_run: bool, make_backups: bool, root: str, filenames: t.List[str]) -> None:  # pragma: no cover
    index = Index.create(dir_path=root)
    for filename in filenames:
        process_file(filename, index, dry_run=dry_run, make_backups=make_backups)


if __name__ == "__main__":
    _main()  # type: ignore
