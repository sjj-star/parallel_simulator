# This file is public domain, it can be freely copied without restrictions.
# SPDX-License-Identifier: CC0-1.0

# test_runner.py

import os
from pathlib import Path
from multiprocessing import Process
from multiprocessing.managers import SharedMemoryManager

from cocotb.runner import get_runner, Simulator

def master_test(runner:Simulator, shm_name:str, proj_path:Path):
    runner.test(
            test_module="interface",
            hdl_toplevel="master",
            extra_env={"HLV_SHM":shm_name, "HLV_INF_TYPE":"MST"},
            build_dir=proj_path / "sim_build/master",
            test_dir=proj_path / "sim_test/master_0",
            waves=True,
            verbose=True
    )

def slave_test(runner:Simulator, shm_name:str, proj_path:Path):
    runner.test(
            test_module="interface",
            hdl_toplevel="slave",
            extra_env={"HLV_SHM":shm_name, "HLV_INF_TYPE":"SLV"},
            build_dir=proj_path / "sim_build/slave",
            test_dir=proj_path / "sim_test/slave_0",
            waves=True,
            verbose=True
    )

if __name__ == "__main__":
    sim = os.getenv("SIM", "xcelium")
    runner = get_runner(sim)

    proj_path = Path(__file__).resolve().parent
    
    runner.build(
        verilog_sources=[proj_path / "rtl/master.sv"],
        hdl_toplevel="master",
        build_dir=proj_path / "sim_build/master",
        waves=True,
        verbose=True
    )

    runner.build(
        verilog_sources=[proj_path / "rtl/slave.sv"],
        hdl_toplevel="slave",
        build_dir=proj_path / "sim_build/slave",
        waves=True,
        verbose=True
    )

    with SharedMemoryManager() as smm:
        shm = smm.SharedMemory(1024)
        shm.buf[:] = bytearray(1024)

        mst_p = Process(target=master_test, args=(runner, shm.name, proj_path))
        slv_p = Process(target=slave_test, args=(runner, shm.name, proj_path))

        mst_p.start()
        slv_p.start()
        mst_p.join()
        slv_p.join()
