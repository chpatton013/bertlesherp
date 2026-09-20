import abc
import logging
import uuid

from typing import (
    Any,
    Awaitable,
    Dict,
    List,
    Optional,
    Union,
)

import tornado.escape
import tornado.web
import tornado.websocket

from .serde import (
    Encodable,
    Decodable,
    DecodeError,
)
from .state import (
    lookup_user,
    lookup_token,
    persist_user,
)
from .user import User
from ..config import Config

REGISTER_REQUEST_CODES = [
    "REGISTER_USER",
    "DEREGISTER_USER",
]

REGISTER_ERROR_NAMES = [
    "UNKNOWN_ERROR",
    "DECODE_ERROR",
    "USER_TOKEN_NOT_FOUND",
    "USER_NAME_ALREADY_EXISTS",
]

REGISTER_ERROR_CODES = {
    REGISTER_ERROR_NAMES[index]: index
    for index in range(len(REGISTER_ERROR_NAMES))
}


class RegisterError(Encodable):
    def __init__(self, name: str, message: str):
        self.code = REGISTER_ERROR_CODES[name]
        self.name = name
        self.message = message

    @staticmethod
    def from_decode_error(e: DecodeError) -> 'RegisterError':
        message = "Failed to decode message:"
        if e.missing_fields:
            message += f" missing fields {str(e.missing_fields)}"
        if e.exclusive_fields:
            message += f" exclusive fields {str(e.exclusive_fields)}"
        return RegisterError("DECODE_ERROR", message)

    def encode(self) -> Dict[str, Any]:
        return dict(
            code=self.code,
            name=self.name,
            message=self.message,
        )


class RegisterUserRequest(Decodable):
    def __init__(self, name: str, token: Optional[str]):
        self.name = name
        self.token = token

    @classmethod
    def decode(cls, message: Dict[str, Any]) -> 'RegisterUserRequest':
        if "name" not in message:
            raise DecodeError(["name"])
        return RegisterUserRequest(message["name"], message.get("token"))


class RegisterUserResponse(Encodable):
    def __init__(
        self,
        user: Optional[User] = None,
        error: Optional[RegisterError] = None
    ):
        self.user = user
        self.error = error

    def encode(self) -> Dict[str, Any]:
        message = dict()
        if self.user:
            message["user"] = self.user.encode()
        if self.error:
            message["error"] = self.error.encode()
        return message


class DeregisterUserRequest(Decodable):
    def __init__(self, token: str):
        self.token = token

    @classmethod
    def decode(cls, message: Dict[str, Any]) -> 'DeregisterUserRequest':
        if "token" not in message:
            raise DecodeError(["token"])
        return DeregisterUserRequest(message["token"])


class DeregisterUserResponse(Encodable):
    def __init__(self, error: Optional[RegisterError] = None):
        self.error = error

    def encode(self) -> Dict[str, Any]:
        message = dict()
        if self.error:
            message["error"] = self.error.encode()
        else:
            message["ack"] = True
        return message


class RegisterRequest(Decodable):
    def __init__(
        self,
        register_user: Optional[RegisterUserRequest] = None,
        deregister_user: Optional[DeregisterUserRequest] = None
    ):
        self.register_user = register_user
        self.deregister_user = deregister_user

    @classmethod
    def decode(cls, message: Dict[str, Any]) -> 'RegisterRequest':
        logging.info("%s", message)
        if "register_user" in message and "deregister_user" in message:
            raise DecodeError(
                exclusive_fields=["register_user", "deregister_user"]
            )
        elif "register_user" in message:
            return RegisterRequest(
                RegisterUserRequest.decode(message["register_user"])
            )
        elif "deregister_user" in message:
            return RegisterRequest(
                DeregisterUserRequest.decode(message["deregister_user"])
            )
        else:
            raise DecodeError(
                missing_fields=["register_user", "deregister_user"]
            )


class RegisterResponse(Encodable):
    def __init__(
        self,
        register_user: Optional[RegisterUserResponse] = None,
        deregister_user: Optional[DeregisterUserResponse] = None,
        error: Optional[RegisterError] = None
    ):
        self.register_user = register_user
        self.deregister_user = deregister_user
        self.error = error

    def encode(self) -> Dict[str, Any]:
        message = dict()
        if self.register_user:
            message["register_user"] = self.register_user.encode()
        if self.deregister_user:
            message["deregister_user"] = self.deregister_user.encode()
        if self.error:
            message["error"] = self.error.encode()
        return message


class RegisterRequestHandler(tornado.web.RequestHandler):
    def initialize(self):
        pass

    def get(self):
        logging.info("RegisterRequestHandler.get")
        self.render("register.html")


class RegisterWebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self) -> Optional[Awaitable[None]]:
        logging.info("RegisterWebSocketHandler.open")

    def on_register_user_request(
        self, request: RegisterUserRequest
    ) -> RegisterUserResponse:
        token = lookup_token(request.name)
        if token:
            if request.token == token:
                return RegisterUserResponse(user=user)
            else:
                return RegisterUserResponse(
                    error=RegisterError(
                        "USER_NAME_ALREADY_EXISTS",
                        f"User with name {request.name} already exists in user set"
                    )
                )
        else:
            if request.token:
                token = request.token
            else:
                token = generate_token()
            user = persist_user(request.name, token)
            return RegisterUserResponse(user=user)

    def on_deregister_user_request(
        self, request: DeregisterUserRequest
    ) -> DeregisterUserResponse:
        user = lookup_user(request.token)
        if user:
            purge_user(user)
            return DeregisterUserResponse()
        else:
            return DeregisterUserResponse(
                error=RegisterError(
                    "USER_TOKEN_NOT_FOUND",
                    f"User token {request.token} was not found in user set",
                )
            )

    def on_message(self,
                   message: Union[str, bytes]) -> Optional[Awaitable[None]]:
        logging.info("RegisterWebSocketHandler.on_message: %s", message)

        try:
            request = RegisterRequest.decode(
                tornado.escape.json_decode(message)
            )
        except DecodeError as e:
            self.write_message(
                RegisterResponse(error=RegisterError.from_decode_error(e)
                                 ).encode()
            )
            return

        if request.register_user:
            self.write_message(
                RegisterResponse(
                    register_user=self.
                    on_register_user_request(request.register_user)
                ).encode()
            )
        elif request.deregister_user:
            self.write_message(
                RegisterResponse(
                    deregister_user=self.
                    on_deregister_user_request(request.deregister_user)
                ).encode()
            )

    def on_close(self) -> None:
        logging.info("RegisterWebSocketHandler.on_close")

    def on_ping(self, data: bytes) -> None:
        logging.info("RegisterWebSocketHandler.on_ping")


def register_routes(config: Config, url_part: Optional[str] = None
                    ) -> List[tornado.web.URLSpec]:
    return [
        tornado.web.URLSpec(
            config.request_url(url_part), RegisterRequestHandler
        ),
        tornado.web.URLSpec(
            config.websocket_url(url_part), RegisterWebSocketHandler
        ),
    ]
