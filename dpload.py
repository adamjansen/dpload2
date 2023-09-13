import binascii
import struct
import logging
import time

import can

from .protocol import (
    encode,
    decode,
    CMD_READ_BOOT_INFO,
    CMD_ERASE_FLASH,
    CMD_PROGRAM_FLASH,
    CMD_READ_CRC,
    CMD_JUMP_TO_APP,
    CMD_READ_OEM_INFO,
    CMD_READ_APP_INFO,
    IncompleteFrameError,
)

from .j1939 import (
    J1939,
    J1939_PGN_ECUID,
    J1939_PGN_SOFT,
)


class DPLoad:
    def __init__(self, bus, sa=39, da=208):
        self.log = logging.getLogger("dpload")
        self.bus = bus
        self.busname = bus.channel

        self.sa = sa
        self.da = da

        self.dm13_task = None

        self.j1939 = J1939(self.bus, sa=self.sa)

    def _flush_rx(self):
        while True:
            msg = self.bus.recv(0)
            if msg is None:
                return

    def ecu_info(self, da=255):
        self.bus.set_filters([])
        ecu_info = self.j1939.request_pgn(J1939_PGN_ECUID, da=da)
        self.log.info("Got ECU Info for %d: %s", da, ecu_info)
        return ecu_info

    def soft_info(self, da=255):
        self.bus.set_filters([])
        soft_info = self.j1939.request_pgn(J1939_PGN_SOFT, da=da)
        self.log.info("Got software version information for %d: %s", da, soft_info)
        return soft_info

    def enter(self, timeout=1.0, da=None):
        data = bytes.fromhex("0301040105090206")
        da = da or self.da
        tx_id = 0x18D60000 + (self.da << 8) + self.sa
        msg = can.Message(arbitration_id=tx_id, data=data)
        self.bus.send(msg)

    def scan(self, timeout=2.0):
        self.bus.set_filters(
            [{"can_id": 0x18EEFF00, "can_mask": 0x3FFFF00, "extended": True}]
        )

        data = bytes.fromhex("ffee00")
        tx_id = 0x18EAFF00 + self.sa
        msg = can.Message(arbitration_id=tx_id, data=data)
        self.bus.send(msg)
        self._flush_rx()
        expiry = time.time() + timeout
        cas = []
        while time.time() < expiry:
            msg = self.bus.recv(0.1)
            if msg is None or not msg.is_rx:
                continue

            sa = msg.arbitration_id & 0xFF
            name = msg.data
            cas.append((sa, name))

        return cas

    def _request(self, cmd, payload=None, timeout=1.0, da=None):
        if da is None:
            da = self.da

        tx_id = 0x18D60000 + (da << 8) + self.sa
        rx_id = 0x18D60000 + (self.sa << 8) + da
        self.bus.set_filters(
            [{"can_id": rx_id, "can_mask": 0x1FFFFFFF, "extended": True}]
        )
        self._flush_rx()
        txframe = encode(cmd, payload)

        self.log.debug(
            "TX [%#02x]=>[%#02x] %s",
            self.sa,
            da,
            binascii.hexlify(txframe).decode("utf-8"),
        )
        err_count = 0
        while len(txframe):
            part = txframe[:8]
            msg = can.Message(arbitration_id=tx_id, data=part)
            try:
                self.bus.send(msg)
            except can.CanOperationError as e:
                if err_count < 10 and e.error_code == 105:
                    time.sleep(0.002)
                    err_count += 1
                    continue
                else:
                    raise
            txframe = txframe[8:]

        rxframe = b""
        expiry = time.time() + timeout
        while time.time() < expiry:
            msg = self.bus.recv(0.001)
            if msg is None or not msg.is_rx:
                continue

            rxframe += msg.data

            try:
                response = decode(rxframe)
            except IncompleteFrameError:
                continue
            except ValueError as e:
                raise e

            self.log.debug(
                "RX [%#02x]=>[%#02x] %s",
                da,
                self.sa,
                binascii.hexlify(rxframe).decode("utf-8"),
            )
            response_cmd, payload = response[1], response[2:-3]

            if response_cmd != cmd:
                raise ValueError(
                    f"Expected command {cmd:#02x}, but received {response_cmd:#02x}"
                )

            return payload
        raise TimeoutError("Timeout waiting for response")

    def dm13_control(self, state, period=2.0):
        """Enable or disable DM13 broadcast"""
        if state and self.dm13_task is None:
            msg = can.Message(
                arbitration_id=0x18DFFF00 + self.sa,
                data=bytes.fromhex("00ffff0fffffffff"),
                is_extended_id=True,
            )

            self.dm13_task = self.bus.send_periodic(msg, period)
        if not state and self.dm13_task is not None:
            self.dm13_task.stop()
            self.dm13_task = None

    def program_flash(self, record, da=None, timeout=2.0):
        """write a raw intel hex record to flash"""
        self._request(CMD_PROGRAM_FLASH, record, da=da, timeout=timeout)
        return None

    def get_boot_info(self, da=None, timeout=0.1):
        payload = self._request(CMD_READ_BOOT_INFO, da=da, timeout=timeout)
        major, minor = struct.unpack("BB", payload)
        return major, minor

    def get_oem_info(self, da=None, timeout=0.1):
        payload = self._request(CMD_READ_OEM_INFO, da=da, timeout=timeout)
        sa, pn, vmajor, vminor = struct.unpack("B11sxxBB16x", payload)
        return sa, pn.decode("utf-8"), vmajor, vminor

    def get_app_info(self, da=None, timeout=0.1):
        payload = self._request(CMD_READ_APP_INFO, da=da, timeout=timeout)
        vmajor, vminor = struct.unpack("BB30x", payload)
        return vmajor, vminor

    def get_crc(self, da=None, timeout=0.1, start=0x9D007000, size=0x79000):
        self.log.debug("Getting CRC for %d bytes starting at %#08x", size, start)
        data = struct.pack("<LL2xLL", start, size, 0x00000000, 0x00000000)
        payload = self._request(CMD_READ_CRC, data, da=da, timeout=timeout)
        crc = struct.unpack("<H", payload)[0]
        return crc

    def erase(self, da=None, timeout=1.0):
        payload = struct.pack("<LL", 0xFFFFFFFF, 0xFFFFFFFF)
        payload = self._request(CMD_ERASE_FLASH, payload, da=da, timeout=timeout)
        return None

    def jump(self, da=None, timeout=2.0):
        return self._request(CMD_JUMP_TO_APP, da=da, timeout=timeout)
