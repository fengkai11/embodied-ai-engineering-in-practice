#!/usr/bin/env python3
"""Generate next data collection plan from failure analysis.

The output is a Markdown plan that maps failure categories to targeted data
collection tasks, forming a simple robot learning data loop.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


CATEGORY_TO_PLAN = {
    "perception_failure": {
        "target": "补采复杂视觉条件",
        "episodes": 20,
        "tasks": ["强/弱光照", "部分遮挡", "物体颜色接近背景", "深度缺失边界"],
    },
    "strategy_failure": {
        "target": "补采对齐与抓取修正",
        "episodes": 18,
        "tasks": ["pre-grasp 微调", "抓取点偏移恢复", "多角度接近", "抓空后重试"],
    },
    "control_or_contact_failure": {
        "target": "补采夹持稳定与搬运过程",
        "episodes": 16,
        "tasks": ["慢速提升", "夹爪闭合确认", "搬运速度变化", "掉落后终止/恢复"],
    },
    "control_or_safety_failure": {
        "target": "补采避障与安全路径",
        "episodes": 14,
        "tasks": ["容器边缘避障", "桌面高度误差", "路径绕行", "碰撞前停止"],
    },
    "task_management_failure": {
        "target": "补采阶段切换与超时恢复",
        "episodes": 12,
        "tasks": ["超时重试", "阶段回退", "观察-决策暂停", "失败后 return_home"],
    },
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--failure_report", type=Path, required=True)
    parser.add_argument("--output_md", type=Path, required=True)
    parser.add_argument("--output_json", type=Path, default=None)
    args = parser.parse_args()

    report = json.loads(args.failure_report.read_text(encoding="utf-8"))
    category_counts = report.get("failure_category_distribution", {})
    total_failures = max(1, report.get("num_failures", 1))

    plan_items = []
    for category, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        base = CATEGORY_TO_PLAN.get(category, {
            "target": "人工复核未知失败",
            "episodes": 8,
            "tasks": ["查看日志", "回放轨迹", "补充人工标注"],
        })
        scale = max(1, round((count / total_failures) * 2))
        item = {
            "category": category,
            "failure_count": count,
            "target": base["target"],
            "recommended_episodes": base["episodes"] * scale,
            "tasks": base["tasks"],
        }
        plan_items.append(item)

    lines = [
        "# Next Data Collection Plan",
        "",
        "本计划由第 18 章失败分析脚本自动生成，用于从 policy_v1 的失败结果进入第二轮数据闭环。",
        "",
        "## Summary",
        "",
        f"- source_failures: `{report.get('num_failures')}`",
        f"- failure_rate: `{report.get('failure_rate')}`",
        "",
        "## Targeted Collection Plan",
        "",
        "| category | failure_count | target | recommended_episodes | tasks |",
        "|---|---:|---|---:|---|",
    ]
    for item in plan_items:
        lines.append(f"| `{item['category']}` | {item['failure_count']} | {item['target']} | {item['recommended_episodes']} | {'; '.join(item['tasks'])} |")
    lines += [
        "",
        "## Policy v2 Experiment Design",
        "",
        "1. 按上表补采 targeted episodes，形成 `dataset_v1_targeted`。",
        "2. 将 `dataset_v0` 与 `dataset_v1_targeted` 合并为 `dataset_v1`。",
        "3. 使用同一训练脚本训练 `policy_v2`。",
        "4. 使用第 17 章相同评测协议重新评测，避免评测口径变化。",
        "5. 对比 `policy_v1` 与 `policy_v2` 的 success rate、failure reason、intervention rate。",
    ]
    args.output_md.parent.mkdir(parents=True, exist_ok=True)
    args.output_md.write_text("\n".join(lines), encoding="utf-8")
    if args.output_json is not None:
        args.output_json.write_text(json.dumps({"plan_items": plan_items}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"num_plan_items": len(plan_items)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
