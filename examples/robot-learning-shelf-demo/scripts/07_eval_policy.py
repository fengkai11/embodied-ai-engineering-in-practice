#!/usr/bin/env python3
"""Evaluate policy_v1 on simulated pick-and-place trials.

This is a teaching evaluation script for Chapter 17. It does not require a real
robot. It uses deterministic scenario generation and a stochastic simulated
policy profile to explain how success rate, completion time, collision rate,
drop rate, intervention rate and failure reason distribution are recorded.
"""
from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

SCENARIO_TYPES = ["fixed", "random_position", "lighting_shift", "object_shift"]


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def scenario_config(trial_id: int, scenario_type: str, rng: random.Random) -> dict[str, Any]:
    if scenario_type == "fixed":
        obj = [0.40, 0.04, 0.02]
        lighting = 1.0
        difficulty = 0.10
    elif scenario_type == "random_position":
        obj = [rng.uniform(0.33, 0.48), rng.uniform(-0.05, 0.10), 0.02]
        lighting = 1.0
        difficulty = 0.25
    elif scenario_type == "lighting_shift":
        obj = [rng.uniform(0.35, 0.45), rng.uniform(-0.04, 0.08), 0.02]
        lighting = rng.choice([0.55, 0.70, 1.35, 1.55])
        difficulty = 0.40
    else:
        obj = [rng.uniform(0.30, 0.52), rng.uniform(-0.08, 0.12), 0.02]
        lighting = rng.uniform(0.65, 1.45)
        difficulty = 0.55
    return {
        "trial_id": trial_id,
        "scenario_type": scenario_type,
        "object_pose_xyz": [round(v, 4) for v in obj],
        "lighting_scale": round(lighting, 3),
        "difficulty": difficulty,
    }


def simulate_policy_trial(policy_name: str, scenario: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    """Simulate one trial.

    The profile is intentionally simple and explainable:
    - fixed scenes are easiest;
    - lighting/object shifts increase perception and placement errors;
    - policy_v2 is slightly more robust than policy_v1.
    """
    base_success = 0.88
    if policy_name.endswith("v2"):
        base_success += 0.08

    difficulty = scenario["difficulty"]
    success_prob = clamp(base_success - 0.55 * difficulty + rng.uniform(-0.06, 0.06), 0.05, 0.98)

    roll = rng.random()
    success = roll < success_prob

    failure_reason = ""
    collision = False
    dropped = False
    intervention = 0

    if success:
        completion_time = rng.uniform(6.0, 10.0) + difficulty * 4.0
    else:
        # Choose failure mode according to scenario difficulty.
        weights = {
            "perception_miss": 0.25 + 0.40 * (scenario["scenario_type"] in ["lighting_shift", "object_shift"]),
            "grasp_offset": 0.25 + 0.25 * (scenario["scenario_type"] == "random_position"),
            "drop_during_transfer": 0.20 + 0.15 * difficulty,
            "collision_risk": 0.15 + 0.10 * difficulty,
            "timeout": 0.15,
        }
        total = sum(weights.values())
        r = rng.random() * total
        acc = 0.0
        failure_reason = "timeout"
        for k, w in weights.items():
            acc += w
            if r <= acc:
                failure_reason = k
                break
        collision = failure_reason == "collision_risk"
        dropped = failure_reason == "drop_during_transfer"
        intervention = 1 if failure_reason in {"collision_risk", "timeout"} else 0
        completion_time = rng.uniform(8.0, 16.0) + difficulty * 5.0

    return {
        "trial_id": scenario["trial_id"],
        "policy_name": policy_name,
        "scenario_type": scenario["scenario_type"],
        "object_x": scenario["object_pose_xyz"][0],
        "object_y": scenario["object_pose_xyz"][1],
        "lighting_scale": scenario["lighting_scale"],
        "success": int(success),
        "completion_time_sec": round(completion_time, 3),
        "collision": int(collision),
        "dropped": int(dropped),
        "intervention_count": intervention,
        "failure_reason": failure_reason,
    }


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    n = len(rows)
    success_count = sum(int(r["success"]) for r in rows)
    collision_count = sum(int(r["collision"]) for r in rows)
    drop_count = sum(int(r["dropped"]) for r in rows)
    intervention_trials = sum(1 for r in rows if int(r["intervention_count"]) > 0)
    failure_counter = Counter(r["failure_reason"] for r in rows if not int(r["success"]))
    by_scenario: dict[str, dict[str, Any]] = {}
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        grouped[r["scenario_type"]].append(r)
    for scenario, items in sorted(grouped.items()):
        by_scenario[scenario] = {
            "num_trials": len(items),
            "success_rate": round(sum(int(x["success"]) for x in items) / len(items), 4),
            "mean_completion_time_sec": round(sum(float(x["completion_time_sec"]) for x in items) / len(items), 3),
        }
    return {
        "num_trials": n,
        "success_count": success_count,
        "success_rate": round(success_count / n, 4) if n else 0.0,
        "collision_rate": round(collision_count / n, 4) if n else 0.0,
        "drop_rate": round(drop_count / n, 4) if n else 0.0,
        "intervention_rate": round(intervention_trials / n, 4) if n else 0.0,
        "mean_completion_time_sec": round(sum(float(r["completion_time_sec"]) for r in rows) / n, 3) if n else 0.0,
        "failure_reason_distribution": dict(failure_counter),
        "by_scenario": by_scenario,
    }


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_markdown(summary: dict[str, Any], policy_name: str, path: Path) -> None:
    lines = [
        f"# Experiment Report: {policy_name}",
        "",
        f"- num_trials: `{summary['num_trials']}`",
        f"- success_rate: `{summary['success_rate']}`",
        f"- mean_completion_time_sec: `{summary['mean_completion_time_sec']}`",
        f"- collision_rate: `{summary['collision_rate']}`",
        f"- drop_rate: `{summary['drop_rate']}`",
        f"- intervention_rate: `{summary['intervention_rate']}`",
        "",
        "## By Scenario",
        "",
        "| scenario | trials | success_rate | mean_time_sec |",
        "|---|---:|---:|---:|",
    ]
    for scenario, item in summary["by_scenario"].items():
        lines.append(f"| {scenario} | {item['num_trials']} | {item['success_rate']} | {item['mean_completion_time_sec']} |")
    lines += ["", "## Failure Reasons", ""]
    if summary["failure_reason_distribution"]:
        for k, v in sorted(summary["failure_reason_distribution"].items(), key=lambda x: (-x[1], x[0])):
            lines.append(f"- `{k}`: {v}")
    else:
        lines.append("- none")
    lines += [
        "",
        "## Interpretation",
        "",
        "本报告用于说明机器人策略评测不能只看单次成功视频，而应基于固定协议、重复 trials、结构化 CSV 与失败原因分布进行判断。",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--policy_name", type=str, default="policy_v1")
    parser.add_argument("--num_trials", type=int, default=40)
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--output_csv", type=Path, required=True)
    parser.add_argument("--summary_json", type=Path, required=True)
    parser.add_argument("--report_md", type=Path, required=True)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    rows = []
    for i in range(args.num_trials):
        scenario_type = SCENARIO_TYPES[i % len(SCENARIO_TYPES)]
        scenario = scenario_config(i + 1, scenario_type, rng)
        rows.append(simulate_policy_trial(args.policy_name, scenario, rng))

    summary = aggregate(rows)
    args.summary_json.parent.mkdir(parents=True, exist_ok=True)
    args.summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(rows, args.output_csv)
    write_markdown(summary, args.policy_name, args.report_md)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
