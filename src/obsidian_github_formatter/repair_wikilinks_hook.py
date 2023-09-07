#!/usr/bin/env python
import os
import typing as t
from pathlib import Path

import click

from .cache import Cache
from .links import process_file


@click.command()
@click.help_option("--help", "-h")
@click.version_option()
@click.option("--dry-run", "-n", is_flag=True, help="Show what would be changed and do not modify any files.")
@click.option("--make-backups", "-b", is_flag=True, help="Copies the backfile before changes are to be mmade.")
@click.option(
    "--root",
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    default=Path(os.getcwd()),
    help="Root of the repo.",
)
@click.argument("filenames", nargs=-1, type=click.Path(exists=True))
def main(dry_run: bool, make_backups: bool, root: str, filenames: t.List[str]) -> None:  # pragma: no cover
    """Repairs wikilinks -- changes [[link]] link format to [link](link).


    * Supports titles and spaces in link.

    * Checks whether linked file exists.

    * Supports submodules: changes [[link]] to a link [link](https://raw.githubusercontent.com/.../link), based on `.gitmodules` config file.
    """
    cache = Cache(
        root=root,
        dry_run=dry_run,
        make_backups=make_backups,
        processed_files=filenames,
    )
    for filename in filenames:
        process_file(filename, cache)


if __name__ == "__main__":
    main()  # type: ignore
