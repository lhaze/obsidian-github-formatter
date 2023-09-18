import difflib
import shutil
import typing as t
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .cache import (
    Cache,
    cached,
)

_BACKUP_EXTENSION = "~"


def read_file(filename: Path) -> str:  # pragma: no cover
    with open(filename, "r") as f:
        return f.read()


def save_file(path: Path, contents: str, make_backups: bool = False) -> None:  # pragma: no cover
    if make_backups:
        shutil.copyfile(str(path), f"{str(path)}.{_BACKUP_EXTENSION}")
    with open(path, "w") as f:
        f.write(contents)


def diff_files(text_a: str, text_b: str) -> t.Iterator[str]:
    return difflib.unified_diff(text_a.splitlines(), text_b.splitlines())


def filter_out_filepaths(filepath: Path) -> bool:
    return filepath.name.startswith(".")


def expand_dir(current: Path) -> t.Generator[Path, None, None]:
    if not current.is_dir():
        yield current
        return
    contents = sorted(current.iterdir())
    for path in contents:
        if not filter_out_filepaths(path):
            if path.is_dir():
                yield from expand_dir(path)
            elif FileFormat.markdown == FileFormat.from_path(path):
                yield path


class FileFormat(Enum):
    directory = "directories"
    markdown = "markdown"
    image = "image"
    audio = "audio"
    video = "video"
    pdf = "pdf"
    other = "other"

    @classmethod
    def from_path(cls, path: Path) -> "FileFormat":
        return _EXTENSTION_FILE_FORMAT_MAP.get(path.suffix.lower(), FileFormat.other)

    @classmethod
    def from_link(cls, link: str) -> "FileFormat":
        path = Path(link)
        return _EXTENSTION_FILE_FORMAT_MAP.get(path.suffix.lower(), FileFormat.markdown)


_EXTENSTION_FILE_FORMAT_MAP = {
    ".3gp": FileFormat.audio,
    ".bmp": FileFormat.image,
    ".flac": FileFormat.audio,
    ".gif": FileFormat.image,
    ".jpeg": FileFormat.image,
    ".jpg": FileFormat.image,
    ".m4a": FileFormat.audio,
    ".md": FileFormat.markdown,
    ".mkv": FileFormat.video,
    ".mov": FileFormat.video,
    ".mp3": FileFormat.audio,
    ".mp4": FileFormat.video,
    ".ogg": FileFormat.audio,
    ".ogv": FileFormat.video,
    ".pdf": FileFormat.pdf,
    ".png": FileFormat.image,
    ".svg": FileFormat.image,
    ".wav": FileFormat.audio,
    ".webm": FileFormat.video,
}


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
