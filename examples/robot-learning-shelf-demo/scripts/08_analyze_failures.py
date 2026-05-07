#!/usr/bin/env python3
"""Analyze evaluation failures and produce a failure database.

Chapter 18 uses this script to turn eval CSV into actionable failure statistics.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


FAILURE_TAXONOMY = {
    "perception_miss": {
        "category": "perception_failure",
        "description": "目标检测、深度估计、遮挡或光照导致感知错误。",
        "recommended_action": "补采遮挡、光照变化、物体扰动样本；检查相机与标注质量。",
    },
    "grasp_offset": {
        "category": "strategy_failure",
        "description": "抓取点或接近姿态偏移，导致抓空或夹持不稳定。",
        "recommended_action": "补采接近/对齐阶段数据；加入 pre-grasp 对齐与修正动作。",
    },
    "drop_during_transfer": {
        "category": "control_or_contact_failure",
        "description": "物体在搬运阶段掉落，可能与夹爪闭合、路径或速度有关。",
        "recommended_action": "补采慢速搬运、夹持确认、提升高度变化样本；检查夹爪控制。",
    },
    "collision_risk": {
        "category": "control_or_safety_failure",
        "description": "路径与桌面、容器或障碍物存在碰撞风险。",
        "recommended_action": "补采避障、容器边缘、路径绕行数据；增加安全约束。",
    },
    "timeout": {
        "category": "task_management_failure",
        "description": "任务长时间未完成，可能因策略犹豫或阶段切换失败。",
        "recommended_action": "补采阶段切换和失败恢复数据；加入超时退出与重试逻辑。",
    },
}


def read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def analyze(rows: list[dict[str, Any]]) -> dict[str, Any]:
    failures = [r for r in rows if int(r.get("success", "0")) == 0]
    reason_counter = Counter(r.get("failure_reason", "unknown") for r in failures)
    category_counter = Counter()
    scenario_counter: dict[str, Counter] = defaultdict(Counter)
    failure_db = []
    for r in failures:
        reason = r.get("failure_reason", "unknown")
        tax = FAILURE_TAXONOMY.get(reason, {
            "category": "unknown_failure",
            "description": "未知失败，需要人工复核。",
            "recommended_action": "抽样查看轨迹、图像和动作日志。",
        })
        category_counter[tax["category"]] += 1
        scenario_counter[r.get("scenario_type", "unknown")][reason] += 1
        failure_db.append({
            "trial_id": int(r["trial_id"]),
            "scenario_type": r.get("scenario_type"),
            "failure_reason": reason,
            "category": tax["category"],
            "description": tax["description"],
            "recommended_action": tax["recommended_action"],
            "object_x": float(r.get("object_x", 0.0)),
            "object_y": float(r.get("object_y", 0.0)),
            "lighting_scale": float(r.get("lighting_scale", 1.0)),
        })

    return {
        "num_trials": len(rows),
        "num_failures": len(failures),
        "failure_rate": round(len(failures) / len(rows), 4) if rows else 0.0,
        "failure_reason_distribution": dict(reason_counter),
        "failure_category_distribution": dict(category_counter),
        "scenario_failure_distribution": {k: dict(v) for k, v in scenario_counter.items()},
        "failure_database": failure_db,
    }


def write_markdown(report: dict[str, Any], path: Path) -> None:
    lines = [
        "# Failure Analysis Report",
        "",
        f"- num_trials: `{report['num_trials']}`",
        f"- num_failures: `{report['num_failures']}`",
        f"- failure_rate: `{report['failure_rate']}`",
        "",
        "## Failure Reason Distribution",
        "",
    ]
    for k, v in sorted(report["failure_reason_distribution"].items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"- `{k}`: {v}")
    lines += ["", "## Failure Category Distribution", ""]
    for k, v in sorted(report["failure_category_distribution"].items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"- `{k}`: {v}")
    lines += ["", "## Top Failure Cases", ""]
    for item in report["failure_database"][:10]:
        lines.append(f"- trial `{item['trial_id']}` | `{item['scenario_type']}` | `{item['failure_reason']}` -> {item['recommended_action']}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval_csv", type=Path, required=True)
    parser.add_argument("--output_json", type=Path, required=True)
    parser.add_argument("--output_md", type=Path, required=True)
    args = parser.parse_args()

    rows = read_csv(args.eval_csv)
    report = analyze(rows)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(report, args.output_md)
    print(json.dumps({k: report[k] for k in ["num_trials", "num_failures", "failure_rate"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
