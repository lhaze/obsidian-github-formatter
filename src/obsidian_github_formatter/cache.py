import typing as t

DataType = t.TypeVar("DataType")
Cached = t.Callable[["Cache"], DataType]


class Cache(t.Generic[DataType]):
    _functions: t.ClassVar[t.Dict[str, Cached]] = {}

    def __init__(self, **initial: DataType) -> None:
        self._values: t.Dict[str, DataType] = initial

    def __repr__(self) -> str:
        return f"Cache({', '.join(self._values)})"

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
                raise ValueError(
                    f"Function named '{function_name}' already registered: {cls._functions[name]}. "
                    "Trying to register: '{function}'."
                )
            cls._functions[name] = function
            return function

        if function is not None:
            return registering_decorator(function)
        return registering_decorator

    def get_value(self, target: t.Union[str, t.Callable]) -> DataType:
        function_name = target if isinstance(target, str) else target.__qualname__
        if function_name not in self._values and function_name not in self._functions:
            raise ValueError(
                f"No value '{target}' to get. Values: {set(self._values)}. Functions: {set(self._functions)}"
            )
        if function_name not in self._values:
            self._values[function_name] = self._functions[function_name](self)
        return self._values[function_name]

    def add_vales(self, **values: DataType) -> None:
        self._values.update(values)

    def reset(self, target: t.Union[str, t.Callable]) -> bool:
        function_name = target if isinstance(target, str) else target.__qualname__
        if function_name not in self._functions:
            raise ValueError(f"No function to reset. Functions: {set(self._functions)}")
        if function_name not in self._values:
            return False
        del self._values[function_name]
        return True


cached = Cache.register
