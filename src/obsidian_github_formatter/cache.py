import typing as t

DataType = t.TypeVar("DataType")
Cached = t.Callable[["Cache"], DataType]


class Cache(t.Generic[DataType]):
    _functions: t.ClassVar[t.Dict[str, Cached]] = {}

    def __init__(self) -> None:
        self._cache: t.Dict[str, DataType] = {}

    @classmethod
    def register(cls, target: t.Union[str, Cached]) -> t.Union[t.Callable[[Cached], Cached], Cached]:
        if isinstance(target, str):
            function = None
            function_name = target
        elif target is not None:
            function = target
            function_name = target.__qualname__
        else:
            function = None
            function_name = None

        def registering_decorator(function: Cached) -> Cached:
            name = function_name or function.__qualname__
            if function_name in cls._functions and cls._functions[name] != function:
                raise ValueError()
            cls._functions[name] = function
            return function

        if function is not None:
            return registering_decorator(function)
        return registering_decorator

    def get_value(self, target: t.Union[str, t.Callable]) -> DataType:
        function_name = target if isinstance(target, str) else target.__qualname__
        if function_name not in self._functions:
            raise ValueError()
        if function_name not in self._cache:
            self._cache[function_name] = self._functions[function_name](self)
        return self._cache[function_name]

    def reset(self, target: t.Union[str, t.Callable]) -> bool:
        function_name = target if isinstance(target, str) else target.__qualname__
        if function_name not in self._functions:
            raise ValueError()
        if function_name not in self._cache:
            return False
        del self._cache[function_name]
        return True


cached = Cache.register
