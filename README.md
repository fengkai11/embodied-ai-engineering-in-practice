# 从自动驾驶感知到具身智能：90 天构建机器人学习数据闭环

在线阅读：<https://fengkai11.github.io/embodied-ai-engineering-in-practice/>

这本书面向有工程背景的读者，目标是在 90 天内建立一条可落地的机器人学习数据闭环：
从任务定义、数据采集、数据质检、基线训练到评测与迭代，把“能跑通一次”变成“可持续改进的工程系统”。

## 这本书适合谁

- 自动驾驶、感知、规划、数据工程背景，想转向具身智能/机器人学习的工程师
- 需要把 VLA/模仿学习概念落到项目交付与团队协作流程的人
- 想用一个完整示例理解「数据 -> 训练 -> 评测 -> 迭代」闭环的人

## 你会获得什么

- 一套从桌面实验到真实机器人任务的工程化方法
- 一个可复现的主线示例：`robot-learning-shelf-demo`
- 围绕 Episode、ROS2、rosbag、ACT 基线、失败分析的实践模板
- 可直接用于项目汇报/作品集沉淀的文档与结果组织方式

## 全书内容

- 正文：第 1–20 章
- 附录：A–K
- 配图：全书关键流程图与系统图
- 示例工程：`examples/robot-learning-shelf-demo`

## 仓库结构

```text
book.toml
src/
  SUMMARY.md
  chapters/
  appendix/
assets/
  images/
examples/
  robot-learning-shelf-demo/
docs/
```

## 本地阅读

```bash
# 已安装 mdBook 时
mdbook serve

# 仅构建静态页面
mdbook build
```

默认构建输出目录为 `book/`。

## 许可与使用

本仓库内容主要用于学习与工程实践交流。若用于再发布、培训或商业用途，请先确认引用与授权边界。
