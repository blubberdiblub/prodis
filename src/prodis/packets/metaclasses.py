#!/usr/bin/env python3

from __future__ import annotations

from typing import ByteString as _ByteString

from .packet import NewMinecraftPacket as _NewMinecraftPacket

from . import iterutils as _iterutils


class IDDispatcher(type):

    def __call__(cls, data: _ByteString) -> _NewMinecraftPacket:

        if not isinstance(data, _ByteString):
            raise TypeError("data must be bytes-like")

        it = iter(data)
        packet_id = _iterutils.consume_varint(it)

        try:
            dispatched = cls.packet_types[packet_id]
        except KeyError:
            raise ValueError("unknown packet ID") from None

        packet = object.__new__(dispatched)
        # cls.__init__(packet, data)
        packet.__init__()
        packet.consume_payload(it)
        return packet


class IDVerifier(IDDispatcher):

    def __call__(cls, **kwargs) -> _NewMinecraftPacket:

        packet = object.__new__(cls)
        packet.__init__(**kwargs)
        # if data is None:
        #     packet.__init__(**kwargs)
        # elif not kwargs:
        #     super(cls, packet).__init__(data)
        #     packet.parse_data()
        # else:
        #     packet.__init__(data=data, **kwargs)
        return packet
