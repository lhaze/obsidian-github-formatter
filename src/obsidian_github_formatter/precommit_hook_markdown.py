#!/usr/bin/env python
import typing as t

import click

from obsidian_github_formatter.markdown import process_file


@click.command()
@click.option("--dry-run", is_flag=True, help="Show what would be changed and do not modify any files.")
@click.option("--make-backups", is_flag=True, help="Copies the backfile before changes are to be mmade.")
@click.argument("filenames", nargs=-1, type=click.Path(exists=True))
def main(dry_run: bool, filenames: t.List[str]) -> None:
    for filename in filenames:
        process_file(filename, dry_run=dry_run, make_backups=True)


if __name__ == "__main__":
    main()  # type: ignore
