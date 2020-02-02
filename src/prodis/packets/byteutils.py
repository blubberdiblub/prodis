#!/usr/bin/env python3


def render_varint(v: int) -> bytes:

    if 0 <= v <= 0x7f:
        return v.to_bytes(1, 'little')

    assert -0x80000000 <= v <= 0x7fffffff
    v &= 0xffffffff

    l = []

    while v >= 0x80:
        l.append(v & 0x7f | 0x80)
        v >>= 7

    return bytes(l + [v])


def render_string(s: str) -> bytes:

    b = s.encode()
    return render_varint(len(b)) + b


def render_identifier(namespace: str, name: str) -> bytes:

    if not namespace:
        namespace = 'minecraft'

    b = b'%b:%b' % (
        namespace.encode('ascii'),
        name.encode('ascii'),
    )
    return render_varint(len(b)) + b
