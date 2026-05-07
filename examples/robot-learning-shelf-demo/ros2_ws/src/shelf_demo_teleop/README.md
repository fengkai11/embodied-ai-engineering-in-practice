# shelf_demo_teleop

本目录对应第 14 章的遥操作采集模块。

在当前教学整合包中，实际可运行的低成本遥操作模拟脚本位于：

```text
robot-learning-shelf-demo/scripts/keyboard_teleop_sim.py
```

该脚本用于模拟键盘遥操作数据采集，并输出标准 episode 数据结构。

未来如果接入真实 ROS2 节点，可以继续在本目录扩展：

- teleop input node
- robot command bridge
- synchronized recorder
- operator session manager
- review / quality check tools
