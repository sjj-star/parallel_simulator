// This file is public domain, it can be freely copied without restrictions.
// SPDX-License-Identifier: CC0-1.0

`timescale 1ps/1ps
module slave(
  input wire clk,
  input wire rst,
  input wire [31:0] data,
  input wire valid,
  output reg ready
);

  always @(posedge clk or posedge rst) begin
    if(rst) begin
      ready <= 1'b0;
    end else begin
      ready <= $urandom_range(0,1);
    end
  end

  always @(posedge clk) begin
    if(valid & ready) begin
      $display("Recv Data: 0x%h", data);
    end
  end

endmodule
