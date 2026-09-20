import argparse
import os

from typing import (
    Any,
    Optional,
)

DEFAULT_BIND_ADDRESS = "0.0.0.0"
DEFAULT_BIND_PORT = 80
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_ROOT_URL = "/"
DEFAULT_SERVER_PROCESSES = 1

ENV_VAR_BIND_ADDRESS = "BS__BIND_ADDRESS"
ENV_VAR_BIND_PORT = "BS__BIND_PORT"
ENV_VAR_LOG_LEVEL = "BS__LOG_LEVEL"
ENV_VAR_ROOT_URL = "BS__ROOT_URL"
ENV_VAR_SERVER_PROCESSES = "BS__SERVER_PROCESSES"

LOG_LEVEL_CHOICES = [
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
]

WEBSOCKET_URL_PART = "ws"


class Config:
    def __init__(
        self, log_level: str, root_url: str, bind_port: int, bind_address: str,
        server_processes: int
    ):
        self.log_level = log_level
        self.root_url = root_url
        self.bind_port = bind_port
        self.bind_address = bind_address
        self.server_processes = server_processes

    def request_url(self, url_part: Optional[str] = None) -> str:
        return os.path.join(self.root_url, url_part)

    def websocket_url(self, url_part: Optional[str] = None) -> str:
        return os.path.join(self.request_url(url_part), WEBSOCKET_URL_PART)


class ConfigArg:
    def __init__(
        self,
        *args,
        env: Optional[str] = None,
        default: Optional[str] = None,
        **kwargs
    ):
        self.args = args
        self.kwargs = kwargs
        if env:
            self.kwargs["default"] = os.environ.get(env, default)
        else:
            self.kwargs["default"] = default

    def __str__(self):
        return f"ConfigArg(args={self.args}, kwargs={self.kwargs})"


def make_config() -> Config:
    values = dict(
        log_level=ConfigArg(
            "--log-level",
            choices=LOG_LEVEL_CHOICES,
            default=DEFAULT_LOG_LEVEL,
            env=ENV_VAR_LOG_LEVEL
        ),
        root_url=ConfigArg(
            "--root-url", default=DEFAULT_ROOT_URL, env=ENV_VAR_ROOT_URL
        ),
        bind_port=ConfigArg(
            "--bind-port",
            default=DEFAULT_BIND_PORT,
            type=int,
            env=ENV_VAR_BIND_PORT
        ),
        bind_address=ConfigArg(
            "--bind-address",
            default=DEFAULT_BIND_ADDRESS,
            env=ENV_VAR_BIND_ADDRESS
        ),
        server_processes=ConfigArg(
            "--server-processes",
            default=DEFAULT_SERVER_PROCESSES,
            type=int,
            env=ENV_VAR_SERVER_PROCESSES
        ),
    )

    parser = argparse.ArgumentParser()
    for value in values.values():
        parser.add_argument(*value.args, **value.kwargs)
    args = parser.parse_args()

    return Config(
        args.log_level,
        args.root_url,
        args.bind_port,
        args.bind_address,
        args.server_processes,
    )
