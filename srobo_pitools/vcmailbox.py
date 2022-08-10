"""Interact with the VideoCore."""
import subprocess
from pathlib import Path
from typing import List


class VideoCoreMailbox:
    """
    Interact with the VideoCore using the mailbox interface.

    Warning: Using the mailbox incorrectly can result in permanent damage.
    """

    _VC_GET_CUSTOMER_OTP = 0x00030021
    _VC_SET_CUSTOMER_OTP = 0x00038021
    OTP_ROW_BITS = 32
    OTP_ROW_NUM = 8

    def __init__(self, *, vcmailbox_path: Path = Path("/usr/bin/vcmailbox")) -> None:
        self._vcmailbox_path = vcmailbox_path
        if not self._vcmailbox_path.exists():
            raise ValueError("Unable to find vcmailbox command.")

    def _request(self, request_id: int, args: List[int]) -> List[int]:
        """Make a request to the mailbox."""
        command = [str(self._vcmailbox_path)]
        command += [str(request_id)]
        command += [str(arg) for arg in args]
        res = subprocess.check_output(command)
        data = res.decode().strip()
        words = data.split(" ")
        return [int(word, 16) for word in words]

    def _get_otp_request_args(
        self,
        data: List[int],
        *,
        start_row: int = 0,
        row_count: int = 8,
    ) -> List[int]:
        """Get the args for the mailbox."""
        number = 8 + row_count * 4
        args = [number] * 2
        args += [start_row, row_count]
        args += data
        return args

    def get_customer_otp(self) -> List[int]:
        """Fetch the customer OTP bits."""
        args = self._get_otp_request_args([0] * 8)
        data = self._request(self._VC_GET_CUSTOMER_OTP, args)
        return data[7:-1]

    def set_customer_otp(self, data: List[int]) -> None:
        """
        Set the customer OTP bits.

        Warning: This is permanent. You can only change 0s to 1s.
        """
        args = self._get_otp_request_args(data, row_count=len(data))
        self._request(self._VC_SET_CUSTOMER_OTP, args)
