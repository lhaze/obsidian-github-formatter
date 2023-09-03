import difflib
import shutil
import typing as t

_BACKUP_EXTENSION = "~"


def read_file(filename: str) -> str:  # pragma: no cover
    with open(filename, "r") as f:
        return f.read()


def save_file(filename: str, contents: str, make_backups: bool = False) -> None:  # pragma: no cover
    if make_backups:
        shutil.copyfile(filename, f"{filename}.{_BACKUP_EXTENSION}")
    with open(filename, "w") as f:
        f.write(contents)


def diff_files(text_a: str, text_b: str) -> t.Iterator[str]:
    return difflib.unified_diff(text_a.splitlines(), text_b.splitlines())
