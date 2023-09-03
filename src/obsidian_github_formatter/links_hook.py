#!/usr/bin/env python
import os
import typing as t

import click

from .cache import Cache
from .links import process_file


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
def main(dry_run: bool, make_backups: bool, root: str, filenames: t.List[str]) -> None:  # pragma: no cover
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
