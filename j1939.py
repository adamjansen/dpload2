import time
import sys
import struct

import can

J1939_TP_CM_RTS = 16
J1939_TP_CM_CTS = 17
J1939_TP_CM_EOM_ACK = 19
J1939_TP_CM_BAM = 32
J1939_TP_CM_ABORT = 255

J1939_PF_TP_CM = 236
J1939_PF_TP_DT = 235
J1939_PF_ACKNOWLEDGE = 232
J1939_PF_REQUEST = 234
J1939_PF_ADDRESS_CLAIMED = 238
J1939_PF_PROPRIETARY_A = 239
J1939_PF_PROPRIETARY_B = 255
J1939_PF_START_STOP_BROADCAST = J1939_PF_DM13 = 223
J1939_PF_MEMORY_ACCESS_REQUEST = J1939_PF_DM14 = 217
J1939_PF_MEMORY_ACCESS_RESPONSE = J1939_PF_DM15 = 216
J1939_PF_BINARY_DATA_TRANSFER = J1939_PF_DM16 = 215
J1939_PF_BOOT_LOAD_DATA = J1939_PF_DM17 = 214
J1939_PF_DATA_SECURITY = J1939_PF_DM18 = 212

J1939_PF_AUXIO7 = 156
J1939_PF_AUXIO6 = 157

J1939_PGN_SOFT = 65242
J1939_PGN_ECUID = 64965
J1939_PGN_EH = 65201
J1939_PGN_DM1 = 65226
J1939_PGN_DM2 = 65227
J1939_PGN_DM3 = 65228

J1939_TP_MAX_BYTES = 255*7

J1939_ADDR_GLOBAL = 255

J1939_DEFAULT_PRIORITY = 6


def pgn_from_id(can_id):
    return (can_id & 0x00FFFF00) >> 8

def pf_from_id(can_id):
    return (can_id & 0x00FF0000) >> 16

def build_id(pgn, sa, pri=J1939_DEFAULT_PRIORITY):
    return ((pri & 0x7) << 26) | ((pgn & 0xFFFFFF) << 8) | (sa & 0xFF)


class J1939:
    def __init__(self, bus, sa=0x27):
        self.bus = bus
        self.sa = sa

    def send_pf_to(self, pf, data, da=J1939_ADDR_GLOBAL, sa=None, pri=J1939_DEFAULT_PRIORITY):
        pgn = (pf << 8) + da
        return self.send_pgn(pgn, data, sa=sa, pri=pri)

    def send_pgn(self, pgn, data, sa=None, pri=J1939_DEFAULT_PRIORITY):
        msg = can.Message(arbitration_id=build_id(pgn, sa or self.sa, pri=pri), data=data, is_extended_id=True)
        self.bus.send(msg)

    def request_pgn(self, pgn, da=J1939_ADDR_GLOBAL, pri=J1939_DEFAULT_PRIORITY, timeout=1.0):
        buffer = bytearray(J1939_TP_MAX_BYTES)
        packets_remaining = set()
        total_bytes = 0
        total_packets = 0
        pgn_bytes = pgn.to_bytes(length=3, byteorder='little', signed=False)
        self.send_pf_to(J1939_PF_REQUEST, data=pgn_bytes, da=da, pri=pri)

        expiry = time.time() + timeout
        while time.time() < expiry:
            msg = self.bus.recv(0.05)
            if msg is None:
                continue
            if pgn_from_id(msg.arbitration_id) == pgn:
                total_bytes = len(msg.data)
                buffer = msg.data
                break
            elif pf_from_id(msg.arbitration_id) == J1939_PF_TP_CM:
                expiry += 1.25
                if msg.data[0] == J1939_TP_CM_RTS:
                    total_bytes, total_packets, max_chunk, rts_pgn_bytes  = struct.unpack_from('<HBB3s', msg.data, 1)
                    if rts_pgn_bytes != pgn_bytes:
                        raise ValueError()

                    packets_remaining = set(range(1, total_packets+1))
                    cts = struct.pack('<BBBH3s', J1939_TP_CM_CTS, 16, 1, 0xFFFF, pgn_bytes)
                    self.send_pf_to(J1939_PF_TP_CM, da=da, data=cts)
            elif pf_from_id(msg.arbitration_id) == J1939_PF_TP_DT:
                seq = msg.data[0]
                offset = (seq - 1) * 7
                struct.pack_into('<7s', buffer, offset, msg.data[1:])
                packets_remaining.remove(seq)

                expiry += 0.2

                if len(packets_remaining) == 0:
                    buffer = buffer[:total_bytes]

                    # Send EOM ACK
                    eom_ack = struct.pack('<BHBB3s', J1939_TP_CM_EOM_ACK, total_bytes, total_packets, 0xFF, pgn_bytes )
                    self.send_pf_to(J1939_PF_TP_CM, da=da, data=eom_ack)
                    break

        if len(packets_remaining) != 0:
            raise TimeoutError("Timeout waiting for data")

        try:
            text = buffer.decode('utf-8')
        except UnicodeDecodeError:
            text = buffer.hex(sep=' ')

        return text