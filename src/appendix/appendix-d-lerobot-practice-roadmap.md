# 附录 D：LeRobot 实战路线：从本书项目迁移到开源框架

本附录说明如何把本书的 `robot-learning-shelf-demo` 思路迁移到 LeRobot 等开源机器人学习工具链。这里的目标不是马上替换全部代码，而是建立概念映射与迁移步骤。

---

## D.1 为什么选择 LeRobot 作为后续实践方向

LeRobot 适合本书读者的原因在于：

1. 它围绕数据集、策略训练和机器人学习流程组织；
2. 它支持 ACT 等适合入门和低成本实践的策略；
3. 它强调 episode / observation / action 这类核心概念；
4. 它可以作为从教学 demo 走向真实机器人学习框架的桥梁。

---

## D.2 本书项目与 LeRobot 的概念映射

| 本书项目 | LeRobot 对应概念 |
|---|---|
| `episode_0001/` | episode |
| `states.jsonl` | state / observation metadata |
| `actions.jsonl` | action sequence |
| `images/front/` | camera observation |
| `images/wrist/` | wrist camera observation |
| `meta.json` | episode metadata |
| `dataset_v0/` | training dataset |
| `teleop dataset` | human demonstration dataset |
| `ACT-like baseline` | ACT policy |
| `evaluation CSV` | rollout/evaluation log |
| `failure_reason` | failure annotation |

---

## D.3 迁移步骤

### 步骤 1：整理本书 episode

先确保每条 episode 都有：

- 图像；
- 状态；
- 动作；
- 时间戳；
- 成功 / 失败标签；
- 任务指令；
- 相机名称；
- 动作维度说明。

### 步骤 2：统一 observation / action 格式

重点检查：

- action 维度是否一致；
- gripper action 是连续值还是离散开合；
- 图像大小是否统一；
- 多视角是否同步；
- 状态字段是否缺失。

### 步骤 3：生成 LeRobot 风格数据集

可以先写一个转换脚本，将本书 `dataset_v0` 转换成目标框架所需格式。

### 步骤 4：训练 ACT policy

使用真实框架训练 ACT policy 时，建议先保持任务简单：

- 单任务；
- 固定动作空间；
- 小规模数据；
- 先跑通训练和 rollout。

### 步骤 5：做 rollout evaluation

不要只看训练 loss。需要评估：

- success rate；
- completion time；
- collision / drop；
- intervention；
- failure reason。

---

## D.4 常见迁移问题

### action 定义不一致

如果本书动作是 `[dx, dy, dz, gripper_delta]`，而目标框架需要 joint position 或 absolute pose，就必须明确转换关系。

### 相机同步问题

本书教学数据可以简化同步，但真实数据必须保证多视角图像、状态和动作时间对齐。

### gripper action 定义问题

夹爪动作必须清楚区分：

- open / close；
- width；
- force；
- normalized command。

### episode 成功/失败标签缺失

没有成功/失败标签，后续评测、失败分析和数据筛选会变得困难。

---

## D.5 建议实践小项目

把本书第 13–16 章重做一遍，但使用 LeRobot 风格数据集和训练代码：

1. 采集 20 条 scripted episode；
2. 采集 20 条 teleop episode；
3. 转换为目标格式；
4. 训练 ACT；
5. 做 30 次 rollout evaluation；
6. 统计 failure reason；
7. 生成 `dataset_v1` 计划。
