#!/usr/bin/env python3

import logging
import os

import tornado.httpserver
import tornado.ioloop
import tornado.template

from .app.game import game_routes
from .app.lobby import lobby_routes
from .app.register import register_routes
from .config import (
    make_config,
    set_config_singleton,
)


def main():
    config = make_config()
    set_config_singleton(config)

    logging.basicConfig(level=logging._nameToLevel[config.log_level])

    logging.info(f"Listening on {config.bind_address}:{config.bind_port}")

    application = tornado.web.Application(
        handlers=(
            game_routes(config, "/game") + lobby_routes(config, "/lobby") +
            register_routes(config, "/")
        ),
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
    )
    server = tornado.httpserver.HTTPServer(application)
    server.bind(port=config.bind_port, address=config.bind_address)
    server.start(config.server_processes)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
