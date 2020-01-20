#!/usr/bin/env python3

from __future__ import annotations


def abbr_str(o: object, max_len: int = 500, cont: str = '...') -> str:

    s = repr(o) if isinstance(o, (str, bytes, bytearray)) else str(o)
    return s if len(s) <= max_len else s[:max(max_len - len(cont), 0)] + cont


class HexInt(int):

    def __repr__(self) -> str:
        return hex(self)
