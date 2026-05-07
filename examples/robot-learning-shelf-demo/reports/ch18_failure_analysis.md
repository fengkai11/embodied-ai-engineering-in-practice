# Failure Analysis Report

- num_trials: `40`
- num_failures: `12`
- failure_rate: `0.3`

## Failure Reason Distribution

- `grasp_offset`: 5
- `collision_risk`: 2
- `perception_miss`: 2
- `timeout`: 2
- `drop_during_transfer`: 1

## Failure Category Distribution

- `strategy_failure`: 5
- `control_or_safety_failure`: 2
- `perception_failure`: 2
- `task_management_failure`: 2
- `control_or_contact_failure`: 1

## Top Failure Cases

- trial `4` | `object_shift` | `drop_during_transfer` -> 补采慢速搬运、夹持确认、提升高度变化样本；检查夹爪控制。
- trial `10` | `random_position` | `grasp_offset` -> 补采接近/对齐阶段数据；加入 pre-grasp 对齐与修正动作。
- trial `11` | `lighting_shift` | `grasp_offset` -> 补采接近/对齐阶段数据；加入 pre-grasp 对齐与修正动作。
- trial `12` | `object_shift` | `grasp_offset` -> 补采接近/对齐阶段数据；加入 pre-grasp 对齐与修正动作。
- trial `14` | `random_position` | `timeout` -> 补采阶段切换和失败恢复数据；加入超时退出与重试逻辑。
- trial `16` | `object_shift` | `collision_risk` -> 补采避障、容器边缘、路径绕行数据；增加安全约束。
- trial `20` | `object_shift` | `collision_risk` -> 补采避障、容器边缘、路径绕行数据；增加安全约束。
- trial `27` | `lighting_shift` | `timeout` -> 补采阶段切换和失败恢复数据；加入超时退出与重试逻辑。
- trial `30` | `random_position` | `perception_miss` -> 补采遮挡、光照变化、物体扰动样本；检查相机与标注质量。
- trial `32` | `object_shift` | `grasp_offset` -> 补采接近/对齐阶段数据；加入 pre-grasp 对齐与修正动作。