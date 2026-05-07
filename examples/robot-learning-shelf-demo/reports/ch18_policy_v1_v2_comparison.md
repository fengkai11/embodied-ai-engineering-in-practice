# Policy v1 / v2 Comparison

| metric | policy_v1 | policy_v2 |
|---|---:|---:|
| success_rate | 0.7 | 0.8 |
| mean_completion_time_sec | 10.555 | 9.771 |
| collision_rate | 0.05 | 0.025 |
| drop_rate | 0.025 | 0.025 |
| intervention_rate | 0.1 | 0.025 |

## Interpretation

`policy_v2` 是根据第 18 章补采计划设计的下一轮策略占位评测，用于展示如何保持相同评测协议并比较版本变化。实际项目中，policy_v2 应由 targeted dataset 重新训练得到。