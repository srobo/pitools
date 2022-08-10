import math
import struct
from pathlib import Path
from typing import List
from srobo_pitools.vcmailbox import VideoCoreMailbox


class AssetCode:

    HEADER_FORMAT = "<ccBB"

    def __init__(self, *, vcmailbox_path: Path = Path("/usr/bin/vcmailbox")) -> None:
        self._vcm = VideoCoreMailbox(vcmailbox_path=vcmailbox_path)

    def decode_asset_code(self, data_int: List[int]) -> str:
        data = [x.to_bytes(4, byteorder="big") for x in data_int]
        sig_1, sig_2, version, length = struct.unpack(self.HEADER_FORMAT, data.pop(0))
        if sig_1 != b"s" or sig_2 != b"r" or version != 0:
            raise ValueError("Did not find a valid header.")
        remaining_data = b"".join(data)
        return remaining_data[:length].decode("ascii")

    def encode_asset_code(self, code: str) -> List[int]:
        length = len(code)
        data = [self.get_header(length)]
        padded_length = 4 * math.ceil(length / 4)
        encoded_asset_code = code.encode("ascii").ljust(padded_length, b"\x00")
        assert len(encoded_asset_code) % 4 == 0
        data += [encoded_asset_code[i:i+4] for i in range(0, len(encoded_asset_code), 4)]
        return [int.from_bytes(x, byteorder="big") for x in data]

    def get_header(self, data_length: int) -> bytes:
        header_version = 0
        max_chars = 7 * 4  # 32 bits / 8 = 4 chars per address
        if data_length not in range(0, max_chars):
            raise ValueError(f"Unable to encode data longer than {max_chars}")
        return struct.pack(self.HEADER_FORMAT, b"s", b"r", header_version, data_length)

    def get_asset_code(self) -> str:
        otp_values = self._vcm.get_customer_otp()
        return self.decode_asset_code(otp_values)

    def set_asset_code(self, code: str) -> None:
        if self._vcm.get_customer_otp() != [0] * VideoCoreMailbox.OTP_ROW_NUM:
            raise ValueError("The asset code has already been set.")

        if len(code) > (VideoCoreMailbox.OTP_ROW_NUM - 1) * 4:
            raise ValueError("Asset Code is too long to be set.")

        otp_values = self.encode_asset_code(code)
        self._vcm.set_customer_otp(otp_values)