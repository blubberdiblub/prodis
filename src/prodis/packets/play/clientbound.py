#!/usr/bin/env python3

from __future__ import annotations

from collections.abc import (
    Iterator as _Iterator,
)

import json as _json
import math as _math

from itertools import islice as _islice

from uuid import UUID as _UUID

from ..packet import MinecraftPacketWithID as _MinecraftPacketWithID

from ...utils import byte as _byte
from ...utils import iter as _iter


class Packet(_MinecraftPacketWithID):

    pass


class SpawnLivingEntity(Packet):

    id = 0x2

    def __init__(
            self,
            entity_id: int,
            entity_uuid: _UUID | str,
            entity_type: int,
            x: float,
            y: float,
            z: float,
            yaw: float,
            pitch: float,
            head_pitch: float,
            velocity_x: float,
            velocity_y: float,
            velocity_z: float,
    ) -> None:

        if entity_uuid and not isinstance(entity_uuid, _UUID):
            entity_uuid = _UUID(entity_uuid)

        super().__init__()

        self.entity_id = entity_id
        self.entity_uuid = entity_uuid
        self.entity_type = entity_type
        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw
        self.pitch = pitch
        self.head_pitch = head_pitch
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.velocity_z = velocity_z

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            'entity_id',
            'entity_uuid',
            'entity_type',
            'x',
            'y',
            'z',
            'yaw',
            'pitch',
            'head_pitch',
            'velocity_x',
            'velocity_y',
            'velocity_z',
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        return b'%b%b%b%b%b%b%c%c%c%b%b%b' % (
            _byte.render_varint(self.entity_id),
            self.entity_uuid.bytes,
            _byte.render_varint(self.entity_type),
            _byte.render_double(self.x),
            _byte.render_double(self.y),
            _byte.render_double(self.z),
            round(self.yaw / 1.40625) & 0xff,
            round(self.pitch / 1.40625) & 0xff,
            round(self.head_pitch / 1.40625) & 0xff,
            round(self.velocity_x * 8000).to_bytes(2, 'big', signed=True),
            round(self.velocity_y * 8000).to_bytes(2, 'big', signed=True),
            round(self.velocity_z * 8000).to_bytes(2, 'big', signed=True),
        )

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        self.entity_id = _iter.consume_varint(it)
        self.entity_uuid = _UUID(bytes=bytes(_islice(it, 16)))
        self.entity_type = _iter.consume_varint(it)
        self.x = _iter.consume_double(it)
        self.y = _iter.consume_double(it)
        self.z = _iter.consume_double(it)
        self.yaw = next(it) * 1.40625
        self.pitch = next(it) * 1.40625
        self.head_pitch = next(it) * 1.40625
        self.velocity_x = int.from_bytes(_islice(it, 2), 'big', signed=True) / 8000
        self.velocity_y = int.from_bytes(_islice(it, 2), 'big', signed=True) / 8000
        self.velocity_z = int.from_bytes(_islice(it, 2), 'big', signed=True) / 8000
        () = it

        assert 0 <= self.entity_type <= 112
        assert _math.isfinite(self.x)
        assert _math.isfinite(self.y)
        assert _math.isfinite(self.z)


class ServerDifficulty(Packet):

    id = 0xe

    def __init__(self, difficulty: int = 2, locked: bool = True) -> None:

        super().__init__()

        self.difficulty = difficulty
        self.locked = locked

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            'difficulty',
            'locked',
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        return b'%c%c' % (
            self.difficulty,
            self.locked,
        )

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        self.difficulty = next(it)
        self.locked = bool(next(it))
        () = it

        assert 0 <= self.difficulty <= 3


class ChatMessage(Packet):

    id = 0xf

    def __init__(
            self,
            data: dict = None,
            position: int = 0,
            sender: _UUID = None,
    ) -> None:

        if sender and not isinstance(sender, _UUID):
            sender = _UUID(sender)

        super().__init__()

        self.data = data
        self.position = position
        self.sender = sender

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            'data',
            'position',
            'sender',
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        return b'%b%c%b' % (
            _byte.render_varstr(_json.dumps(self.data, separators=(',', ':'))),
            self.position,
            self.sender.bytes,
        )

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        self.data = _json.loads(_iter.consume_varstr(it))
        self.position = next(it)
        self.sender = _UUID(bytes=bytes(_islice(it, 16)))
        () = it

        assert 0 <= self.position <= 2


# TODO: complete
class DeclareCommands(Packet):

    id = 0x12

    def __init__(self, raw_tail: bytes) -> None:

        super().__init__()

        # ...
        self.raw_tail = raw_tail

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            # ...,
            'raw_tail',
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        return b'%b' % (
            # ...,
            self.raw_tail,
        )

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        # ...
        self.raw_tail = bytes(it)
        # () = it


# TODO: complete
class WindowItems(Packet):

    id = 0x14

    def __init__(self, window_id: int, state_id: int, raw_tail: bytes) -> None:

        super().__init__()

        self.window_id = window_id
        self.state_id = state_id
        # ...
        self.raw_tail = raw_tail

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            'window_id',
            'state_id',
            # ...,
            'raw_tail',
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        return b'%c%b%b' % (
            self.window_id,
            _byte.render_varint(self.state_id),
            # ...,
            self.raw_tail,
        )

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        self.window_id = next(it)
        self.state_id = _iter.consume_varint(it)
        # ...
        self.raw_tail = bytes(it)
        # () = it


class PluginMessage(Packet):

    id = 0x18

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


class EntityTrigger(Packet):

    id = 0x1b

    def __init__(self, entity_id: int, trigger: int) -> None:

        super().__init__()

        self.entity_id = entity_id
        self.trigger = trigger

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            'entity_id',
            'trigger',
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        return b'%b%c' % (
            self.entity_id.to_bytes(4, 'big'),
            self.trigger,
        )

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        self.entity_id = int.from_bytes(_islice(it, 4), 'big')
        self.trigger = next(it)
        () = it

        assert 0 <= self.trigger <= 60


class InitializeWorldBorder(Packet):

    id = 0x20

    def __init__(
            self,
            x: float,
            z: float,
            old_diameter: float,
            new_diameter: float,
            speed: float,
            portal_teleport_boundary: int,
            warning_blocks: int,
            warning_time: int,
    ) -> None:

        super().__init__()

        self.x = x
        self.z = z
        self.old_diameter = old_diameter
        self.new_diameter = new_diameter
        self.speed = speed
        self.portal_teleport_boundary = portal_teleport_boundary
        self.warning_blocks = warning_blocks
        self.warning_time = warning_time

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            'x',
            'z',
            'old_diameter',
            'new_diameter',
            'speed',
            'portal_teleport_boundary',
            'warning_blocks',
            'warning_time',
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        return b'%b%b%b%b%b%b%b%b' % (
            _byte.render_double(self.x),
            _byte.render_double(self.z),
            _byte.render_double(self.old_diameter),
            _byte.render_double(self.new_diameter),
            _byte.render_varlong(round(self.speed * 1000)),
            _byte.render_varint(self.portal_teleport_boundary),
            _byte.render_varint(self.warning_blocks),
            _byte.render_varint(self.warning_time),
        )

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        self.x = _iter.consume_double(it)
        self.z = _iter.consume_double(it)
        self.old_diameter = _iter.consume_double(it)
        self.new_diameter = _iter.consume_double(it)
        self.speed = _iter.consume_varlong(it) / 1000
        self.portal_teleport_boundary = _iter.consume_varint(it)
        self.warning_blocks = _iter.consume_varint(it)
        self.warning_time = _iter.consume_varint(it)
        () = it

        assert _math.isfinite(self.x)
        assert _math.isfinite(self.z)
        assert _math.isfinite(self.old_diameter) and self.old_diameter > 0
        assert _math.isfinite(self.new_diameter) and self.new_diameter > 0


# TODO: complete
class ChunkData(Packet):

    id = 0x22

    def __init__(
            self,
            chunk_x: int,
            chunk_z: int,
            # ...,
            raw_tail: bytes,
    ) -> None:

        super().__init__()

        self.chunk_x = chunk_x
        self.chunk_z = chunk_z
        # ...
        self.raw_tail = raw_tail

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            'chunk_x',
            'chunk_z',
            # ...,
            'raw_tail',
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        return b'%b%b%b' % (
            self.chunk_x.to_bytes(4, 'big', signed=True),
            self.chunk_z.to_bytes(4, 'big', signed=True),
            # ...,
            self.raw_tail,
        )

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        self.chunk_x = int.from_bytes(_islice(it, 4), 'big', signed=True)
        self.chunk_z = int.from_bytes(_islice(it, 4), 'big', signed=True)
        # ...
        self.raw_tail = bytes(it)
        # () = it


# TODO: complete
class UpdateLight(Packet):

    id = 0x25

    def __init__(
            self,
            chunk_x: int,
            chunk_z: int,
            trust_edges: bool,
            # ...,
            raw_tail: bytes,
    ) -> None:

        super().__init__()

        self.chunk_x = chunk_x
        self.chunk_z = chunk_z
        self.trust_edges = trust_edges
        # ...
        self.raw_tail = raw_tail

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            'chunk_x',
            'chunk_z',
            'trust_edges',
            # ...,
            'raw_tail',
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        return b'%b%b%c%b' % (
            _byte.render_varint(self.chunk_x),
            _byte.render_varint(self.chunk_z),
            self.trust_edges,
            # ...,
            self.raw_tail,
        )

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        self.chunk_x = _iter.consume_varint(it)
        self.chunk_z = _iter.consume_varint(it)
        self.trust_edges = bool(next(it))
        # ...
        self.raw_tail = bytes(it)
        # () = it


# TODO: complete
class JoinGame(Packet):

    id = 0x26

    def __init__(
            self,
            entity_id: int,
            hardcore: bool,
            gamemode: int,
            previous_gamemode: int,
            # dimension: int,
            # hashed_seed: int,
            # max_players: int = 20,
            # level_type: str = 'default',
            # view_distance: int = 10,
            # reduced_debug_info: bool = False,
            # enable_respawn_screen: bool = True,
            raw_tail: bytes,
    ) -> None:

        super().__init__()

        self.entity_id = entity_id
        self.hardcore = hardcore
        self.gamemode = gamemode
        self.previous_gamemode = previous_gamemode
        # self.dimension = dimension
        # self.hashed_seed = hashed_seed
        # self.max_players = max_players
        # self.level_type = level_type
        # self.view_distance = view_distance
        # self.reduced_debug_info = reduced_debug_info
        # self.enable_respawn_screen = enable_respawn_screen
        self.raw_tail = raw_tail

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            'entity_id',
            'hardcore',
            'gamemode',
            'previous_gamemode',
            # 'dimension',
            # 'hashed_seed',
            # 'max_players',
            # 'level_type',
            # 'view_distance',
            # 'reduced_debug_info',
            # 'enable_respawn_screen',
            'raw_tail',
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        return b'%b%c%c%c%b' % (
            self.entity_id.to_bytes(4, 'big', signed=True),
            self.hardcore,
            self.gamemode,
            self.previous_gamemode & 0xff,
            # self.dimension.to_bytes(4, 'big', signed=True),
            # self.hashed_seed.to_bytes(8, 'big', signed=True),
            # self.max_players,
            # _byte.render_varstr(self.level_type),
            # _byte.render_varint(self.view_distance),
            # self.reduced_debug_info,
            # self.enable_respawn_screen,
            self.raw_tail,
        )

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        self.entity_id = int.from_bytes(_islice(it, 4), 'big', signed=True)
        self.hardcore = bool(next(it))
        self.gamemode = next(it)
        self.previous_gamemode = (next(it) ^ 0x80) - 0x80
        # self.dimension = int.from_bytes(_islice(it, 4), 'big', signed=True)
        # self.hashed_seed = int.from_bytes(_islice(it, 8), 'big', signed=True)
        # self.max_players = next(it)
        # self.level_type = _iter.consume_varstr(it)
        # self.view_distance = _iter.consume_varint(it)
        # self.reduced_debug_info = bool(next(it))
        # self.enable_respawn_screen = bool(next(it))
        self.raw_tail = bytes(it)
        # () = it

        assert self.entity_id != 0
        assert 0 <= self.gamemode <= 3
        assert -1 <= self.previous_gamemode <= 3
        # assert -1 <= self.dimension <= 1
        # assert self.max_players > 0
        # assert self.level_type in [
        #     'default',
        #     'flat',
        #     'largeBiomes',
        #     'amplified',
        #     'customized',
        #     'buffet',
        #     'default_1_1',
        # ]
        # assert 2 <= self.view_distance <= 32


class PlayerAbilities(Packet):

    id = 0x32

    def __init__(
            self,
            flags: int = 0,
            flying_speed: float = 0.05,
            fov_modifier: float = 0.1,
    ) -> None:

        super().__init__()

        self.flags = flags
        self.flying_speed = flying_speed
        self.fov_modifier = fov_modifier

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            'flags',
            'flying_speed',
            'fov_modifier',
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        return b'%c%b%b' % (
            self.flags,
            _byte.render_float(self.flying_speed),
            _byte.render_float(self.fov_modifier),
        )

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        self.flags = next(it)
        self.flying_speed = _iter.consume_float(it)
        self.fov_modifier = _iter.consume_float(it)
        () = it

        assert not (self.flags & ~0xf)
        assert _math.isfinite(self.flying_speed) and self.flying_speed >= 0
        assert _math.isfinite(self.fov_modifier) and self.fov_modifier >= 0


class PlayerInfo(Packet):

    id = 0x36

    def __init__(
            self,
            action: int = 0,
            updates: dict[_UUID, dict[str, int | str | dict] | None] = None,
    ) -> None:

        super().__init__()

        self.action = action
        self.updates = updates

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            'action',
            'updates',
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        payload = _byte.render_varint(self.action)

        payload += _byte.render_varint(len(self.updates))
        for uuid, update in self.updates.items():
            payload += uuid.bytes

            if self.action == 0:
                payload += _byte.render_varstr(update['name'])

                properties = update['properties']
                payload += _byte.render_varint(len(properties))
                for name, (value, signature) in properties.items():
                    payload += _byte.render_varstr(name)
                    payload += _byte.render_varstr(value)
                    payload += (b'\x00' if signature is None else
                                b'\x01' + _byte.render_varstr(signature))

            if self.action in (0, 1):
                payload += _byte.render_varint(update['gamemode'])

            if self.action in (0, 2):
                payload += _byte.render_varint(update['ping'])

            if self.action in (0, 3):
                display_name = update['display_name']
                payload += (b'\x00' if display_name is None else
                            b'\x01' + _byte.render_varstr(display_name))

        return payload

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        self.action = _iter.consume_varint(it)
        assert 0 <= self.action <= 4

        self.updates = {}
        for _ in range(_iter.consume_varint(it)):
            uuid = _UUID(bytes=bytes(_islice(it, 16)))
            if self.action == 4:
                self.updates[uuid] = None
                continue

            update = self.updates[uuid] = {}

            if self.action == 0:
                update['name'] = _iter.consume_varstr(it)
                properties = update['properties'] = {}
                for __ in range(_iter.consume_varint(it)):
                    name = _iter.consume_varstr(it)
                    value = _iter.consume_varstr(it)
                    signature = _iter.consume_varstr(it) if next(it) else None
                    properties[name] = (value, signature)
                update['properties'] = properties

            if self.action in (0, 1):
                update['gamemode'] = _iter.consume_varint(it)

            if self.action in (0, 2):
                update['ping'] = _iter.consume_varint(it)

            if self.action in (0, 3):
                update['display_name'] = (_iter.consume_varstr(it)
                                          if next(it) else None)
        () = it


class PlayerPositionAndLook(Packet):

    id = 0x38

    def __init__(
            self,
            x: float = 0.0,
            y: float = 0.0,
            z: float = 0.0,
            yaw: float = 0.0,
            pitch: float = 0.0,
            flags: int = 0,
            teleport_id: int = 0,
            dismount_vehicle: bool = False,
    ) -> None:

        super().__init__()

        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw
        self.pitch = pitch
        self.flags = flags
        self.teleport_id = teleport_id
        self.dismount_vehicle = dismount_vehicle

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            'x',
            'y',
            'z',
            'yaw',
            'pitch',
            'flags',
            'teleport_id',
            'dismount_vehicle',
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        return b'%b%b%b%b%b%c%b%c' % (
            _byte.render_double(self.x),
            _byte.render_double(self.y),
            _byte.render_double(self.z),
            _byte.render_float(self.yaw),
            _byte.render_float(self.pitch),
            self.flags,
            _byte.render_varint(self.teleport_id),
            self.dismount_vehicle,
        )

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        self.x = _iter.consume_double(it)
        self.y = _iter.consume_double(it)
        self.z = _iter.consume_double(it)
        self.yaw = _iter.consume_float(it)
        self.pitch = _iter.consume_float(it)
        self.flags = next(it)
        self.teleport_id = _iter.consume_varint(it)
        self.dismount_vehicle = bool(next(it))
        () = it

        assert _math.isfinite(self.x)
        assert _math.isfinite(self.y)
        assert _math.isfinite(self.z)
        assert _math.isfinite(self.yaw)
        assert _math.isfinite(self.pitch)
        assert not (self.flags & ~0x1f)


class EntityHeadLook(Packet):

    id = 0x3e

    def __init__(self, entity_id: int, head_yaw: float) -> None:

        super().__init__()

        self.entity_id = entity_id
        self.head_yaw = head_yaw

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            'entity_id',
            'head_yaw',
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        return b'%b%c' % (
            _byte.render_varint(self.entity_id),
            round(self.head_yaw / 1.40625) & 0xff,
        )

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        self.entity_id = _iter.consume_varint(it)
        self.head_yaw = next(it) * 1.40625
        () = it


class HeldItemChange(Packet):

    id = 0x48

    def __init__(self, slot: int = 0) -> None:

        super().__init__()

        self.slot = slot

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            'slot',
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        return b'%c' % (
            self.slot,
        )

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        self.slot = next(it)
        () = it

        assert 0 <= self.slot <= 8


class UpdateViewPosition(Packet):

    id = 0x49

    def __init__(self, chunk_x: int, chunk_z: int) -> None:

        super().__init__()

        self.chunk_x = chunk_x
        self.chunk_z = chunk_z

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            'chunk_x',
            'chunk_z',
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        return b'%b%b' % (
            _byte.render_varint(self.chunk_x),
            _byte.render_varint(self.chunk_z),
        )

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        self.chunk_x = _iter.consume_varint(it)
        self.chunk_z = _iter.consume_varint(it)
        () = it


class SpawnPosition(Packet):

    id = 0x4b

    def __init__(self, x: int, y: int, z: int, angle: float) -> None:

        super().__init__()

        self.x = x
        self.y = y
        self.z = z
        self.angle = angle

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            'x',
            'y',
            'z',
            'angle',
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        location = (
                (self.x & 0x3_fff_fff) << 38 |
                (self.z & 0x3_fff_fff) << 12 |
                (self.y & 0xfff)
        )

        return b'%b%b' % (
            location.to_bytes(8, 'big'),
            _byte.render_float(self.angle),
        )

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        location = int.from_bytes(_islice(it, 8), 'big', signed=True)

        self.y = location | -0x800 if location & 0x800 else location & 0x7ff

        location >>= 12
        self.z = (location | -0x2_000_000 if location & 0x2_000_000
                  else location & 0x1_fff_fff)

        self.x = location >> 26

        self.angle = _iter.consume_float(it)
        () = it


# TODO: complete
class EntityMetadata(Packet):

    id = 0x4d

    def __init__(self, entity_id: int, metadata: bytes | bytearray) -> None:

        super().__init__()

        self.entity_id = entity_id
        self.metadata = metadata
        # ...

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            'entity_id',
            'metadata',
            # ...,
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        return b'%b%b' % (
            _byte.render_varint(self.entity_id),
            self.metadata,
        )

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        self.entity_id = _iter.consume_varint(it)
        self.metadata = bytes(it)
        # ...
        # () = it


# TODO: complete
class EntityEquipment(Packet):

    id = 0x50

    def __init__(self, entity_id: int, equipment: bytes | bytearray) -> None:

        super().__init__()

        self.entity_id = entity_id
        self.equipment = equipment
        # ...

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            'entity_id',
            'equipment',
            # ...,
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        return b'%b%b' % (
            _byte.render_varint(self.entity_id),
            self.equipment,
        )

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        self.entity_id = _iter.consume_varint(it)
        self.equipment = bytes(it)
        # ...
        # () = it


class TimeUpdate(Packet):

    id = 0x59

    def __init__(self, world_age: int = 0, time_of_day: int = 0) -> None:

        super().__init__()

        self.world_age = world_age
        self.time_of_day = time_of_day

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            'world_age',
            'time_of_day',
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        return b'%b%b' % (
            self.world_age.to_bytes(8, 'big', signed=True),
            self.time_of_day.to_bytes(8, 'big', signed=True),
        )

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        self.world_age = int.from_bytes(_islice(it, 8), 'big', signed=True)
        self.time_of_day = int.from_bytes(_islice(it, 8), 'big', signed=True)
        () = it

        assert self.world_age >= 0


# TODO: complete
class EntityProperties(Packet):

    id = 0x64

    def __init__(self, entity_id: int, raw_tail: bytes | bytearray) -> None:

        super().__init__()

        self.entity_id = entity_id
        # ...
        self.raw_tail = raw_tail

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            'entity_id',
            # ...,
            'raw_tail',
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        return b'%b%b' % (
            _byte.render_varint(self.entity_id),
            # ...,
            self.raw_tail,
        )

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        self.entity_id = _iter.consume_varint(it)
        # ...
        self.raw_tail = bytes(it)
        # () = it


# TODO: complete
class DeclareRecipes(Packet):

    id = 0x66

    def __init__(self, raw_tail: bytes) -> None:

        super().__init__()

        # ...
        self.raw_tail = raw_tail

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            # ...,
            'raw_tail',
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        return b'%b' % (
            # ...,
            self.raw_tail,
        )

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        # ...
        self.raw_tail = bytes(it)
        # () = it


# TODO: complete
class Tags(Packet):

    id = 0x67

    def __init__(self, raw_tail: bytes) -> None:

        super().__init__()

        # ...
        self.raw_tail = raw_tail

    def __getstate__(self) -> dict[str, object]:

        return {key: getattr(self, key) for key in [
            # ...,
            'raw_tail',
        ]}

    @property
    def payload(self) -> bytes | bytearray:

        return b'%b' % (
            # ...,
            self.raw_tail,
        )

    @payload.setter
    def payload(self, it: bytes | bytearray | _Iterator[int]) -> None:

        it = iter(it)
        # ...
        self.raw_tail = bytes(it)
        # () = it
