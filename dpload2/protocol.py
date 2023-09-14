import io
import struct

SOH = b"\x01"
EOT = b"\x04"
DLE = b"\x10"

CMD_READ_BOOT_INFO = 1
CMD_ERASE_FLASH = 2
CMD_PROGRAM_FLASH = 3
CMD_READ_CRC = 4
CMD_JUMP_TO_APP = 5
CMD_READ_OEM_INFO = 6
CMD_READ_APP_INFO = 7


class IncompleteFrameError(Exception):
    pass


class InvalidFrameError(Exception):
    pass


class CrcMismatchError(Exception):
    pass


def crc16(data, start=0x0000):
    crc = start
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            if (crc & 0x8000) > 0:
                crc = (crc << 1) ^ 0x1021
            else:
                crc = crc << 1
    return crc & 0xFFFF


def escape(b):
    if b in (SOH, EOT, DLE):
        return bytes(DLE + b)
    return b


def decode(frame):
    if not frame.startswith(SOH):
        raise InvalidFrameError("Does not start with SOH")
    if not frame.endswith(EOT):
        raise IncompleteFrameError("Does not end with EOT")

    frame = frame.replace(b"\x10\x01", SOH)
    frame = frame.replace(b"\x10\x04", EOT)
    frame = frame.replace(b"\x10\x10", DLE)

    payload = frame[1:-3]
    try:
        crc_rx = frame[-3] + (frame[-2] << 8)
    except IndexError:
        raise IncompleteFrameError("missing CRC")

    crc = crc16(payload)
    if crc_rx != crc:
        raise CrcMismatchError(
            f"Checksum failure: Expected {crc_rx:#06x}, but got {crc:#06x} {frame.hex()}"
        )
    return frame


def encode(cmd, payload=None):
    buf = io.BytesIO()
    buf.write(SOH)

    if isinstance(cmd, int):
        cmd = bytes([cmd])

    buf.write(escape(cmd))

    crc = crc16(cmd)
    if payload is not None:
        crc = crc16(payload, start=crc)
        for b in payload:
            buf.write(escape(bytes([b])))

    h, l = (crc >> 8), (crc & 0xFF)

    buf.write(escape(bytes([l])))
    buf.write(escape(bytes([h])))
    buf.write(EOT)
    return buf.getvalue()
