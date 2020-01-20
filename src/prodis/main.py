#!/usr/bin/env python3

import asyncio as _asyncio

from .clientcounterpart import ClientListener as _ClientListener


async def main_coroutine(*tasks) -> _asyncio.Future:

    futures = [task.schedule() for task in tasks]
    return await _asyncio.gather(*futures)


def main() -> None:

    create_from = [
        _ClientListener,
    ]

    tasks = [factory() for factory in create_from]
    _asyncio.run(main_coroutine(*tasks))


if __name__ == '__main__':
    import sys as _sys
    _sys.exit(main())
