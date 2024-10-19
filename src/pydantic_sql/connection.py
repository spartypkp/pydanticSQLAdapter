from typing import Protocol, Any, List, Dict
from types import TracebackType
from typing_extensions import Type

class PostgreSQLConnection(Protocol):
    def execute(self, query: str, params: Dict[str, Any] = None) -> Any:
        ...

    def fetch_all(self) -> List[Dict[str, Any]]:
        ...

    def fetch_one(self) -> Dict[str, Any]:
        ...

    def close(self) -> None:
        ...

    def __enter__(self) -> 'PostgreSQLConnection':
        ...

    def __exit__(self, exc_type: Type[BaseException] | None,
                 exc_val: BaseException | None,
                 exc_tb: TracebackType | None) -> None:
        ...