# 简历项目描述（Chapter 20）

## 项目名称
机器人学习数据闭环教学项目（robot-learning-shelf-demo）

## 项目描述（长版）
围绕桌面 pick-and-place 任务，独立设计并实现了一套面向具身智能入门的机器人学习主线项目，覆盖任务定义、episode 数据结构、ROS2 数据记录、规则式 expert 数据生成、键盘遥操作数据采集、dataset_v0 构建、ACT-like baseline 训练、结构化评测协议、failure taxonomy 与第二轮数据闭环；并进一步扩展到货架异常检测与理货机器人方向，形成可用于 GitHub 展示和面试讲解的作品集。

## 项目描述（简历精简版）
- 搭建机器人学习主线项目，完成从数据采集、训练、评测到失败闭环的完整教学链路；
- 设计 episode / dataset 结构，生成 scripted 与 teleop 数据，并构建可训练的 `dataset_v0`；
- 训练 ACT-like baseline，建立 success rate / collision rate / failure reason 等结构化评测指标；
- 基于失败分析制定 targeted data collection 方案，并扩展到货架异常检测与理货机器人任务。

## STAR 表达建议
### S（Situation）
希望从自动驾驶感知工程转向具身智能，但缺少一条可执行、可展示、可解释的机器人学习主线项目。

### T（Task）
搭建一个从任务定义到数据闭环完整跑通的项目，并沉淀为可展示的工程作品集。

### A（Action）
完成数据结构设计、mock ROS2 录制、规则式 expert rollout、teleop 数据采集、dataset_v0 构建、ACT-like baseline 训练、评测协议与失败分析；同时新增货架异常检测 demo 和作品集整理文档。

### R（Result）
形成第 1–20 章完整项目包，具备代码、数据、报告、图示和面试讲解材料，可直接作为具身智能方向的学习成果与求职作品集。
