from typing import Dict, Any
from array import array


class GoldModel:
    BASE_ADDR = 0x4000_0000
    REG_SIZE = 4

    REGS = {
        "RBR_THR": 0x4000_0000,
        "DLL":     0x4000_0004,
        "DLM":     0x4000_0008,
        "LCR":     0x4000_000C,
        "IER":     0x4000_0010,
        "IIR":     0x4000_0014,
        "FCR":     0x4000_0018,
        "LSR":     0x4000_001C,
        "MCR":     0x4000_0020,
        "MSR":     0x4000_0024,
    }

    def __init__(self):
        self.reg = array('i', [0] * 17)
  

    def gold_access(self, addr: int, data: int, operation: str) -> Dict[str, Any]:

        if operation == 'write':

            self.reg[addr] = data

            return {'ack': True, 'reg_value': data}

        elif operation == 'read':

            return {'ack': True, 'reg_value': self.reg[addr]}
        return {'ack': False, 'reg_value': 0}
  


uart_golden = GoldModel()


def gold_access(addr: int, data: int, operation: str) -> Dict[str, Any]:
    return uart_golden.gold_access(addr, data, operation)