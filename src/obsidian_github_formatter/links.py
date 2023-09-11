import re
import typing as t
from pathlib import Path

from pca.packages.errors import (
    ErrorCatalog,
    error_builder,
)

from .cache import Cache
from .console import (
    color_diff,
    color_header,
)
from .errors import Errors
from .files import (
    ProcessedFile,
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
    process_file: ProcessedFile = cache.get_value("get_processed_file")
    with process_file:
        process_file.set(Path(filename))
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


class LinksErrors(ErrorCatalog):
    TargetNotFound = error_builder()
    MoreThanOneFile = error_builder()


def substitute_wikilink_format(contents: str, cache: Cache) -> str:
    index: Index = cache.get_value("build_index")
    prefix: str = cache.get_value("link_prefix", "")
    errors: Errors = cache.get_value("get_errors")
    processed_file: ProcessedFile = cache.get_value("get_processed_file")
    bracket_l = bracket_r = ""

    link = contents.strip("[]")
    if "|" in contents:
        title, link = link.rsplit("|", 1)
    else:
        title = None
    paths = index.file_map.get(link, None)
    if paths is None:
        errors.append(LinksErrors.TargetNotFound(target=link, title=title, file=str(processed_file.filepath)))
        return contents
    if len(paths) > 1:  # pragma: no cover
        errors.append(
            LinksErrors.MoreThanOneFile(
                target=link, target_files=[str(p) for p in paths], file=str(processed_file.filepath)
            )
        )
        return contents
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
