from riscv_reg_block import reg_access
import pytest
import random

@pytest.mark.bug
def test_stale_data_hunt():
    """Охота на stale data"""
    suspicious_addrs = list(range(0x0000, 0x1000))
    random.shuffle(suspicious_addrs)
    
    stale_found = 0
    for addr in suspicious_addrs[:100]:
        reg_access(addr, 0x1234, 'write')
        r1 = reg_access(addr, 0, 'read')
        reg_access(addr, 0x5678, 'write')
        r2 = reg_access(addr, 0, 'read')
        if r1['reg_value'] == r2['reg_value']:
            print(f"STALE DATA addr=0x{addr:04x}")
            stale_found += 1
    
    print(f"Найдено stale data: {stale_found}")
