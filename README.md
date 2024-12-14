# parallel_simulator
基于VPI库的并行仿真工具

目前为一个初始的实验版本代码，环境的依赖有：
+ Python:
    1. cocotb: 作为仿真的VPI库的Python API及仿真的启动工具
    2. SharedMemory: 用于构建进程间通信的缓冲区
    3. atomics: 用于进程间同步的基础原子操作
+ Simulator:
    Xcelium(>23.0)

运行方法为`python test_runner.py`
