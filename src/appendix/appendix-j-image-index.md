# 附录 J：全书图片清单

本附录用于终检图片资源，尤其适合 mdBook / GitHub 发布前确认图片引用路径。

---

## J.1 图片目录说明

当前整合包主要图片目录为：

```text
images/
assets/images/
```

正文中大多数章节使用相对路径引用 `../images/...`。

---

## J.2 扫描到的图片文件

| 章节 | 图片文件 | 用途 |
|---|---|---|
| - | `images/ch02_data_closed_loop_comparison.png` | 章节配图 / 项目图示 |
| - | `images/ch02_skill_transfer_path.png` | 章节配图 / 项目图示 |
| - | `images/ch03_episode_timeline.png` | 章节配图 / 项目图示 |
| - | `images/ch03_obs_state_action_policy.png` | 章节配图 / 项目图示 |
| - | `images/ch04_bc_vs_act.png` | 章节配图 / 项目图示 |
| - | `images/ch04_imitation_learning_flow.png` | 章节配图 / 项目图示 |
| - | `images/ch05_instruction_to_structured_task.png` | 章节配图 / 项目图示 |
| - | `images/ch05_vlm_vs_vla.png` | 章节配图 / 项目图示 |
| - | `images/ch06_task_decomposition_and_versions.png` | 章节配图 / 项目图示 |
| - | `images/ch06_task_yaml_config.png` | 章节配图 / 项目图示 |
| - | `images/ch07_episode_structure.png` | 章节配图 / 项目图示 |
| - | `images/ch07_episode_sync.png` | 章节配图 / 项目图示 |
| - | `images/ch08_data_anomaly_and_action_distribution.png` | 章节配图 / 项目图示 |
| - | `images/ch08_dataset_quality_workflow.png` | 章节配图 / 项目图示 |
| - | `images/ch09_ros2_node_topic_communication.png` | 章节配图 / 项目图示 |
| - | `images/ch09_ros2_topic_to_episode_mapping.png` | 章节配图 / 项目图示 |
| - | `images/ch10_rosbag_record_and_replay.png` | 章节配图 / 项目图示 |
| - | `images/ch10_rosbag_to_episode_conversion.png` | 章节配图 / 项目图示 |
| - | `images/ch11_eye_to_hand_vs_eye_in_hand.png` | 章节配图 / 项目图示 |
| - | `images/ch11_tf_tree_and_pixel_to_grasp_pose.png` | 章节配图 / 项目图示 |
| - | `images/ch12_planning_scene_and_grasp_path.png` | 章节配图 / 项目图示 |
| - | `images/ch12_robot_arm_fk_ik_moveit2.png` | 章节配图 / 项目图示 |
| - | `images/ch13_expert_rollout_to_episode.png` | 章节配图 / 项目图示 |
| - | `images/ch13_scripted_pick_and_place_state_machine.png` | 章节配图 / 项目图示 |
| - | `images/ch14_human_demo_to_episode_data_flow.png` | 章节配图 / 项目图示 |
| - | `images/ch14_teleoperation_system_structure.png` | 章节配图 / 项目图示 |
| - | `images/ch15_dataset_split_and_versioning.png` | 章节配图 / 项目图示 |
| - | `images/ch15_dataset_v0_build_pipeline.png` | 章节配图 / 项目图示 |
| - | `images/ch16_act_training_flow.png` | 章节配图 / 项目图示 |
| - | `images/ch16_action_chunk_and_policy_rollout.png` | 章节配图 / 项目图示 |
| - | `images/ch17_eval_protocol_flow.svg` | 章节配图 / 项目图示 |
| - | `images/ch17_metric_dashboard.svg` | 章节配图 / 项目图示 |
| - | `images/ch18_failure_loop_policy_compare.svg` | 章节配图 / 项目图示 |
| - | `images/ch18_failure_taxonomy.svg` | 章节配图 / 项目图示 |
| - | `images/ch19_desktop_to_shelf_robot_evolution.png` | 章节配图 / 项目图示 |
| - | `images/ch19_shelf_merchandising_robot_architecture.png` | 章节配图 / 项目图示 |
| - | `images/ch20_career_learning_roadmap.png` | 章节配图 / 项目图示 |
| - | `images/ch20_project_to_portfolio_map.png` | 章节配图 / 项目图示 |

---

## J.3 发布前检查建议

```text
[ ] 图片文件存在
[ ] Markdown 引用路径正确
[ ] 图片命名保持英文和章节编号
[ ] 不覆盖旧图，只新增新图
[ ] mdBook 构建后逐章检查显示效果
```

---

## J.4 命名规范建议

推荐图片命名格式：

```text
chXX_short_description.png
```

例如：

```text
ch16_act_training_flow.png
ch19_desktop_to_shelf_robot_evolution.png
ch20_project_to_portfolio_map.png
```
