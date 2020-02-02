#!/usr/bin/env python3

from __future__ import annotations

from typing import (
    ByteString as _ByteString,
    Iterator as _Iterator,
    Union as _Union,
)

from ..packet import NewMinecraftPacket as _NewMinecraftPacket
from ..metaclasses import (
    IDDispatcher as _IDDispatcher,
    IDVerifier as _IDVerifier,
)

from .. import byteutils as _byteutils
from .. import iterutils as _iterutils


class Packet(_NewMinecraftPacket, metaclass=_IDDispatcher):

    def __str__(self) -> str:

        try:
            args = self._fmt_args()

        except AttributeError:
            return super().__str__()

        return f'{self.__class__.__name__}({args})'


class _VerifiedPacket(Packet, metaclass=_IDVerifier):

    pass


class ClientSettings(_VerifiedPacket):

    ID = 0x5

    def __init__(
            self,
            locale: str = 'en_US',
            view_distance: int = 32,
            chat_mode: int = 0,
            chat_colors: bool = True,
            displayed_skin_parts: int = 0x7f,
            main_hand: int = 1,
    ) -> None:

        super().__init__()

        self.locale = locale
        self.view_distance = view_distance
        self.chat_mode = chat_mode
        self.chat_colors = chat_colors
        self.displayed_skin_parts = displayed_skin_parts
        self.main_hand = main_hand

    def _fmt_args(self) -> str:

        return ', '.join([
            f'locale={self.locale!r}',
            f'view_distance={self.view_distance!r}',
            f'chat_mode={self.chat_mode!r}',
            f'chat_colors={self.chat_colors!r}',
            f'displayed_skin_parts={self.displayed_skin_parts:#x}',
            f'main_hand={self.main_hand!r}',
        ])

    def consume_payload(self, it: _Union[_ByteString, _Iterator[int]]) -> None:

        it = iter(it)
        self.locale = _iterutils.consume_string(it)
        self.view_distance = next(it)
        self.chat_mode = _iterutils.consume_varint(it)
        self.chat_colors = bool(next(it))
        self.displayed_skin_parts = next(it)
        self.main_hand = _iterutils.consume_varint(it)
        () = it

        assert self.locale.lower() in ['en_us', 'en_gb', 'de_de']
        assert 2 <= self.view_distance <= 32
        assert 0 <= self.chat_mode <= 2
        assert (self.displayed_skin_parts & ~0x7f) == 0
        assert 0 <= self.main_hand <= 1

    def render_payload(self) -> _ByteString:

        return b'%b%c%b%c%c%b' % (
            _byteutils.render_string(self.locale),
            self.view_distance,
            _byteutils.render_varint(self.chat_mode),
            self.chat_colors,
            self.displayed_skin_parts,
            _byteutils.render_varint(self.main_hand),
        )


class PluginMessage(_VerifiedPacket):

    ID = 0xb

    def __init__(
            self,
            namespace: str = 'minecraft',
            channel: str = None,
            channel_data: _ByteString = None,
    ) -> None:

        super().__init__()

        self.namespace = namespace
        self.channel = channel
        self.channel_data = channel_data

    def _fmt_args(self) -> str:

        return ', '.join([
            f'namespace={self.namespace!r}',
            f'channel={self.channel!r}',
            f'channel_data={self.channel_data!r}',
        ])

    def consume_payload(self, it: _Union[_ByteString, _Iterator[int]]) -> None:

        it = iter(it)
        self.namespace, self.channel = _iterutils.consume_identifier(it)
        self.channel_data = bytes(it)

    def render_payload(self) -> _ByteString:

        return b'%b%b' % (
            _byteutils.render_identifier(self.namespace, self.channel),
            self.channel_data,
        )


Packet.packet_types = {
    ClientSettings.ID: ClientSettings,
    PluginMessage.ID: PluginMessage,
}
