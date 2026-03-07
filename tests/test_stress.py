import random
import time

from gold_model import gold_access, uart_golden
from riscv_reg_block import reg_access


def test_stress_1000():
    """Run randomized stress test and compare DUT against golden model."""
    errors = []
    seed = int(time.time_ns() % (2**32))
    rng = random.Random(seed)

    print(f"Rand seed={seed}")  # 3360095148

    for i in range(1_000_000):
        addr = rng.randint(0, 17)
        operation = rng.choice(["read", "write", "error"])

        if operation == "write":
            data = rng.randint(0, 0xFFFFFFFF)
        else:
            data = 0

        result = reg_access(addr, data, operation)
        result_ref = gold_access(addr, data, operation)

        if result["ack"] != result_ref["ack"]:
            msg = (
                f"[ITER {i}] ACK mismatch: "
                f"addr=0x{addr:04X}, op={operation}, data=0x{data:08X}, "
                f"dut={result['ack']}, ref={result_ref['ack']}"
            )
            print(msg)
            errors.append(msg)

        if operation == "read":
            if result["reg_value"] != result_ref["reg_value"]:
                msg = (
                    f"[ITER {i}] REG_VALUE mismatch: "
                    f"addr=0x{addr:04X}, op={operation}, "
                    f"dut=0x{result['reg_value']:X}, "
                    f"ref=0x{result_ref['reg_value']:X}"
                )
                print(msg)
                errors.append(msg)

    uart_golden.write_toggle_report("toggle_report.txt")

    assert not errors, f"Rand seed={seed}"
