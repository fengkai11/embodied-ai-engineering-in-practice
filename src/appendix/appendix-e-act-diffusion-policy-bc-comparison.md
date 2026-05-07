# 附录 E：ACT、Diffusion Policy 与 Behavior Cloning 对比

本附录用于帮助读者理解三类常见模仿学习策略的关系：Behavior Cloning、ACT、Diffusion Policy。它们不是互相排斥的“阵营”，而是不同复杂度和表达能力的策略选择。

---

## E.1 Behavior Cloning

Behavior Cloning 是最基础的模仿学习方法。它的核心形式是：

```text
observation -> action
```

优点：

- 简单；
- 易实现；
- 训练快；
- 适合第一版 baseline。

局限：

- 容易误差累积；
- 对分布外状态不稳；
- 单步动作可能不够连贯；
- 难以表达复杂多模态动作。

适合场景：

- 入门实验；
- 数据链路验证；
- 简单控制任务；
- 教学项目 baseline。

---

## E.2 ACT

ACT 的核心思想是预测 action chunk：

```text
observation -> action[t : t+K]
```

优点：

- 动作更连贯；
- 适合机械臂局部连续操作；
- 比单步 BC 更适合操作任务；
- 是低成本 robot learning 项目中很实用的路线。

局限：

- 仍依赖高质量示范数据；
- chunk 长度需要调试；
- 对视觉输入和动作空间设计比较敏感；
- 长程任务仍需要高层规划或分段策略。

适合场景：

- 抓取；
- 放置；
- 扶正；
- 开抽屉；
- 局部连续操作任务。

---

## E.3 Diffusion Policy

Diffusion Policy 使用扩散建模方式生成动作序列，可以表达更复杂的动作分布。

优点：

- 对复杂、多模态动作更友好；
- 能处理多个合理动作解；
- 在复杂操作任务中表达能力强。

局限：

- 训练复杂度更高；
- 推理成本可能更高；
- 调参与工程门槛更高；
- 对数据质量和评测要求更高。

适合场景：

- 多模态操作；
- 精细 manipulation；
- 动作分布复杂的任务；
- 更成熟的数据和硬件条件。

---

## E.4 三者对比表

| 方法 | 输入输出 | 优点 | 局限 | 适合阶段 |
|---|---|---|---|---|
| Behavior Cloning | observation -> action | 简单、快、易调试 | 单步、易误差累积 | 第一个 baseline |
| ACT | observation -> action chunk | 动作连贯、适合操作 | 依赖高质量数据 | 低成本操作策略 |
| Diffusion Policy | observation -> action sequence distribution | 表达能力强 | 工程复杂度更高 | 进阶策略 |

---

## E.5 本书为什么先用 ACT-like baseline

本书选择 ACT-like baseline 的原因是：

1. 它能自然引出 action chunk；
2. 它比单步 BC 更贴近机械臂操作；
3. 它又比完整 Diffusion Policy 更容易讲清楚；
4. 它适合在教学项目中建立第一条训练闭环。

注意：本书中的 ACT-like baseline 是教学简化版，不等同于完整论文级 ACT 实现。它的目标是让读者理解数据到策略训练的主线，而不是刷 benchmark。
