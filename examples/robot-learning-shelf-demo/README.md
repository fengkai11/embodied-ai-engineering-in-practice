# robot-learning-shelf-demo

这是《从自动驾驶感知到具身智能：90 天构建机器人学习数据闭环》的主线项目目录。

到第 13 章为止，项目目标已经从“理解数据格式和记录链路”，推进到“完成空间理解、机械臂控制抽象，并用规则式 expert 生成第一批 scripted episodes”。

## 当前完成范围

| 章节 | 项目推进 | 主要文件 |
|---|---|---|
| 第 2–3 章 | 生成与理解 episode | `scripts/01_generate_synthetic_episode.py`, `scripts/02_visualize_episode.py`, `datasets/dataset_v0_sample/` |
| 第 4 章 | 极简 BC / action chunk 训练雏形 | `scripts/05_train_act_baseline.py`, `reports/ch04_toy_act_report.json` |
| 第 5 章 | 自然语言指令到结构化任务 | `scripts/rule_based_task_parser.py`, `reports/ch05_task_parse.json` |
| 第 6 章 | 任务 YAML 与配置校验 | `configs/task_pick_box_to_bin.yaml`, `configs/task_straighten_box.yaml`, `scripts/validate_task_config.py` |
| 第 7–8 章 | 数据格式、坏样本、质检报告 | `scripts/04_validate_dataset.py`, `datasets/dataset_v0_bad_examples/`, `reports/ch08_*` |
| 第 9–10 章 | ROS2 topic 教学结构与 mock rosbag 转换 | `ros2_ws/`, `data/mock_rosbag/`, `scripts/03_convert_rosbag_to_dataset.py` |
| 第 11 章 | 相机内参 / 外参、TF、像素到 base_link 的变换 | `configs/camera_config.yaml`, `configs/robot_config.yaml`, `scripts/geometry_utils.py`, `reports/ch11_transform_demo.json` |
| 第 12 章 | 机械臂控制抽象与 mock 执行 | `scripts/robot_arm_interface.py`, `reports/ch12_mock_robot_arm_demo.json` |
| 第 13 章 | 规则式 pick-and-place expert 与 scripted dataset | `scripts/scripted_pick_and_place.py`, `datasets/dataset_v1_scripted/`, `reports/ch13_*` |

## 建议运行顺序

```bash
# 1. 生成/更新样例 episode
python scripts/01_generate_synthetic_episode.py

# 2. 可视化一条 episode
python scripts/02_visualize_episode.py \
  --episode_dir datasets/dataset_v0_sample/episode_0001 \
  --save_plot reports/ch07_episode_0001_action_timeline.png \
  --save_summary reports/ch07_episode_0001_summary.md

# 3. 解析自然语言任务
python scripts/rule_based_task_parser.py \
  --instruction "把红色盒子放进右边收纳盒" \
  --output_json reports/ch05_task_parse.json

# 4. 校验任务配置
python scripts/validate_task_config.py \
  --config configs/task_pick_box_to_bin.yaml \
  --output reports/ch06_task_pick_box_to_bin_validation.json

# 5. 验证数据集
python scripts/04_validate_dataset.py \
  --dataset_dir datasets/dataset_v0_sample \
  --output_json reports/ch08_dataset_v0_sample_report.json \
  --output_md reports/ch08_dataset_v0_sample_report.md \
  --plot_path reports/ch08_dataset_v0_sample_action_distribution.png

# 6. 运行 mock ROS2 数据流示例
python ros2_ws/src/shelf_demo_data_recorder/mock_ros2_pubsub_demo.py \
  --output_json reports/ch09_mock_ros2_demo.json

# 7. 将 mock rosbag 转成 episode
python scripts/03_convert_rosbag_to_dataset.py \
  --bag_jsonl data/mock_rosbag/session_0001_mock_rosbag.jsonl \
  --output_episode_dir datasets/dataset_from_mock_rosbag/episode_9001 \
  --summary_md reports/ch10_rosbag_conversion_summary.md

# 8. 运行第 11 章几何计算示例
python scripts/geometry_utils.py \
  --camera_config configs/camera_config.yaml \
  --u 356 --v 242 --depth 0.58 \
  --output reports/ch11_transform_demo.json

# 9. 运行第 12 章 mock 机械臂演示
python scripts/robot_arm_interface.py \
  --output reports/ch12_mock_robot_arm_demo.json

# 10. 生成第 13 章规则式 expert 数据
python scripts/scripted_pick_and_place.py \
  --output_dir datasets/dataset_v1_scripted \
  --num_episodes 10 \
  --seed 42 \
  --fail_mode mixed \
  --summary_md reports/ch13_scripted_rollout_summary.md

# 11. 对第 13 章数据集做统一质检
python scripts/04_validate_dataset.py \
  --dataset_dir datasets/dataset_v1_scripted \
  --output_json reports/ch13_dataset_v1_scripted_report.json \
  --output_md reports/ch13_dataset_v1_scripted_report.md \
  --plot_path reports/ch13_dataset_v1_scripted_action_distribution.png
```

## 设计边界

当前目录仍是教学项目骨架，不代表真实机器人系统的完整生产实现。真实硬件接入时，还需要继续补齐：

- 真机 MoveIt2 接入；
- 真实深度相机与时间同步；
- 遥操作采集；
- 训练 / 评测协议；
- 失败恢复与数据回流闭环。

但到第 13 章为止，本项目已经具备一个清晰、可运行、可验证的具身智能入门主线。
\n\n## Added in Chapters 14-16\n\n- keyboard teleoperation simulator\n- dataset_v0 builder\n- ACT-like baseline trainer


## 第 17–18 章新增能力

- `scripts/07_eval_policy.py`：对 policy_v1 / policy_v2 进行多场景模拟评测；
- `scripts/08_analyze_failures.py`：从 eval CSV 中统计失败原因与 failure taxonomy；
- `scripts/09_plan_next_data_collection.py`：根据失败分析生成下一轮补采数据计划；
- `reports/experiment_v1.md`：policy_v1 首次评测报告；
- `reports/ch18_next_data_collection_plan.md`：第二轮数据闭环计划。


## 第 19–20 章新增能力

- `scripts/shelf_anomaly_detection_demo.py`：实现简化的货架格口异常检测，输出 `normal / missing / misplaced / tilted`；
- `reports/ch19_shelf_anomaly_report.md`：货架异常检测教学报告；
- `scripts/10_generate_portfolio_manifest.py`：扫描项目目录，生成作品集索引和 README 模板；
- `docs/portfolio_notes.md`：GitHub 作品集整理说明；
- `docs/interview_qa.md`：面试问答清单；
- `docs/resume_project_description.md`：简历项目描述模板；
- `docs/next_90_days_plan.md`：下一阶段 90 天学习计划。
