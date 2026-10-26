## How it works

This project implements a serial CRC-8 calculator using the polynomial 0x07 (x^8 + x^2 + x + 1).

The circuit uses an 8-bit CRC register initialized to 0x00. On each rising edge of the clock, when `uio_in[1]` (DATA_VALID) is high, the circuit processes the serial input bit from `uio_in[0]` (DATA_BIT).

The CRC is calculated using a non-reflected, MSB-first algorithm. The input bit is XORed with the most significant bit of the current CRC register. The register is shifted left, and the polynomial 0x07 is XORed into the result when the feedback bit is 1.

The CRC register can be reset to 0x00 using `uio_in[2]` (CRC_INIT). The calculated CRC is copied to the output register when `uio_in[3]` (CRC_LATCH) is asserted. The output `uo_out[7:0]` holds the latched CRC value.

Note: `uio_in[3]` is currently used as the latch input based on the implementation assumption; this pin assignment must be confirmed against the project specification.

## How to test

1. Apply a low pulse to `rst_n` to reset the circuit.
2. Set `uio_in[2]` high for one clock cycle to initialize the CRC register to 0x00.
3. Send each input bit through `uio_in[0]`, most significant bit first.
4. Set `uio_in[1]` high for each clock cycle in which a bit should be processed.
5. After all bits have been processed, set `uio_in[3]` high for one clock cycle to latch the CRC result.
6. Read the result from `uo_out[7:0]`.

The testbench checks an empty message, a byte containing all zeros, a byte containing all ones, and the ASCII string "123456789". With CRC-8 polynomial 0x07, initial value 0x00, no reflection, and final XOR 0x00, the expected CRC of "123456789" is 0xF4.

## External hardware

No external hardware is required for simulation. The design uses the clock and reset signals provided by the Tiny Tapeout interface.
