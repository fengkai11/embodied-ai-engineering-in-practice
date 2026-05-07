# dataset_v0 report

- version: `v0.0.0`
- total_episodes: `18`
- success_rate: `0.7778`

## Splits

| split | episodes | success | failure | success_rate | sources |
|---|---:|---:|---:|---:|---|
| train | 11 | 9 | 2 | 0.8182 | {'teleop_keyboard_sim': 4, 'scripted_state_machine': 7} |
| val | 3 | 2 | 1 | 0.6667 | {'scripted_state_machine': 1, 'teleop_keyboard_sim': 2} |
| test | 4 | 3 | 1 | 0.75 | {'scripted_state_machine': 2, 'teleop_keyboard_sim': 2} |

## Design Notes

- 本教学版数据集来自规则 expert 数据与键盘遥操作模拟数据。
- 数据按 `source × success` 做轻量分层，再划分 train/val/test。
- 该紧凑版本用于教学与 baseline 训练；实际项目可进一步扩展数据规模、随机化与场景覆盖。