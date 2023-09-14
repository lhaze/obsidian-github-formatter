import typing as t

from pca.packages.errors import ExceptionWithCode

from .cache import cached

Errors = t.List[ExceptionWithCode]
Notifications = t.List[str]


@cached
def get_errors(_: t.Any) -> Errors:
    return []


@cached
def get_notifications(_: t.Any) -> Notifications:
    return []
