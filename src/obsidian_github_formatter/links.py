import re
import typing as t
from pathlib import Path

from .cache import Cache
from .console import (
    color_diff,
    color_header,
)
from .files import (
    diff_files,
    read_file,
    save_file,
)
from .index import Index
from .repository import (
    Submodule,
    get_submodules,
)


def process_file(filename: str, cache: Cache) -> None:
    original_text = read_file(filename)
    formatted_text = repair_links(original_text, cache)
    if original_text != formatted_text:
        if not cache.get_value("dry_run"):
            save_file(filename, formatted_text, make_backups=cache.get_value("make_backups"))
        else:
            _print(color_header(f"File '{filename}' would be modified. Here's the diff:"))
            diff = diff_files(original_text, formatted_text)
            _print("\n".join(color_diff(diff)))


def _print(text: str) -> None:  # pragma: no cover
    print(color_header(text))


_WIKILINK_STRUCTURE = re.compile(r"\[\[(.*?)\]\]")


def repair_links(contents: str, cache: Cache) -> str:
    return _WIKILINK_STRUCTURE.sub(lambda m: substitute_wikilink_format(m.group(1), cache), contents)


def substitute_wikilink_format(contents: str, cache: Cache) -> str:
    index: Index = cache.get_value("build_index")
    prefix: str = cache.get_value("link_prefix", "")
    bracket_l = bracket_r = ""

    link = contents.strip("[]")
    if "|" in contents:
        title, link = link.rsplit("|", 1)
    else:
        title = None
    paths = index.file_map.get(link, None)
    if paths is None:
        raise ValueError(f"No file identifies as '{link}'")  # pragma: no cover
    if len(paths) > 1:
        raise ValueError(f"More than one file identifies as '{link}': {[str(p) for p in paths]}")  # pragma: no cover
    path = paths[0]
    path_str = str(path)
    if " " in path_str or " " in prefix:
        bracket_l = "<"
        bracket_r = ">"
    if title is None:
        title = link
    url = _substitute_submodules(cache, path) or f"{prefix}/{path}"
    return f"[{title}]({bracket_l}{url}{bracket_r})"


def _substitute_submodules(cache: Cache, path: Path) -> t.Optional[str]:
    submodules: t.Dict[Path, Submodule] = cache.get_value(get_submodules)
    root: Path = cache.get_value("root")

    for submodule in submodules:
        assert isinstance(submodule, Submodule)
        if submodule.path in (root / path).parents:
            return submodule.substitute(root / path)
    return
