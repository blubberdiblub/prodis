#!/usr/bin/env python3

from __future__ import annotations

from typing import (
    ByteString as _ByteString,
    Iterator as _Iterator,
    Union as _Union,
)

from itertools import islice as _islice

from uuid import UUID as _UUID

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


class JoinGame(_VerifiedPacket):

    ID = 0x26

    def __init__(
            self,
            entity_id: int,
            game_mode: int,
            dimension: int,
            hashed_seed: int,
            max_players: int = 20,
            level_type: str = 'default',
            view_distance: int = 10,
            reduced_debug_info: bool = False,
            enable_respawn_screen: bool = True,
    ) -> None:

        super().__init__()

        self.entity_id = entity_id
        self.game_mode = game_mode
        self.dimension = dimension
        self.hashed_seed = hashed_seed
        self.max_players = max_players
        self.level_type = level_type
        self.view_distance = view_distance
        self.reduced_debug_info = reduced_debug_info
        self.enable_respawn_screen = enable_respawn_screen

    def _fmt_args(self) -> str:

        return ', '.join([
            f'entity_id={self.entity_id!r}',
            f'game_mode={self.game_mode!r}',
            f'dimension={self.dimension!r}',
            f'hashed_seed={self.hashed_seed!r}',
            f'max_players={self.max_players!r}',
            f'level_type={self.level_type!r}',
            f'view_distance={self.view_distance!r}',
            f'reduced_debug_info={self.reduced_debug_info!r}',
            f'enable_respawn_screen={self.enable_respawn_screen!r}',
        ])

    def consume_payload(self, it: _Union[_ByteString, _Iterator[int]]) -> None:

        it = iter(it)
        self.entity_id = int.from_bytes(_islice(it, 4), 'big', signed=True)
        self.game_mode = next(it)
        self.dimension = int.from_bytes(_islice(it, 4), 'big', signed=True)
        self.hashed_seed = int.from_bytes(_islice(it, 8), 'big', signed=True)
        self.max_players = next(it)
        self.level_type = _iterutils.consume_string(it)
        self.view_distance = _iterutils.consume_varint(it)
        self.reduced_debug_info = bool(next(it))
        self.enable_respawn_screen = bool(next(it))
        () = it

        assert self.entity_id != 0
        assert 0 <= self.game_mode <= 0xf
        assert -1 <= self.dimension <= 1
        assert self.max_players > 0
        assert self.level_type in [
            'default',
            'flat',
            'largeBiomes',
            'amplified',
            'customized',
            'buffet',
            'default_1_1',
        ]
        assert 2 <= self.view_distance <= 32

    def render_payload(self) -> _ByteString:

        return b'%b%c%b%b%c%b%b%c%c' % (
            self.entity_id.to_bytes(4, 'big', signed=True),
            self.game_mode,
            self.dimension.to_bytes(4, 'big', signed=True),
            self.hashed_seed.to_bytes(8, 'big', signed=True),
            self.max_players,
            _byteutils.render_string(self.level_type),
            _byteutils.render_varint(self.view_distance),
            self.reduced_debug_info,
            self.enable_respawn_screen,
        )


# TODO: complete
class ChunkData(_VerifiedPacket):

    ID = 0x22

    def __init__(
            self,
            chunk_x: int = None,
            chunk_z: int = None,
            full_chunk: bool = True,
            primary_bit_mask: int = 0,
            motion_blocking=None,
            world_surface=None,
            # ...,
    ) -> None:

        super().__init__()

        self.chunk_x = chunk_x
        self.chunk_z = chunk_z
        self.full_chunk = full_chunk
        self.primary_bit_mask = primary_bit_mask
        self.motion_blocking = motion_blocking
        self.world_surface = world_surface

    def _fmt_args(self) -> str:

        return ', '.join([
            f'chunk_x={self.chunk_x!r}',
            f'chunk_z={self.chunk_z!r}',
            f'full_chunk={self.full_chunk!r}',
            f'primary_bit_mask={self.primary_bit_mask!r}',
            f'motion_blocking={self.motion_blocking!r}',
            f'world_surface={self.world_surface!r}',
        ])

    def consume_payload(self, it: _Union[_ByteString, _Iterator[int]]) -> None:

        it = iter(it)
        () = it

    def render_payload(self) -> _ByteString:

        return b''


Packet.packet_types = {
    JoinGame.ID: JoinGame,
    ChunkData.ID: ChunkData,
}
