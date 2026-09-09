import pytest

from host.protocol import Command, Frame, ProtocolError, crc8, decode_frame, encode_frame, miso_enabled


def test_crc8_known_vector():
    assert crc8(b"123456789") == 0xF4


def test_command_frame_round_trip():
    encoded = encode_frame(Frame(Command.SET_THROTTLE, b"\x34\x12"))
    assert encoded[0] == 0xA5
    assert decode_frame(encoded) == Frame(Command.SET_THROTTLE, b"\x34\x12")


def test_bad_crc_is_rejected():
    encoded = bytearray(encode_frame(Frame(Command.ARM, b"")))
    encoded[-1] ^= 0x01
    with pytest.raises(ProtocolError, match="CRC"):
        decode_frame(bytes(encoded))


def test_truncated_payload_is_rejected():
    with pytest.raises(ProtocolError, match="length"):
        decode_frame(bytes((0xA5, Command.SET_CURRENT_LIMIT, 2, 0x10, 0x00)))


def test_miso_is_released_when_chip_select_is_inactive():
    assert miso_enabled(cs_low=True)
    assert not miso_enabled(cs_low=False)
