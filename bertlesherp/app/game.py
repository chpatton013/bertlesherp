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


class GameRequestHandler(tornado.web.RequestHandler):
    def initialize(self):
        pass

    def get(self):
        logging.info("GameRequestHandler.get")
        self.render("index.html")


class GameWebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self) -> Optional[Awaitable[None]]:
        logging.info("GameWebSocketHandler.open")

    def on_message(self,
                   message: Union[str, bytes]) -> Optional[Awaitable[None]]:
        logging.info("GameWebSocketHandler.on_message")
        self.write_message(message)

    def on_close(self) -> None:
        logging.info("GameWebSocketHandler.on_close")

    def on_ping(self, data: bytes) -> None:
        logging.info("GameWebSocketHandler.on_ping")


def game_routes(config: Config,
                url_part: Optional[str] = None) -> List[tornado.web.URLSpec]:
    return [
        tornado.web.URLSpec(config.request_url(url_part), GameRequestHandler),
        tornado.web.URLSpec(
            config.websocket_url(url_part), GameWebSocketHandler
        ),
    ]
