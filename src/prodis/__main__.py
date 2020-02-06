#!/usr/bin/env python3

import sys

from . import debug
from . import logger

from .cli import main

logger.basic_config(level=logger.DEBUG if debug.DEBUG else logger.NOTICE)

sys.exit(main(debug.DEBUG_ASYNCIO))
