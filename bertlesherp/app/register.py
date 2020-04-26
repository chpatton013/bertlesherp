import logging

from typing import (
    Awaitable,
    List,
    Optional,
    Union,
)

import tornado.web
import tornado.websocket

from ..config import Config


class RegisterRequestHandler(tornado.web.RequestHandler):
    def initialize(self):
        pass

    def get(self):
        logging.info("RegisterRequestHandler.get")
        self.render("index.html")


class RegisterWebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self) -> Optional[Awaitable[None]]:
        logging.info("RegisterWebSocketHandler.open")

    def on_message(self,
                   message: Union[str, bytes]) -> Optional[Awaitable[None]]:
        logging.info("RegisterWebSocketHandler.on_message")
        self.write_message(message)

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
