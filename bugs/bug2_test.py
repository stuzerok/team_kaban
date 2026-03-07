from riscv_reg_block import reg_access
import pytest
import random

@pytest.mark.bug
def test_deadlock_hunt():
    """Охота на bus deadlock"""
    suspicious_addrs = list(range(0x0000, 0x1000))
    random.shuffle(suspicious_addrs)
    
    deadlocks_found = 0
    for write_addr in suspicious_addrs[:50]:
        reg_access(write_addr, 0xAAAAAAAA, 'write')
        
        for read_addr in suspicious_addrs[:50]:
            result = reg_access(read_addr, 0, 'read')
            if not result['ack']:
                print(f"DEADLOCK! write=0x{write_addr:04x} → read=0x{read_addr:04x}")
                deadlocks_found += 1
                break
    
    print(f"Найдено deadlock'ов: {deadlocks_found}")
