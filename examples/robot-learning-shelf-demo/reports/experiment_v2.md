# Experiment Report: policy_v2

- num_trials: `40`
- success_rate: `0.8`
- mean_completion_time_sec: `9.771`
- collision_rate: `0.025`
- drop_rate: `0.025`
- intervention_rate: `0.025`

## By Scenario

| scenario | trials | success_rate | mean_time_sec |
|---|---:|---:|---:|
| fixed | 10 | 0.8 | 8.963 |
| lighting_shift | 10 | 0.7 | 10.697 |
| object_shift | 10 | 0.8 | 10.207 |
| random_position | 10 | 0.9 | 9.217 |

## Failure Reasons

- `grasp_offset`: 3
- `perception_miss`: 3
- `collision_risk`: 1
- `drop_during_transfer`: 1