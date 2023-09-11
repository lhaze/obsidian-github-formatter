import difflib
import shutil
import typing as t
from dataclasses import dataclass
from pathlib import Path

from .cache import (
    Cache,
    cached,
)

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


@dataclass
class ProcessedFile:
    filepath: t.Optional[Path] = None

    def set(self, filepath: Path) -> None:
        self.filepath = filepath

    def reset(self) -> None:
        self.filepath = None

    def __enter__(self) -> "ProcessedFile":
        return self

    def __exit__(self, _: t.Any, __: t.Any, ___: t.Any) -> None:
        self.reset()


@cached
def get_processed_file(cache: Cache) -> ProcessedFile:
    return ProcessedFile()
