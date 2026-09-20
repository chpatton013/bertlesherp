from typing import (
    Any,
    Dict,
)

from .serde import (
    Encodable,
    Decodable,
    DecodeError,
)


class User(Encodable, Decodable):
    def __init__(self, name, token):
        self.name = name
        self.token = token

    def encode(self) -> Dict[str, Any]:
        return dict(
            name=self.name,
            token=self.token,
        )

    @classmethod
    def decode(cls, message: Dict[str, Any]) -> 'User':
        if "name" not in message:
            raise DecodeError(["name"])
        if "token" not in message:
            raise DecodeError(["token"])
        return User(message["name"], message["token"])
