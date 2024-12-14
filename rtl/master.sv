// This file is public domain, it can be freely copied without restrictions.
// SPDX-License-Identifier: CC0-1.0

`timescale 1ns/1ps
module master(
  input wire clk,
  input wire rst,
  output reg [31:0] data,
  output reg valid,
  input wire ready
);

  initial begin
    @(posedge rst);
    valid <= 1'b0;
    @(negedge rst);

    forever begin
      if($urandom_range(0,1)) begin
        valid <= 1'b1;
        data <= $urandom();
        @(posedge clk iff ready);
        $display("Send Data: 0x%h", data);
      end else begin
        valid <= 1'b0;
        @(posedge clk);
      end
    end
  end

endmodule
