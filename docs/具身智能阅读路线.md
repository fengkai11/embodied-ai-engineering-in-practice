# 附录 B：具身智能论文与项目阅读路线

本附录给出一条服务本书主线的阅读路线。它不是为了追求“读最多论文”，而是为了让读者围绕机器人学习数据闭环逐步建立知识结构。

---

## B.1 阅读原则

阅读具身智能资料时，建议遵循三条原则：

1. **先读能落到项目里的内容**：例如 episode、teleop、ACT、evaluation；
2. **再读基础模型路线**：例如 VLA、robot foundation model；
3. **最后读大规模系统与开放问题**：例如跨机器人泛化、多任务学习、sim-to-real。

不要一开始就陷入“追最前沿模型”的焦虑。本书的核心是把工程底座先跑通。

---

## B.2 第一阶段：机器人学习基础

建议目标：理解机器人学习任务中的数据、策略、动作空间和评测方式。

推荐主题：

- Behavior Cloning；
- Imitation Learning；
- Offline RL；
- Visuomotor Policy；
- Dataset / Episode；
- Teleoperation。

阅读时重点问自己：

- 输入是什么？
- 输出是什么？
- 数据从哪里来？
- 策略如何训练？
- 成功率如何评测？
- 失败如何分析？

---

## B.3 第二阶段：操作策略模型

建议目标：理解机械臂操作任务中常见策略结构。

推荐主题：

- ACT；
- Diffusion Policy；
- Transformer-based policy；
- Action Chunk；
- Sequence modeling for manipulation；
- Multi-view visuomotor learning。

阅读时重点关注：

- 为什么一次预测多步动作？
- 图像如何编码为策略输入？
- 动作空间如何设计？
- 模型如何 rollout？
- 离线指标和实机成功率之间有什么差距？

---

## B.4 第三阶段：VLA 与机器人基础模型

建议目标：理解前沿路线的核心问题，而不是马上复现大模型。

推荐主题：

- RT 系列；
- OpenVLA；
- π0 / pi-zero 类路线；
- Open X-Embodiment；
- DROID；
- Gemini Robotics；
- GR00T；
- LeRobot。

阅读时重点关注：

- 多任务数据如何组织？
- 语言指令如何进入策略？
- action representation 如何设计？
- 跨机器人泛化如何实现？
- 数据规模、硬件和算力门槛在哪里？

---

## B.5 第四阶段：系统工程与部署

建议目标：理解真实机器人系统如何从模型走向可执行系统。

推荐主题：

- ROS2；
- MoveIt2；
- TF 与标定；
- Isaac Sim / MuJoCo / Gazebo；
- Real-time inference；
- Safety monitoring；
- Teleop system；
- Data recorder。

阅读时重点关注：

- 机器人坐标链如何保证正确？
- 相机和动作如何同步？
- 评测协议如何设计？
- 失败日志如何保留？
- 如何把 demo 做成可复现工程？

---

## B.6 推荐阅读顺序

```text
机器人学习基础
  -> 数据格式与遥操作
  -> ACT / Diffusion Policy
  -> 评测与失败闭环
  -> VLA / Robot Foundation Model
  -> 系统部署与真机差距
```

这个顺序和本书主线一致，适合自动驾驶/机器人算法工程师从已有经验迁移到具身智能。
