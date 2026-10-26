
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer


def crc8_update(crc, bit_in):
    feedback = ((crc >> 7) & 1) ^ bit_in
    crc = (crc << 1) & 0xFF
    if feedback:
        crc ^= 0x07
    return crc


async def tick(dut):
    await RisingEdge(dut.clk)
    await Timer(1, unit="ns")


async def send_bit(dut, bit_in):
    dut.uio_in.value = (1 << 1) | (bit_in & 1)
    await tick(dut)


@cocotb.test()
async def test_crc8(dut):
    cocotb.start_soon(Clock(dut.clk, 10, unit="us").start())

    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await tick(dut)
    await tick(dut)
    dut.rst_n.value = 1

    # Reset CRC accumulator using uio_in[2].
    dut.uio_in.value = 0b00000100
    await tick(dut)
    dut.uio_in.value = 0

    assert int(dut.uo_out.value) == 0

    # Empty message: latch should preserve CRC = 0.
    dut.uio_in.value = 0b00001000
    await tick(dut)
    assert int(dut.uo_out.value) == 0
    dut.uio_in.value = 0

    # All-zero byte.
    crc = 0
    for _ in range(8):
        await send_bit(dut, 0)
        crc = crc8_update(crc, 0)
    dut.uio_in.value = 0b00001000
    await tick(dut)
    assert int(dut.uo_out.value) == crc
    assert crc == 0
    dut.uio_in.value = 0

    # Reinitialize, then process 0xFF, MSB first.
    dut.uio_in.value = 0b00000100
    await tick(dut)
    dut.uio_in.value = 0
    crc = 0
    for bit_in in [1] * 8:
        await send_bit(dut, bit_in)
        crc = crc8_update(crc, bit_in)
    dut.uio_in.value = 0b00001000
    await tick(dut)
    assert int(dut.uo_out.value) == crc
    assert crc == 0xF3
    dut.uio_in.value = 0

    # Reinitialize, then process ASCII "123456789", MSB first.
    dut.uio_in.value = 0b00000100
    await tick(dut)
    dut.uio_in.value = 0
    crc = 0
    for byte in b"123456789":
        for shift in range(7, -1, -1):
            bit_in = (byte >> shift) & 1
            await send_bit(dut, bit_in)
            crc = crc8_update(crc, bit_in)

    dut.uio_in.value = 0b00001000
    await tick(dut)
    assert int(dut.uo_out.value) == 0xF4
    assert int(dut.uo_out.value) == crc
