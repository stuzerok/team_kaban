"""Golden reference model for register block verification."""

from array import array
from typing import Any, Dict


class GoldModel:
    """Simple golden model for register read/write operations."""

    BASE_ADDR = 0x4000_0000
    REG_SIZE = 4

    REGS = {
        "RBR_THR": 0x4000_0000,
        "DLL": 0x4000_0004,
        "DLM": 0x4000_0008,
        "LCR": 0x4000_000C,
        "IER": 0x4000_0010,
        "IIR": 0x4000_0014,
        "FCR": 0x4000_0018,
        "LSR": 0x4000_001C,
        "MCR": 0x4000_0020,
        "MSR": 0x4000_0024,
    }

    def __init__(self) -> None:
        """Initialize internal register storage."""
        self.reg = array("I", [0] * 16)
        self.reg[3] = 0x01
        self.reg[5] = 0x8C
        self.reg[7] = 0x60

    def gold_access(self, addr: int, data: int, operation: str) -> Dict[str, Any]:
        """Perform reference read or write transaction.

        Args:
            addr: Register index.
            data: Data to be written for write operations.
            operation: Transaction type: 'read' or 'write'.

        Returns:
            Dictionary with transaction result:
            {'ack': bool, 'reg_value': int}
        """
        if not 0 <= addr < len(self.reg):
            return {"ack": False, "reg_value": 0}

        if operation == "write":
            if addr == 0:
                self.reg[addr] = data & 0x000000ff
            elif addr < 16:
                self.reg[addr] = data
            return {"ack": True, "reg_value": data}

        if operation == "read":
            return {"ack": True, "reg_value": self.reg[addr]}

        return {"ack": False, "reg_value": 0}


uart_golden = GoldModel()


def gold_access(addr: int, data: int, operation: str) -> Dict[str, Any]:
    """Proxy function for access to the global golden model instance."""
    return uart_golden.gold_access(addr, data, operation)