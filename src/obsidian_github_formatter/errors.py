import typing as t

from pca.packages.errors import ExceptionWithCode

from .cache import cached

Errors = t.List[ExceptionWithCode]


@cached
def get_errors(_: t.Any) -> Errors:
    return []
