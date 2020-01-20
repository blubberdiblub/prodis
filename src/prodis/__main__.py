#!/usr/bin/env python3

import sys

from . import logger

from .cli import main

logger.basic_config(level=(logger.DEBUG if __debug__ or sys.flags.dev_mode
                           else logger.NOTICE))

sys.exit(main())
