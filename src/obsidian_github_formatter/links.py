import re

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


def process_file(filename: str, cache: Cache) -> None:
    original_text = read_file(filename)
    index = cache.get_value("build_index")
    formatted_text = repair_links(original_text, index)
    if original_text != formatted_text:
        if not cache.get_value("dry_run"):
            save_file(filename, formatted_text, make_backups=cache.get_value("make_backups"))
        else:
            _print(color_header(f"File '{filename}' would be modified. Here's the diff:"))
            diff = diff_files(original_text, formatted_text)
            _print("\n".join(color_diff(diff)))


def _print(text: str) -> None:  # pragma: no cover
    print(color_header(text))


def repair_links(contents: str, index: Index, prefix: str = "") -> str:
    pattern = re.compile(r"\[\[(.*?)\]\]")
    return pattern.sub(lambda m: substitute_wikilink_format(m.group(1), index, prefix), contents)


def substitute_wikilink_format(contents: str, index: Index, prefix: str = "") -> str:
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
    path = str(paths[0])
    if " " in path or " " in prefix:
        bracket_l = "<"
        bracket_r = ">"
    if title is None:
        title = link
    return f"[{title}]({bracket_l}{prefix}/{path}{bracket_r})"
