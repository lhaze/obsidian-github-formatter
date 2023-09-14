import typing as t
from dataclasses import dataclass
from pathlib import Path

import dacite
import yaml
from pca.packages.errors import (
    ErrorCatalog,
    error_builder,
)

from .cache import (
    Cache,
    cached,
)

_CONFIG_FILE_NAME = ".ogf-config.yaml"


@dataclass
class LinksConfig:
    autogenerate_dir: t.Optional[str] = None
    autogenerate_template: t.Optional[str] = None


@dataclass
class Config:
    links: LinksConfig = LinksConfig()


class ConfigErrors(ErrorCatalog):
    ConfigFileNotReadable = error_builder()
    ConfigFileSyntaxError = error_builder()
    ConfigContentError = error_builder()


@cached
def get_config(cache: Cache) -> Config:
    root: Path = cache.get_value("vault_root")
    errors: list = cache.get_value("get_errors")
    config_filepath = root / _CONFIG_FILE_NAME
    if not config_filepath.exists():
        return Config()
    try:
        contents = _read(config_filepath)
        return dacite.from_dict(Config, contents)
    except IOError as e:  # pragma: no cover
        errors.append(ConfigErrors.ConfigFileNotReadable(origin=e))
        return Config()
    except yaml.YAMLError as e:
        errors.append(ConfigErrors.ConfigFileSyntaxError(origin=e))
        return Config()
    except dacite.DaciteError as e:  # pragma: no cover
        errors.append(ConfigErrors.ConfigContentError(origin=e))
        return Config()


def _read(filename: Path) -> dict:  # pragma: no cover
    with open(filename) as f:
        return yaml.safe_load(f)
