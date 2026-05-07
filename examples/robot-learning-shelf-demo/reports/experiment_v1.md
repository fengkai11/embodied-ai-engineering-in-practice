# Experiment Report: policy_v1

- num_trials: `40`
- success_rate: `0.7`
- mean_completion_time_sec: `10.555`
- collision_rate: `0.05`
- drop_rate: `0.025`
- intervention_rate: `0.1`

## By Scenario

| scenario | trials | success_rate | mean_time_sec |
|---|---:|---:|---:|
| fixed | 10 | 1.0 | 8.73 |
| lighting_shift | 10 | 0.8 | 10.689 |
| object_shift | 10 | 0.5 | 11.863 |
| random_position | 10 | 0.5 | 10.936 |

## Failure Reasons

- `grasp_offset`: 5
- `collision_risk`: 2
- `perception_miss`: 2
- `timeout`: 2
- `drop_during_transfer`: 1

## Interpretation

本报告用于说明机器人策略评测不能只看单次成功视频，而应基于固定协议、重复 trials、结构化 CSV 与失败原因分布进行判断。