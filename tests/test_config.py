from unittest import mock

import yaml

from obsidian_github_formatter.cache import Cache
from obsidian_github_formatter.config import (
    Config,
    LinksConfig,
    get_config,
)

from . import _test_stub_path


@mock.patch("obsidian_github_formatter.config._read")
def test_existing_config_file(_read: mock.MagicMock, cache: Cache) -> None:
    _read.return_value = {"links": {"autogenerate_dir": "bar"}}
    assert get_config(cache) == Config(links=LinksConfig(autogenerate_dir="bar"))


def test_non_existing_config_file(cache: Cache) -> None:
    cache.add_values(vault_root=_test_stub_path / "..")
    assert get_config(cache) == Config()


@mock.patch("obsidian_github_formatter.config._read")
def test_invalid_config_file(_read: mock.MagicMock, cache: Cache) -> None:
    error = yaml.YAMLError()
    _read.side_effect = error
    assert get_config(cache) == Config()
    assert cache.get_value("get_errors")[0].to_dict() == {
        "code": "ConfigFileSyntaxError",
        "catalog": "ConfigErrors",
        "kwargs": {"origin": error},
    }
