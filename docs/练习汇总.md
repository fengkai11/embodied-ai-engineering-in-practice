# 附录 I：全书练习汇总

本附录按章节阶段汇总全书练习，便于读者规划实践路线。

---

## I.1 第 1–5 章：概念理解练习

- 解释具身智能与 LLM Agent 的区别；
- 画出 observation / state / action / policy / episode 的关系图；
- 对比 VLM 与 VLA；
- 解释为什么机器人学习必须关心数据闭环；
- 用自己的话说明 imitation learning、BC、ACT、Diffusion Policy 的关系。

---

## I.2 第 6–8 章：任务定义与数据格式练习

- 编写 `task_pick_box_to_bin.yaml`；
- 设计一个新任务 `straighten_box`；
- 生成 synthetic episode；
- 手动检查 `states.jsonl` 和 `actions.jsonl`；
- 编写或运行数据质检脚本；
- 统计 action distribution；
- 解释什么样的 episode 不应该进入训练集。

---

## I.3 第 9–10 章：ROS2 与 rosbag 数据链路练习

- 画出 ROS2 node / topic / message 结构；
- 解释 recorder 在数据链路中的位置；
- 运行 mock ROS2 pub/sub demo；
- 将 mock rosbag 转成 episode；
- 思考真实 rosbag 与教学 mock 数据之间的差距。

---

## I.4 第 11–13 章：空间、控制与规则专家练习

- 实现像素 + 深度到相机坐标点的反投影；
- 将相机坐标点变换到 `base_link`；
- 解释 eye-to-hand 与 eye-in-hand 的区别；
- 编写 `MockRobotArm` 控制接口；
- 画出 pick-and-place 状态机；
- 生成 scripted expert 数据；
- 对 scripted dataset 做质量检查。

---

## I.5 第 14–16 章：遥操作、数据集与训练练习

- 运行键盘遥操作模拟器；
- 记录 `operator_id`、`intervention_count`、`failure_reason`；
- 构建 `dataset_v0`；
- 检查 train / val / test 划分；
- 训练 ACT-like baseline；
- 修改 `chunk_size` 并观察 loss；
- 为训练脚本增加 test set evaluation。

---

## I.6 第 17–18 章：评测与失败闭环练习

- 设计 30 次评测协议；
- 运行 policy evaluation；
- 统计 success rate、collision rate、drop rate；
- 统计 failure reason 分布；
- 建立 failure taxonomy；
- 生成下一轮补采数据计划；
- 对比 policy_v1 与 policy_v2。

---

## I.7 第 19–20 章：扩展与作品集练习

- 实现货架格口数据结构；
- 运行 shelf anomaly detection demo；
- 输出 normal / missing / misplaced / tilted；
- 将桌面扶正任务扩展为货架扶正任务；
- 生成 portfolio manifest；
- 编写 GitHub README；
- 准备简历项目描述；
- 准备 10 个面试问答；
- 制定后续 90 天学习计划。

---

## I.8 建议打卡路线

```text
第 1 周：第 1–5 章概念 + 图示
第 2 周：第 6–8 章数据格式与质检
第 3 周：第 9–13 章 ROS2、坐标系、控制与 scripted expert
第 4 周：第 14–16 章 teleop、dataset_v0、baseline 训练
第 5 周：第 17–18 章评测与失败闭环
第 6 周：第 19–20 章扩展与作品集
```
