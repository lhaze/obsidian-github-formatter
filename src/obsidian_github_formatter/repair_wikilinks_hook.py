#!/usr/bin/env python
import os
import typing as t
from pathlib import Path

import click

from .cache import Cache
from .console import color_header
from .errors import (
    Errors,
    Notifications,
)
from .files import expand_dir
from .links import process_file


@click.command()
@click.help_option("--help", "-h")
@click.version_option()
@click.option("--verbose", "-v", count=True, help="Set verbosity level.")
@click.option("--dry-run", "-n", is_flag=True, help="Show what would be changed and do not modify any files.")
@click.option("--make-backups", "-b", is_flag=True, help="Copies the backfile before changes are to be mmade.")
@click.option(
    "--root",
    "-r",
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    default=Path(os.getcwd()),
    help="Root of the vault (it may not be the same as root of the repo).",
)
@click.argument("filenames", nargs=-1, type=click.Path(exists=True))
def main(
    verbose: int, dry_run: bool, make_backups: bool, root: str, filenames: t.List[str]
) -> int:  # pragma: no cover
    """Repairs wikilinks -- changes [[link]] link format to [link](link).


    * Supports titles and spaces in link.

    * Checks whether linked file exists.

    * Supports submodules: changes [[link]] to a link [link](https://github.com/.../raw/master/{filepath}), based on `.gitmodules` config file.
    """
    filepaths = (Path(fn) for fn in filenames)
    filepaths = [p for fp in filepaths for p in expand_dir(fp)]
    cache = Cache[t.Any](
        verbosity=verbose,
        vault_root=Path(root),
        dry_run=dry_run,
        make_backups=make_backups,
        processed_files=filepaths,
    )
    if verbose > 1:
        _echo_vars(cache)
    for filename in filepaths:
        process_file(filename, cache)
    errors: Errors = cache.get_value("get_errors")
    if errors:
        print(color_header("\nErrors:"))
        for error in errors:
            print(f"{error.code}: {', '.join(f'{k}={v}' for k, v in error.kwargs.items())}")
    notifications: Notifications = cache.get_value("get_notifications")
    if verbose > 0 and notifications:
        print(color_header("\nInfo:"))
        print("\n".join(notifications))
    return 1 if errors else 0


def _echo_vars(cache: Cache) -> None:
    print(
        f"{color_header('Vault root:')} {cache.get_value('vault_root')} "
        f"{color_header('Verbosity:')} {cache.get_value('verbosity')} "
        f"{color_header('Dry-run:')} {cache.get_value('dry_run')} "
        f"{color_header('make-backups:')} {cache.get_value('make_backups')} "
    )
    processed_files = cache.get_value("processed_files")
    if not processed_files:
        print(f"{color_header('Processed:')} None")
    else:
        print(f"{color_header('Processed:')}")
        print("\n".join(str(p) for p in processed_files))


if __name__ == "__main__":
    raise SystemExit(main())  # type: ignore
