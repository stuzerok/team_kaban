"""Randomized stress test for DUT register block against golden model."""

import random
import time
from typing import Final

from gold_model import gold_access
from riscv_reg_block import reg_access

ITERATIONS: Final[int] = 10_000
MAX_ADDR: Final[int] = 16
MAX_WRITE_DATA: Final[int] = 0x0FFFFFFF
OPERATIONS: Final[tuple[str, ...]] = ("read", "write", "error")
MAX_LOGGED_ERRORS: Final[int] = 20


def test_stress_10000() -> None:
    """Run randomized DUT vs reference comparison on register accesses."""
    errors: list[str] = []
    seed = time.time_ns() & 0xFFFF_FFFF
    rng = random.Random(seed)

    print(f"Random seed={seed}")

    for iteration in range(ITERATIONS):
        addr = rng.randint(0, MAX_ADDR)
        operation = rng.choice(OPERATIONS)
        data = rng.randint(0, MAX_WRITE_DATA) if operation == "write" else 0

        dut_result = reg_access(addr, data, operation)
        ref_result = gold_access(addr, data, operation)

        if dut_result["ack"] != ref_result["ack"]:
            errors.append(
                (
                    f"[ITER {iteration}] ACK mismatch: "
                    f"addr=0x{addr:04X}, op={operation}, data=0x{data:08X}, "
                    f"dut={dut_result['ack']}, ref={ref_result['ack']}"
                )
            )

        if operation == "read" and dut_result["reg_value"] != ref_result["reg_value"]:
            errors.append(
                (
                    f"[ITER {iteration}] REG_VALUE mismatch: "
                    f"addr=0x{addr:04X}, op={operation}, "
                    f"dut=0x{dut_result['reg_value']:08X}, "
                    f"ref=0x{ref_result['reg_value']:08X}"
                )
            )

        if len(errors) >= MAX_LOGGED_ERRORS:
            errors.append(
                f"Too many errors, stopping early. Seed={seed}, "
                f"iteration={iteration}"
            )
            break

    assert not errors, (
        f"Stress test failed with seed={seed}\n" + "\n".join(errors)
    )