# 附录 H：全书代码目录说明

本附录汇总 `robot-learning-shelf-demo/` 的主要代码、配置、数据与报告目录，方便读者按章节查找。

---

## H.1 项目总览

```text
robot-learning-shelf-demo/
  configs/
  scripts/
  datasets/
  reports/
  docs/
  notebooks/
  ros2_ws/
```

---

## H.2 configs/

配置文件主要用于任务定义、相机参数、机器人参数等。

- `configs/camera_config.yaml`
- `configs/robot_config.yaml`
- `configs/task_pick_box_to_bin.yaml`
- `configs/task_straighten_box.yaml`

---

## H.3 scripts/

脚本目录是主线项目的核心，覆盖数据生成、可视化、转换、校验、训练、评测、失败分析、作品集生成等步骤。

- `ros2_ws/src/shelf_demo_data_recorder/launch/shelf_demo_record.launch.py`
- `ros2_ws/src/shelf_demo_data_recorder/mock_ros2_pubsub_demo.py`
- `scripts/01_generate_synthetic_episode.py`
- `scripts/02_visualize_episode.py`
- `scripts/03_convert_rosbag_to_dataset.py`
- `scripts/04_validate_dataset.py`
- `scripts/05_train_act_baseline.py`
- `scripts/06_train_act_on_dataset_v0.py`
- `scripts/07_eval_policy.py`
- `scripts/08_analyze_failures.py`
- `scripts/09_plan_next_data_collection.py`
- `scripts/10_generate_portfolio_manifest.py`
- `scripts/build_dataset_v0.py`
- `scripts/geometry_utils.py`
- `scripts/keyboard_teleop_sim.py`
- `scripts/robot_arm_interface.py`
- `scripts/rule_based_task_parser.py`
- `scripts/scripted_pick_and_place.py`
- `scripts/shelf_anomaly_detection_demo.py`
- `scripts/validate_task_config.py`

---

## H.4 datasets/

数据集目录通常包含：

- `dataset_v0_sample/`：早期样例 episode；
- `dataset_v0_bad_examples/`：坏样本案例；
- `dataset_from_mock_rosbag/`：由 mock rosbag 转换得到的数据；
- `dataset_v1_scripted/`：规则专家生成数据；
- `dataset_teleop_demo/`：遥操作模拟数据；
- `dataset_v0/`：第一版可训练数据集。

---

## H.5 reports/

报告目录用于保存训练、评测、数据集检查和失败分析结果。当前扫描到的报告文件包括：

- `reports/action_timeline.png`
- `reports/ch04_toy_act_report.json`
- `reports/ch04_toy_act_rollout.png`
- `reports/ch05_task_parse.json`
- `reports/ch06_task_pick_box_to_bin_validation.json`
- `reports/ch07_episode_0001_action_timeline.png`
- `reports/ch07_episode_0001_summary.md`
- `reports/ch07_episode_0002_action_timeline.png`
- `reports/ch07_episode_0002_summary.md`
- `reports/ch08_dataset_v0_bad_examples_action_distribution.png`
- `reports/ch08_dataset_v0_bad_examples_report.json`
- `reports/ch08_dataset_v0_bad_examples_report.md`
- `reports/ch08_dataset_v0_sample_action_distribution.png`
- `reports/ch08_dataset_v0_sample_report.json`
- `reports/ch08_dataset_v0_sample_report.md`
- `reports/ch09_mock_ros2_demo.json`
- `reports/ch10_dataset_from_mock_rosbag_action_distribution.png`
- `reports/ch10_dataset_from_mock_rosbag_report.json`
- `reports/ch10_dataset_from_mock_rosbag_report.md`
- `reports/ch10_rosbag_conversion_summary.md`
- `reports/ch11_transform_demo.json`
- `reports/ch12_mock_robot_arm_demo.json`
- `reports/ch13_dataset_v1_scripted_action_distribution.png`
- `reports/ch13_dataset_v1_scripted_report.json`
- `reports/ch13_dataset_v1_scripted_report.md`
- `reports/ch13_scripted_rollout_summary.md`
- `reports/ch14_keyboard_teleop_summary.json`
- `reports/ch14_keyboard_teleop_summary.md`
- `reports/ch15_dataset_v0_report.json`
- `reports/ch15_dataset_v0_report.md`
- `reports/ch16_act_dataset_v0_loss_curve.png`
- `reports/ch16_act_dataset_v0_report.json`
- `reports/ch16_act_dataset_v0_report.md`
- `reports/ch16_policy_v1_linear_chunk.npz`
- `reports/ch17_policy_v1_eval.csv`
- `reports/ch17_policy_v1_eval_summary.json`
- `reports/ch18_failure_analysis.json`
- `reports/ch18_failure_analysis.md`
- `reports/ch18_next_data_collection_plan.json`
- `reports/ch18_next_data_collection_plan.md`
- `reports/ch18_policy_v1_v2_comparison.md`
- `reports/ch18_policy_v2_eval.csv`
- `reports/ch18_policy_v2_eval_summary.json`
- `reports/ch19_shelf_anomaly_report.json`
- `reports/ch19_shelf_anomaly_report.md`
- `reports/experiment_v1.md`
- `reports/experiment_v2.md`

---

## H.6 docs/

docs 目录用于保存作品集、简历、面试和后续学习材料。

- `docs/README_portfolio_template.md`
- `docs/interview_qa.md`
- `docs/next_90_days_plan.md`
- `docs/portfolio_manifest.json`
- `docs/portfolio_notes.md`
- `docs/resume_project_description.md`

---

## H.7 推荐运行顺序

```text
01_generate_synthetic_episode.py
-> 02_visualize_episode.py
-> 04_validate_dataset.py
-> 03_convert_rosbag_to_dataset.py
-> scripted_pick_and_place.py
-> keyboard_teleop_sim.py
-> build_dataset_v0.py
-> 06_train_act_on_dataset_v0.py
-> 07_eval_policy.py
-> 08_analyze_failures.py
-> 09_plan_next_data_collection.py
-> shelf_anomaly_detection_demo.py
-> 10_generate_portfolio_manifest.py
```

实际运行时以项目 README 中命令为准。
