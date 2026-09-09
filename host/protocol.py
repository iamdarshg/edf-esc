"""Strict framing for the EDF-ESC SPI control interface."""

from dataclasses import dataclass
from enum import IntEnum

SYNC = 0xA5
MAX_PAYLOAD = 255


class ProtocolError(ValueError):
    """Raised when a wire frame is malformed."""


class Command(IntEnum):
    ARM = 0x01
    DISARM = 0x02
    EMERGENCY_STOP = 0x03
    SET_THROTTLE = 0x10
    SET_PWM_FREQUENCY = 0x11
    SET_CURRENT_LIMIT = 0x12
    SET_RAMP_RATE = 0x13
    SET_DIRECTION = 0x14
    READ_TELEMETRY = 0x20
    READ_FAULTS = 0x21
    READ_VERSION = 0x22


@dataclass(frozen=True)
class Frame:
    command: Command
    payload: bytes = b""


def crc8(data: bytes) -> int:
    """CRC-8/ATM (poly 0x07, init 0x00, no reflection)."""
    crc = 0
    for value in data:
        crc ^= value
        for _ in range(8):
            crc = ((crc << 1) ^ 0x07) & 0xFF if crc & 0x80 else (crc << 1) & 0xFF
    return crc


def encode_frame(frame: Frame) -> bytes:
    payload = bytes(frame.payload)
    if len(payload) > MAX_PAYLOAD:
        raise ProtocolError("payload length exceeds 255 bytes")
    body = bytes((SYNC, int(frame.command), len(payload))) + payload
    return body + bytes((crc8(body),))


def decode_frame(data: bytes) -> Frame:
    if len(data) < 4:
        raise ProtocolError("frame length is too short")
    if data[0] != SYNC:
        raise ProtocolError("invalid sync byte")
    expected = 4 + data[2]
    if len(data) != expected:
        raise ProtocolError(f"frame length is {len(data)}, expected {expected}")
    if crc8(data[:-1]) != data[-1]:
        raise ProtocolError("CRC mismatch")
    try:
        command = Command(data[1])
    except ValueError as exc:
        raise ProtocolError(f"unknown command 0x{data[1]:02x}") from exc
    return Frame(command, data[3:-1])


def miso_enabled(*, cs_low: bool) -> bool:
    """Reference rule for the platform driver: inactive slaves must be high-Z."""
    return cs_low
