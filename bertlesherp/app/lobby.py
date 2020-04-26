import logging

from typing import (
    Awaitable,
    List,
    Optional,
    Union,
)

import tornado.routing
import tornado.web
import tornado.websocket

from ..config import Config


class LobbyRequestHandler(tornado.web.RequestHandler):
    def initialize(self):
        pass

    def get(self):
        logging.info("LobbyRequestHandler.get")
        self.render("index.html")


class LobbyWebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self) -> Optional[Awaitable[None]]:
        logging.info("LobbyWebSocketHandler.open")

    def on_message(self,
                   message: Union[str, bytes]) -> Optional[Awaitable[None]]:
        logging.info("LobbyWebSocketHandler.on_message")
        self.write_message(message)

    def on_close(self) -> None:
        logging.info("LobbyWebSocketHandler.on_close")

    def on_ping(self, data: bytes) -> None:
        logging.info("LobbyWebSocketHandler.on_ping")


def lobby_routes(config: Config,
                 url_part: Optional[str] = None) -> List[tornado.web.URLSpec]:
    return [
        tornado.web.URLSpec(config.request_url(url_part), LobbyRequestHandler),
        tornado.web.URLSpec(
            config.websocket_url(url_part), LobbyWebSocketHandler
        ),
    ]
