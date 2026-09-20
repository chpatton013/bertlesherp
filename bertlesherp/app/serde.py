import abc

from typing import (
    Any,
    Dict,
    List,
    Optional,
)


class Encodable(abc.ABC):
    @abc.abstractmethod
    def encode(self) -> Dict[str, Any]:
        pass


class Decodable(abc.ABC):
    @classmethod
    @abc.abstractmethod
    def decode(cls, message: Dict[str, Any]) -> 'Decodable':
        pass


class DecodeError(Exception):
    def __init__(
        self,
        missing_fields: Optional[List[str]] = None,
        exclusive_fields: Optional[List[str]] = None
    ):
        self.missing_fields = missing_fields
        self.exclusive_fields = exclusive_fields
