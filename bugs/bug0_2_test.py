from riscv_reg_block import reg_access
from gold_model import gold_access
import pytest
import random

def test_bit_mask():
    
    errors = 0

    addr = 5
    data = 0x00000000
    operation = 'read'
    errors += data_sent(addr, data, operation)
    
    addr = 5
    data = 0x00ffff
    operation = 'write'
    errors += data_sent(addr, data, operation)

    addr = 5
    data = 0x00000000
    operation = 'read'
    errors += data_sent(addr, data, operation)

    addr = 7
    data = 0x00000000
    operation = 'read'
    errors += data_sent(addr, data, operation)
    
    addr = 7
    data = 0x00ffff
    operation = 'write'
    errors += data_sent(addr, data, operation)

    addr = 7
    data = 0x00000000
    operation = 'read'
    errors += data_sent(addr, data, operation)


    assert not errors

def data_sent(addr, data, operation):
    errors = 0
    result = reg_access(addr, data, operation)
    result_ref = gold_access(addr, data, operation)
    errors = check_val (addr, data, result, result_ref, operation)
    return errors

def check_val(addr, data, result, result_ref, operation):
    errors = 0
    if result['ack'] != result_ref['ack']:
        msg = (
            f"ACK mismatch: "
            f"addr=0x{addr:04X}, op={operation}, data=0x{data:08X}, "
            f"dut={result['ack']}, ref={result_ref['ack']}"
        )
        print(msg)
        errors = errors + 1
    if operation == 'read':
        if result['reg_value'] != result_ref['reg_value']:
            msg = (
                f"REG_VALUE mismatch: "
                f"addr=0x{addr:04X}, op={operation}, "
                f"dut=0x{result['reg_value']:X}, ref=0x{result_ref['reg_value']:X}"
            )
            print(msg)
            errors = errors + 1
    return errors