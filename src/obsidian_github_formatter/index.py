import typing as t
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class TreeElements(Enum):
    space = "    "
    branch = "│   "
    tee = "├── "
    last = "└── "

    def __repr__(self) -> str:
        return f"TreeElements.{self.name}"


@dataclass(frozen=True)
class IndexLine:
    elements: t.Tuple[TreeElements]
    path: Path

    def __repr__(self) -> str:
        return "".join(e.value for e in self.elements) + f" {self.path.name}"


@dataclass(frozen=True)
class Index:
    root: Path
    lines: t.Tuple[IndexLine]
    files: int
    directories: int

    @classmethod
    def create(
        cls,
        dir_path: t.Union[Path, str],
    ) -> "Index":
        dir_path = Path(dir_path)
        files = 0
        directories = 0

        def inner(dir_path: Path, prefix: t.Sequence[TreeElements] = ()) -> t.Tuple[t.Sequence[TreeElements], Path]:
            nonlocal files, directories
            contents = list(dir_path.iterdir())
            elements = [TreeElements.tee] * (len(contents) - 1) + [TreeElements.last]
            for element, path in zip(elements, contents):
                if path.is_dir():
                    yield IndexLine(prefix + (element,), path)
                    directories += 1
                    extension = TreeElements.branch if element == TreeElements.tee else TreeElements.space
                    yield from inner(path, prefix=prefix + (extension,))
                else:
                    yield IndexLine(prefix + (element,), path)
                    files += 1

        return cls(root=dir_path, lines=tuple(inner(dir_path)), files=files, directories=directories)

    def __repr__(self) -> str:
        return (
            f"{self.root.name}\n"
            + "\n".join(repr(line) for line in self.lines)
            + f"\n\n{self.directories} directories"
            + (f", {self.files} files" if self.files else "")
        )
