from obsidian_github_formatter.cache import Cache
from obsidian_github_formatter.repository import (
    Submodule,
    get_repo_root,
    get_submodules,
)

from . import _test_stub_path


def test_get_repo_root(cache: Cache) -> None:
    cache.add_values(root=_test_stub_path)
    assert get_repo_root(cache) == (_test_stub_path / "..").resolve()


def test_get_submodules_empty(cache: Cache) -> None:
    cache.add_values(get_repo_root=_test_stub_path)
    assert get_submodules(cache) == []


def test_get_submodules(cache: Cache) -> None:
    cache.add_values(get_repo_roo=_test_stub_path / "..")
    submodule_path = _test_stub_path / "submodule"

    assert get_submodules(cache) == [
        Submodule(
            name="submodule",
            path=submodule_path,
            repo_url="git@github.com:lhaze/obsidian-github-formatter-test-submodule.git",
        )
    ]
