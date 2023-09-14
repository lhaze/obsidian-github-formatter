import typing as t
from configparser import ConfigParser
from dataclasses import dataclass
from pathlib import Path
from re import search

from .cache import (
    Cache,
    cached,
)

_GITHUB_FILE_URL_PATTERN = "https://raw.githubusercontent.com/{repo}/{branch}/{filepath}"


@cached
def get_repo_root(cache: Cache) -> Path:
    root: Path = cache.get_value("vault_root")
    if not (root / ".git").exists():
        root = root.parent
    return root.resolve()


@dataclass
class Submodule:
    name: str
    path: Path
    repo_url: str

    @property
    def repo(self) -> str:
        repo = search(r"github.com:([\w\.\_\-\/]+).git", self.repo_url)
        if not repo:
            raise ValueError(f"Submodule's repo not matching: {self.repo_url}")  # pragma: no cover
        return repo.group(1)

    def substitute(self, filepath: Path) -> str:
        relative_filepath = filepath.relative_to(self.path)
        return _GITHUB_FILE_URL_PATTERN.format(repo=self.repo, branch="master", filepath=str(relative_filepath))


@cached
def get_submodules(cache: Cache) -> t.List[Submodule]:
    root = cache.get_value(get_repo_root)
    gitmodules_path = root / ".gitmodules"
    if not gitmodules_path.exists():
        return []
    config = ConfigParser()
    config.read(str(gitmodules_path))
    result = []
    for key, section in config.items():
        if section.get("path"):
            submodule_path = root / section["path"]
            submodule_name = search(r'"(\w+)"', key)
            result.append(
                Submodule(
                    name=submodule_name.group(1) if submodule_name else "",
                    path=submodule_path,
                    repo_url=section["url"],
                )
            )
    return result
