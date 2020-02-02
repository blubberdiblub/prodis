#!/usr/bin/env python3

from __future__ import annotations

from typing import (
    ByteString as _ByteString,
    Type as _Type,
)

from .packet import NewMinecraftPacket as _NewMinecraftPacket

from . import iterutils as _iterutils


class IDDispatcher(type):

    def __call__(
            cls: _Type[_NewMinecraftPacket], data: _ByteString
    ) -> _NewMinecraftPacket:

        if not isinstance(data, _ByteString):
            raise TypeError("data must be bytes-like")

        it = iter(data)
        packet_id = _iterutils.consume_varint(it)

        try:
            dispatched = cls.packet_types[packet_id]
        except KeyError:
            raise ValueError(f"unknown packet ID {packet_id:#x}") from None

        packet = object.__new__(dispatched)
        # cls.__init__(packet, data)
        packet.__init__()
        packet.consume_payload(it)
        () = it

        return packet


class IDVerifier(IDDispatcher):

    def __call__(
            cls: _Type[_NewMinecraftPacket], data: _ByteString = None, **kwargs
    ) -> _NewMinecraftPacket:

        packet = object.__new__(cls)

        if data is None:

            packet.__init__(**kwargs)

        else:

            it = iter(data)
            packet_id = _iterutils.consume_varint(it)

            if packet_id != cls.ID:
                raise ValueError(
                    f"expected packet ID {cls.ID:#x}, got {packet_id:#x}"
                )

            if kwargs:
                raise NotImplementedError("cannot have both data and arguments")

            packet.__init__()
            packet.consume_payload(it)
            () = it

        return packet
