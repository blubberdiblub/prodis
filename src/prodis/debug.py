#!/usr/bin/env python3

import os as _os
import sys as _sys


DEBUG = bool(_sys.flags.dev_mode)

DEBUG_ASYNCIO = DEBUG or (not _sys.flags.ignore_environment and
                          bool(_os.environ.get('PYTHONASYNCIODEBUG')))
