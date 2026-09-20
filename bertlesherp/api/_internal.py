import abc

from typing import (
    Any,
    Dict,
    Optional,
    Union,
)

import tornado.web

from ..config import Config


class RequestHandler(tornado.web.RequestHandler):
    def __init__(self, config: Config, url_part: str, *args, **kwrags):
        super().__init__(*args, **kwargs)
        self.config = config
        self.url_part = url_part


class ApiResponse:
    pass


class ApiSuccess(ApiResponse):
    def __init__(self, status: int, payload: Optional[Dict[str, Any]]):
        self.status = status
        self.payload = payload


class ApiClientError(ApiResponse):
    def __init__(self, status: int, name: str, message: str):
        self.status = status
        self.name = name
        self.message = message


class ApiRequestHandler(tornado.web.RequestHandler, abc.ABC):
    @property
    @classmethod
    @abc.abstractmethod
    def error_names(cls):
        pass

    @property
    @classmethod
    def error_codes(cls):
        error_names = cls.error_names
        return {error_names[index]: index for index in range(len(error_names))}

    def response(self, response: Union[ApiSuccess, ApiClientError]):
        self.set_status(response.status)
        if isinstance(response, ApiSuccess):
            self.write(tornado.escape.json_encode(response.payload))
        elif isinstance(response, ApiClientError):
            self.write(
                tornado.escape.json_encode({
                    "error": {
                        "code": error_codes[response.name],
                        "name": response.name,
                        "message": response.message,
                    },
                })
            )
