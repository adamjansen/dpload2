import hashlib
from enum import Enum
import struct
from intelhex import IntelHex, NotEnoughDataError
import io


class InvalidImageError(Exception):
    pass


TLV_INFO_MAGIC = 0x6907
TLV_PROT_INFO_MAGIC = 0x6908
TLV_INFO_SIZE = 4
IMAGE_MAGIC = 0x96F3B83D
HEADER_FORMAT = "IIHHIIBBHI"
BOOT_MAGIC = bytes.fromhex("77c295f360d2ef7f3552500f2cb67980")
BOOT_MAGIC_SIZE = len(BOOT_MAGIC)


class ImageTlvType(Enum):
    KEYHASH = 0x01
    PUBKEY = 0x02
    SHA256 = 0x10
    RSA2048_PSS = 0x20
    ECDSA224 = 0x21
    ECDSA_SIG = 0x22
    RSA3072 = 0x23
    ED25519 = 0x24
    ENC_RSA2048 = 0x30
    ENC_KW = 0x31
    ENC_EC256 = 0x32
    ENC_X25519 = 0x33
    DEPENDENCY = 0x40
    SEC_CNT = 0x50
    BOOT_RECORD = 0x60

    # Vendor-reserved TLVs are xxA0-xxAF

    DP_SW_PART_NUMBER = 0xDDA0
    DP_HW_PART_NUMBER = 0xDDA1


TLV_PROCESSORS = {
    ImageTlvType.SHA256: bytes.hex,
    ImageTlvType.DP_SW_PART_NUMBER: lambda s: s.decode("utf-8"),
    ImageTlvType.DP_HW_PART_NUMBER: lambda s: s.decode("utf-8"),
    ImageTlvType.SEC_CNT: lambda v: int.from_bytes(v, 'little'),
}


class Image:
    def __init__(self, path=None):
        self.ver_major = None
        self.ver_minor = None
        self.ver_patch = None
        self.ver_tweak = None
        self.ihex = IntelHex()
        self.load_address = 0
        self.header_size = 0
        self.image_size = 0
        self.protected_tlv_size = 0
        self.protected_tlvs = []
        self.tlvs = []
        self._filename = path or ""
        if path is not None:
            self.load(path)

    @property
    def filename(self):
        return self._filename

    def load(self, path):
        """Load an image from a file"""
        self.ihex = IntelHex()
        format = "hex" if path.lower().endswith(".hex") else "bin"
        self.ihex.fromfile(path, format)
        self._filename = path

        header = self.ihex.gets(self.ihex.minaddr(), 28)

        (
            magic,
            self.load_address,
            self.header_size,
            self.protected_tlv_size,
            self.image_size,
            flags,
            self.ver_major,
            self.ver_minor,
            self.ver_patch,
            self.ver_tweak,
        ) = struct.unpack_from("IIHHIIBBHI", header, 0)
        if magic != IMAGE_MAGIC:
            raise InvalidImageError(f"Incorrect magic value 0x{magic:08x}")

        tlv_offset = self.ihex.minaddr() + self.header_size + self.image_size
        if self.protected_tlv_size > 0:
            tlv_magic, tlv_total = struct.unpack(
                "HH", self.ihex.gets(tlv_offset, TLV_INFO_SIZE)
            )
            if tlv_magic != TLV_PROT_INFO_MAGIC:
                raise InvalidImageError(
                    f"Invalid magic for protected TLV at offset {tlv_offset}"
                )
            tlv_end = tlv_offset + tlv_total
            tlv_offset += TLV_INFO_SIZE

            self.protected_tlvs = []
            while tlv_offset < tlv_end:
                tlv_type, tlv_length = struct.unpack_from(
                    "HH", self.ihex.gets(tlv_offset, TLV_INFO_SIZE)
                )
                tlv_offset += TLV_INFO_SIZE
                tlv_data = self.ihex.gets(tlv_offset, tlv_length)
                tlv_offset += tlv_length
                self.protected_tlvs.append((tlv_type, tlv_length, tlv_data))

        tlv_magic, tlv_total = struct.unpack(
            "HH", self.ihex.gets(tlv_offset, TLV_INFO_SIZE)
        )
        if tlv_magic != TLV_INFO_MAGIC:
            raise InvalidImageError(f"Invalid magic for TLV at offset {tlv_offset}")
        tlv_end = tlv_offset + tlv_total

        tlv_offset += TLV_INFO_SIZE

        sha256sum = None
        self.tlvs = []
        while tlv_offset < tlv_end:
            tlv_type, tlv_length = struct.unpack(
                "HH", self.ihex.gets(tlv_offset, TLV_INFO_SIZE)
            )
            tlv_offset += TLV_INFO_SIZE
            tlv_data = self.ihex.gets(tlv_offset, tlv_length)
            tlv_offset += tlv_length
            if tlv_type == ImageTlvType.SHA256.value:
                sha256sum = tlv_data
            self.tlvs.append((tlv_type, tlv_length, tlv_data))

        padding_size = self.ihex.maxaddr() - tlv_end
        trailer_offset = self.ihex.maxaddr() - BOOT_MAGIC_SIZE
        if padding_size > 0:
            max_align = None
            # Parse image trailer
            trailer_magic = self.ihex.gets(trailer_offset)
            if trailer_magic == BOOT_MAGIC:
                max_align = 8
            elif trailer_magic.endswith(BOOT_MAGIC_2):
                max_align = int(trailer_magic[:2], 0)
            else:
                raise InvalidImageError("Invalid trailer magic")
            if max_align is not None:
                if max_align > BOOT_MAGIC_SIZE:
                    trailer_offset -= max_align - BOOT_MAGIC_SIZE
                trailer_offset -= max_align
                image_ok = self.ihex.gets(trailer_offset, 1)
                trailer_offset -= max_align
                copy_done = self.ihex.gets(trailer_offset, 1)
                trailer_offset -= max_align
                swap_info = self.ihex.gets(trailer_offset, 1)
                trailer_offset -= max_align
                swap_size = int.from_bytes(self.ihex.gets(trailer_offset, 4), "little")

                # TODO: encryption keys

        if sha256sum is not None:
            m = hashlib.sha256()
            m.update(self.ihex.gets(self.ihex.minaddr(), self.header_size))
            m.update(
                self.ihex.gets(self.ihex.minaddr() + self.header_size, self.image_size)
            )
            if self.protected_tlv_size > 0:
                m.update(
                    self.ihex.gets(
                        self.ihex.minaddr() + self.header_size + self.image_size,
                        self.protected_tlv_size,
                    )
                )

            if sha256sum != m.digest():
                raise InvalidImageError(
                    f"SHA256 hash mismatch! Image={sha256sum.hex()} Calculated={m.hexdigest()}"
                )

    @property
    def version(self):
        major = self.ver_major or 0
        minor = self.ver_minor or 0
        patch = "" if self.ver_patch is None else f".{self.ver_patch}"
        tweak = "" if self.ver_tweak is None else f"+{self.ver_tweak}"
        return f"{major}.{minor}{patch}{tweak}"

    @property
    def size(self):
        tlv_size = sum([length for (_, length, _) in self.tlvs])
        if len(self.tlvs) > 0:
            tlv_size += 8
        return self.header_size + self.image_size + self.protected_tlv_size + tlv_size

    @property
    def bindata(self):
        return self.ihex.tobinarray()

    @property
    def hexdata(self):
        with io.StringIO() as out:
            self.ihex.tofile(out, "hex", byte_count=16)
            return out.getvalue()

    def get_tlv(self, tlv, default=None):

        if not isinstance(tlv, ImageTlvType):
            tlv = ImageTlvType(tlv)

        for tag, _, value in self.tlvs + self.protected_tlvs:
            if ImageTlvType(tag) != tlv:
                continue
            processor = TLV_PROCESSORS.get(tlv, lambda v: v)
            return processor(value)

        return default
