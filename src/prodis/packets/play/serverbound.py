#!/usr/bin/env python3

from __future__ import annotations

from collections.abc import (
    Iterator as _Iterator,
)

from ..packet import MinecraftPacketWithID as _MinecraftPacketWithID

from ...utils import fmt as _fmt
from ...utils import byte as _byte
from ...utils import iter as _iter


class Packet(_MinecraftPacketWithID):

    pass


class ClientSettings(Packet):

    id = 0x5

    def __init__(
            self,
            locale: str = 'en_US',
            view_distance: int = 32,
            chat_mode: int = 0,
            chat_colors: bool = True,
            displayed_skin_parts: int = 0x7f,
            main_hand: int = 1,
            enable_text_filtering: bool = False,
            allow_server_listings: bool = True,
    ) -> None:

        super().__init__()

        self.locale = locale
        self.view_distance = view_distance
        self.chat_mode = chat_mode
        self.chat_colors = chat_colors
        self.displayed_skin_parts = displayed_skin_parts
        self.main_hand = main_hand
        self.enable_text_filtering = enable_text_filtering
        self.allow_server_listings = allow_server_listings

    def __getstate__(self) -> dict[str, object]:

        return {
            'locale':                self.locale,
            'view_distance':         self.view_distance,
            'chat_mode':             self.chat_mode,
            'chat_colors':           self.chat_colors,
            'displayed_skin_parts':  _fmt.HexInt(self.displayed_skin_parts),
            'main_hand':             self.main_hand,
            'enable_text_filtering': self.enable_text_filtering,
            'allow_server_listings': self.allow_server_listings,
        }

    @property
    def payload(self) -> bytes | bytearray:

        return b'%b%c%b%c%c%b%c%c' % (
            _byte.render_varstr(self.locale),
            self.view_distance,
            _byte.render_varint(self.chat_mode),
            self.chat_colors,
            self.displayed_skin_parts,
            _byte.render_varint(self.main_hand),
            self.enable_text_filtering,
            self.allow_server_listings,
        )

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        self.locale = _iter.consume_varstr(it)
        self.view_distance = next(it)
        self.chat_mode = _iter.consume_varint(it)
        self.chat_colors = bool(next(it))
        self.displayed_skin_parts = next(it)
        self.main_hand = _iter.consume_varint(it)
        self.enable_text_filtering = bool(next(it))
        self.allow_server_listings = bool(next(it))
        () = it

        assert self.locale.lower() in ['en_us', 'en_gb', 'de_de']
        assert 2 <= self.view_distance <= 32
        assert 0 <= self.chat_mode <= 2
        assert (self.displayed_skin_parts & ~0x7f) == 0
        assert 0 <= self.main_hand <= 1


class PluginMessage(Packet):

    id = 0xa

    def __init__(
            self,
            namespace: str = 'minecraft',
            channel: str = None,
            data: bytes | bytearray = None,
    ) -> None:

        super().__init__()

        self.namespace = namespace
        self.channel = channel
        self.data = data

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            'namespace',
            'channel',
            'data',
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        return b'%b%b' % (
            _byte.render_identifier(self.namespace, self.channel),
            self.data,
        )

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        self.namespace, self.channel = _iter.consume_identifier(it)
        self.data = bytes(it)
