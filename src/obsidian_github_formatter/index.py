import json
import typing as t
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from .cache import (
    Cache,
    cached,
)


class TreeElements(Enum):
    space = ". . "
    branch = "│ . "
    tee = "├── "
    last = "└── "

    def __repr__(self) -> str:
        return f"TreeElements.{self.name}"


class FileFormat(Enum):
    directory = "directories"
    markdown = "markdown"
    image = "image"
    audio = "audio"
    video = "video"
    pdf = "pdf"
    other = "other"

    @classmethod
    def from_extension(cls, extension: t.Optional[str]) -> t.Optional["FileFormat"]:
        map = {
            ".3gp": cls.audio,
            ".bmp": cls.image,
            ".flac": cls.audio,
            ".gif": cls.image,
            ".jpeg": cls.image,
            ".jpg": cls.image,
            ".m4a": cls.audio,
            ".md": cls.markdown,
            ".mkv": cls.video,
            ".mov": cls.video,
            ".mp3": cls.audio,
            ".mp4": cls.video,
            ".ogg": cls.audio,
            ".ogv": cls.video,
            ".pdf": cls.pdf,
            ".png": cls.image,
            ".svg": cls.image,
            ".wav": cls.audio,
            ".webm": cls.video,
        }
        return map.get((extension or "").lower(), cls.other)


@dataclass(frozen=True)
class IndexLine:
    elements: t.Tuple[TreeElements, ...]
    path: Path

    def __repr__(self) -> str:
        return "".join(e.value for e in self.elements) + f" {self.path.name}"


Summary = t.DefaultDict[FileFormat, int]
FileMap = t.Dict[str, t.List[Path]]


def _iterate_file_names(filepath: Path) -> t.Generator[str, None, None]:
    yield filepath.name
    if filepath.suffix.lower() == ".md":
        yield filepath.stem


def _filter_out_filepaths(filepath: Path) -> bool:
    return filepath.name.startswith(".")


def _walk_path_tree(
    root: Path, current: Path, summary: Summary, file_map: FileMap, prefix: t.Tuple[TreeElements, ...] = ()
) -> t.Generator[IndexLine, None, None]:
    contents = sorted(current.iterdir())
    elements = [TreeElements.tee] * (len(contents) - 1) + [TreeElements.last]
    for element, path in zip(elements, contents):
        if _filter_out_filepaths(path):
            continue
        elif path.is_dir():
            yield IndexLine(prefix + (element,), path)
            summary[FileFormat.directory] += 1
            extension = TreeElements.branch if element == TreeElements.tee else TreeElements.space
            yield from _walk_path_tree(root, path, summary=summary, file_map=file_map, prefix=prefix + (extension,))
        else:
            yield IndexLine(prefix + (element,), path)
            for file_name in _iterate_file_names(path):
                file_map[file_name].append(path.relative_to(root))
            summary[FileFormat.from_extension(path.suffix)] += 1  # type: ignore


@dataclass(frozen=True)
class Index:
    root: Path
    lines: t.Tuple[IndexLine]
    file_map: FileMap
    summary: Summary

    def __repr__(self) -> str:
        return (
            f"{self.root.name if self.root else ''}\n"
            + "\n".join(repr(line) for line in (self.lines or []))
            + f"\n\n{json.dumps(dict((f.value, c) for f, c in (self.summary or {}).items()), sort_keys=True)}"  # noqa: C402
        )


@cached
def build_index(cache: Cache) -> Index:
    dir_path = Path(cache.get_value("vault_root"))
    summary = defaultdict(int)
    file_map = defaultdict(list)

    return Index(
        root=dir_path,
        lines=tuple(_walk_path_tree(dir_path, dir_path, summary, file_map)),
        summary=summary,
        file_map=file_map,
    )


def render_doc_link(path: Path) -> str:
    if " " in str(path):
        return f"[{path.name}](<{str(path)}>)"
    return f"[{path.name}]({str(path)})"


SUMMARY_TEMPLATE = """
| File Format | Count |
| :---        |  ---: |
{summary_lines}
"""


def render_summary_line(format: FileFormat, count: int) -> str:
    return f"| {format.value} | {count} |"


def render_summary(summary: Summary) -> str:
    return SUMMARY_TEMPLATE.format(summary_lines="\n".join(render_summary_line(f, summary[f]) for f in FileFormat))


INDEX_TEMPLATE = """
# Index

<sub>Do not edit this file, it is auto-generated.</sub>

**{dir_name}**
{rendered_index}

## Summary
{rendered_summary}"""


def render_index_line(line: IndexLine, root: t.Optional[Path] = None) -> str:
    doc_link = line.path.relative_to(root) if root else line.path
    return "".join(e.value for e in line.elements) + render_doc_link(doc_link)


def render_index(index: Index) -> str:
    return INDEX_TEMPLATE.format(
        dir_name=index.root.name,
        rendered_index="\n".join(render_index_line(line, index.root) for line in index.lines),
        rendered_summary=render_summary(index.summary),
    )
