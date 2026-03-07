"""Golden reference model for register block verification."""

from array import array
from typing import Any, Dict, List


class GoldModel:
    """Golden model for register read/write operations with toggle coverage."""

    BASE_ADDR = 0x4000_0000
    REG_SIZE = 4
    NUM_REGS = 10
    DATA_MASK = 0xFFFFFFFF
    BYTE_MASK_0 = 0x000000FF
    BYTE_MASK_4 = 0x0000000F
    BYTE_MASK_6 = 0x000000C7
    BYTE_MASK_8 = 0x0000000F

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
        """Initialize register storage and toggle coverage structures."""
        self.reg = array("I", [0] * self.NUM_REGS)
        self.prev_reg = array("I", [0] * self.NUM_REGS)
        self.toggle_01 = array("I", [0] * self.NUM_REGS)
        self.toggle_10 = array("I", [0] * self.NUM_REGS)
        self.reset()

    def reset(self) -> None:
        """Reset registers and coverage state to default values."""
        self.reg = array("I", [0] * self.NUM_REGS)

        # Пример reset-значений
        self.reg[3] = 0x01
        self.reg[5] = 0x8C
        self.reg[7] = 0x60

        self.prev_reg = array("I", self.reg)
        self.toggle_01 = array("I", [0] * self.NUM_REGS)
        self.toggle_10 = array("I", [0] * self.NUM_REGS)

    def _is_valid_addr(self, addr: int) -> bool:
        """Check whether register index is valid."""
        return 0 <= addr < self.NUM_REGS

    def _normalize_write_data(self, addr: int, data: int) -> int:
        """Apply register-specific write masking rules."""
        if addr == 0:
            return data & self.BYTE_MASK_0
        if addr == 4:
            return data & self.BYTE_MASK_4
        if addr == 6:
            return data & self.BYTE_MASK_6
        if addr == 8:
            return data & self.BYTE_MASK_8
        return data & self.DATA_MASK

    def _update_toggle(self, addr: int, new_value: int) -> None:
        """Update toggle coverage for one register."""
        old_value = self.prev_reg[addr] & self.DATA_MASK
        new_value = new_value & self.DATA_MASK

        rise_mask = (~old_value) & new_value & self.DATA_MASK
        fall_mask = old_value & (~new_value) & self.DATA_MASK

        self.toggle_01[addr] |= rise_mask
        self.toggle_10[addr] |= fall_mask
        self.prev_reg[addr] = new_value

    def gold_access(self, addr: int, data: int, operation: str) -> Dict[str, Any]:
        """Perform reference read or write transaction.

        Args:
            addr: Register index.
            data: Data for write operation.
            operation: 'read' or 'write'.

        Returns:
            Dictionary with result:
            {'ack': bool, 'reg_value': int}
        """
        if not self._is_valid_addr(addr):
            return {"ack": False, "reg_value": 0}

        op = operation.lower()

        if op == "write":
            new_value = self._normalize_write_data(addr, data)
            if addr == 5:
                self.reg[addr] = self.reg[addr]
            elif addr == 7:
                self.reg[addr] = self.reg[addr]
            elif addr == 9:
                self.reg[addr] = self.reg[addr]
            elif addr == 1 and not (self.reg[3] * 0x80 >> 8):
                self.reg[addr] = self.reg[addr]
            elif addr == 2 and not (self.reg[3] * 0x80 >> 8):
                self.reg[addr] = self.reg[addr]   
            else:         
                self.reg[addr] = new_value

            self._update_toggle(addr, data)
            return {"ack": True, "reg_value": new_value}

        if op == "read":
            return {"ack": True, "reg_value": self.reg[addr]}

        return {"ack": False, "reg_value": 0}

    def get_toggle_coverage(self) -> Dict[str, float]:
        """Return overall toggle coverage statistics."""
        hit_points = 0

        for addr in range(self.NUM_REGS):
            hit_points += self.toggle_01[addr].bit_count()
            hit_points += self.toggle_10[addr].bit_count()

        total_points = self.NUM_REGS * 32 * 2
        coverage_percent = 100.0 * hit_points / total_points

        return {
            "hit_points": float(hit_points),
            "total_points": float(total_points),
            "coverage_percent": coverage_percent,
        }

    def get_toggle_per_reg(self) -> List[float]:
        """Return toggle coverage percentage for each register."""
        coverage = []

        for addr in range(self.NUM_REGS):
            hits = self.toggle_01[addr].bit_count() + self.toggle_10[addr].bit_count()
            coverage.append(100.0 * hits / 64.0)

        return coverage

    def get_toggle_matrix(self) -> Dict[int, Dict[str, int]]:
        """Return raw toggle masks for each register."""
        matrix: Dict[int, Dict[str, int]] = {}

        for addr in range(self.NUM_REGS):
            matrix[addr] = {
                "0_to_1": int(self.toggle_01[addr]),
                "1_to_0": int(self.toggle_10[addr]),
            }

        return matrix

    def write_toggle_report(self, filename: str = "toggle_report.txt") -> None:
        """Write 10x32 toggle matrix to a text file.
    
        Matrix[row][bit] == 1 means that this bit had both transitions:
        0->1 at least once and 1->0 at least once.
        """
        with open(filename, "w", encoding="utf-8") as report:
            for reg_idx in range(10):
                row = []

                for bit in range(32):
                    rise_seen = (self.toggle_01[reg_idx] >> bit) & 1
                    fall_seen = (self.toggle_10[reg_idx] >> bit) & 1

                    if rise_seen and fall_seen:
                        row.append("1")
                    else:
                        row.append("0")

                report.write(" ".join(row) + "\n")

    def write_toggle_arrays(self, filename: str = "toggle_arrays.txt") -> None:
        """Write raw toggle arrays to a text file."""
        with open(filename, "w", encoding="utf-8") as report:
            report.write("toggle_01 = [\n")
            for value in self.toggle_01:
                report.write(f"    0x{value:08X},\n")
            report.write("]\n\n")

            report.write("toggle_10 = [\n")
            for value in self.toggle_10:
                report.write(f"    0x{value:08X},\n")
            report.write("]\n")


uart_golden = GoldModel()


def gold_access(addr: int, data: int, operation: str) -> Dict[str, Any]:
    """Proxy function for access to the global golden model instance."""
    return uart_golden.gold_access(addr, data, operation)