# Next Data Collection Plan

本计划由第 18 章失败分析结果生成，用于从 policy_v1 的失败结果进入第二轮数据闭环。

## Summary

- source_failures: `12`
- failure_rate: `0.3`

## Targeted Collection Plan

| category | failure_count | target | recommended_episodes | tasks |
|---|---:|---|---:|---|
| `strategy_failure` | 5 | 补采对齐与抓取修正 | 18 | pre-grasp 微调; 抓取点偏移恢复; 多角度接近; 抓空后重试 |
| `task_management_failure` | 2 | 补采阶段切换与超时恢复 | 12 | 超时重试; 阶段回退; 观察-决策暂停; 失败后 return_home |
| `control_or_safety_failure` | 2 | 补采避障与安全路径 | 14 | 容器边缘避障; 桌面高度误差; 路径绕行; 碰撞前停止 |
| `perception_failure` | 2 | 补采复杂视觉条件 | 20 | 强/弱光照; 部分遮挡; 物体颜色接近背景; 深度缺失边界 |
| `control_or_contact_failure` | 1 | 补采夹持稳定与搬运过程 | 16 | 慢速提升; 夹爪闭合确认; 搬运速度变化; 掉落后终止/恢复 |

## Policy v2 Experiment Design

1. 按上表补采 targeted episodes，形成 `dataset_v1_targeted`。
2. 将 `dataset_v0` 与 `dataset_v1_targeted` 合并为 `dataset_v1`。
3. 使用同一训练脚本训练 `policy_v2`。
4. 使用第 17 章相同评测协议重新评测，避免评测口径变化。
5. 对比 `policy_v1` 与 `policy_v2` 的 success rate、failure reason、intervention rate。