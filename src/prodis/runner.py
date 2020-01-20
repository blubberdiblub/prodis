#!/usr/bin/env python3

import trio as _trio

from .clientlistener import ClientListener as _ClientListener
from .serverconnector import ServerConnector as _ServerConnector

from .logger import Logger as _Logger
_log = _Logger(__name__)


async def main_coroutine() -> None:

    client_listener = _ClientListener()
    server_connector = _ServerConnector()

    async with _trio.open_nursery() as nursery:
        nursery.start_soon(client_listener.run)
        # nursery.start_soon(server_connector.run)
