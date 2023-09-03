import typing as t

from colorama import (
    Fore,
    init,
)

# Initialize colorama
init()


def color_header(content: str) -> str:
    return Fore.YELLOW + content + Fore.RESET


def color_diff(diff: t.Iterator[str]) -> t.Generator[str, None, None]:
    for line in diff:
        if line.startswith("-"):
            yield Fore.RED + line
        elif line.startswith("+"):
            yield Fore.GREEN + line
        else:
            yield Fore.RESET + line
