
/*
 * E05 - Serial CRC-8
 * Polynomial: 0x07
 * Init: 0x00, RefIn/RefOut: false, XorOut: 0x00
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_yuuchann123_crc8 (
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);

    wire data_bit   = uio_in[0];
    wire data_valid = uio_in[1];
    wire crc_init   = uio_in[2];
    wire crc_latch  = uio_in[3];

    reg  [7:0] crc;
    reg  [7:0] crc_out;
    wire       feedback;
    wire [7:0] crc_next;

    assign feedback = crc[7] ^ data_bit;

    assign crc_next = {
        crc[6],
        crc[5],
        crc[4],
        crc[3],
        crc[2],
        crc[1] ^ feedback,
        crc[0] ^ feedback,
        feedback
    };

    always @(posedge clk) begin
        if (!rst_n) begin
            crc     <= 8'h00;
            crc_out <= 8'h00;
        end else if (ena) begin
            if (crc_init) begin
                crc     <= 8'h00;
                crc_out <= 8'h00;
            end else begin
                if (data_valid)
                    crc <= crc_next;

                if (crc_latch)
                    crc_out <= crc;
            end
        end
    end

    assign uo_out  = crc_out;
    assign uio_out = 8'h00;
    assign uio_oe  = 8'h00;

    wire _unused = &{1'b0, ui_in};

endmodule

`default_nettype wire
