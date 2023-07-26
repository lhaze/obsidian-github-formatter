import re

from .index import Index


def repair_links(contents: str, index: Index, prefix: str = "") -> str:
    pattern = re.compile(r"\[\[(.*?)\]\]")
    return pattern.sub(lambda m: substitute_wikilink_format(m.group(1), index, prefix), contents)


def substitute_wikilink_format(contents: str, index: Index, prefix: str = "") -> str:
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
    if title:
        return f"[{title}]({prefix}/{path})"
    else:
        return f"[{link}]({prefix}/{path})"