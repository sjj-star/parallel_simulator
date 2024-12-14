# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0

import os
import struct
from multiprocessing import shared_memory
import atomics

import cocotb
from cocotb.triggers import Timer
import cocotb.triggers


async def generate_clock(clk):
    """Generate clock pulses."""

    while True:
        clk.value = 0
        await Timer(5, units="ns")
        clk.value = 1
        await Timer(5, units="ns")

async def generate_reset(dut, inf_type, rst_ready_count):
    """Generate reset pulses."""

    dut.rst.value = 1
    if inf_type == "MST":
        dut.ready.value = 0
    elif inf_type == "SLV":
        dut.valid.value = 0
    await Timer(50, units="ns")
    await cocotb.triggers.RisingEdge(dut.clk)
    dut.rst.value = 0
    rst_ready_count.inc()
    while True:
        if rst_ready_count.load() == 2:
            break

async def generate_ready(dut):
    while True:
        await cocotb.triggers.RisingEdge(dut.clk)
        dut.ready.value = 1
        await cocotb.triggers.RisingEdge(dut.clk)
        dut.ready.value = 0

@cocotb.test()
async def interface_agent(dut):
    await cocotb.start(generate_clock(dut.clk))  # run the clock "in the background"

    shm_name = os.getenv("HLV_SHM")
    inf_type = os.getenv("HLV_INF_TYPE")
    if shm_name:
        shm = shared_memory.SharedMemory(shm_name)
        sim_buf = shm.buf
        with atomics.atomicview(buffer=sim_buf[:4], atype=atomics.INT) as sim_ready_count:
            sim_ready_count.inc()
            while True:
                if sim_ready_count.load() == 2:
                    break
        with atomics.atomicview(buffer=sim_buf[4:8], atype=atomics.INT) as rst_ready_count:
            await generate_reset(dut, inf_type, rst_ready_count)

        with atomics.atomicview(buffer=sim_buf[8:12], atype=atomics.INT) as wr_ptr:
            with atomics.atomicview(buffer=sim_buf[12:16], atype=atomics.INT) as rd_ptr:
                """Try accessing the design."""
                if inf_type == "MST":
                    await cocotb.start(generate_ready(dut))
                    while True:
                        await cocotb.triggers.RisingEdge(dut.clk)
                        if dut.valid.value and dut.ready.value:
                            struct.pack_into('I', sim_buf, 16+wr_ptr.load()*4, int(dut.data.value))
                            wr_ptr.inc()
                        if wr_ptr.load() == 100:
                            break
                elif inf_type == "SLV":
                        while True:
                            if wr_ptr.load() - rd_ptr.load() > 0:
                                data = struct.unpack('I', sim_buf[16+rd_ptr.load()*4:20+rd_ptr.load()*4])[0]
                                dut.valid.value = 1
                                dut.data.value = data
                                rd_ptr.inc()
                                while True:
                                    await cocotb.triggers.RisingEdge(dut.clk)
                                    if dut.ready.value:
                                        dut.valid.value = 0
                                        break
                            elif rd_ptr.load() == 100:
                                break
                            else:
                                await cocotb.triggers.RisingEdge(dut.clk)
        shm.close()
