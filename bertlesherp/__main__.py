#!/usr/bin/env python3

import logging
import os

from typing import (
    Any,
)

import tornado.httpserver
import tornado.ioloop
import tornado.template

from .api.register import RegisterRequestHandler
from .config import (
    Config,
    make_config,
)


class Factory:
    def __init__(self, object_type: Any, *args: Any, **kwargs: Any):
        self.object_type = object_type
        self.args = args
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs) -> Any:
        return self.object_type(*self.args, *args, **self.kwargs, **kwargs)


def _route(
    config: Config, url_part: str, object_type: Any, *args: Any, **kwargs: Any
):
    return tornado.web.URLSpec(
        config.request_url(url_part),
        Factory(object_type, config, url_part, *args, **kwargs)
    )


def main():
    config = make_config()

    logging.basicConfig(level=logging._nameToLevel[config.log_level])

    logging.info(f"Listening on {config.bind_address}:{config.bind_port}")

    application = tornado.web.Application(
        handlers=[_route(config, "/api/register", RegisterRequestHandler)],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
    )
    server = tornado.httpserver.HTTPServer(application)
    server.bind(port=config.bind_port, address=config.bind_address)
    server.start(config.server_processes)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
