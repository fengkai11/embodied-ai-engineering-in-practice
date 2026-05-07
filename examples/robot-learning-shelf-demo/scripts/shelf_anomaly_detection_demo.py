#!/usr/bin/env python3
"""Chapter 19: simplified shelf anomaly detection demo.

Given a compact shelf state, classify each slot as:
- normal
- missing
- misplaced
- tilted

This is a teaching script, not a production perception pipeline.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


@dataclass
class ShelfSlot:
    slot_id: str
    expected_sku: str
    observed_sku: str | None
    tilt_deg: float
    occupancy: float


@dataclass
class SlotResult:
    slot_id: str
    expected_sku: str
    observed_sku: str | None
    status: str
    tilt_deg: float
    note: str


def default_shelf_state() -> list[ShelfSlot]:
    return [
        ShelfSlot('A1', 'tea_01', 'tea_01', 2.0, 1.0),
        ShelfSlot('A2', 'tea_02', None, 0.0, 0.0),
        ShelfSlot('A3', 'juice_01', 'juice_02', 4.0, 1.0),
        ShelfSlot('B1', 'milk_01', 'milk_01', 18.5, 1.0),
        ShelfSlot('B2', 'milk_02', 'milk_02', 3.0, 1.0),
        ShelfSlot('B3', 'snack_01', 'snack_01', 1.0, 1.0),
    ]


def classify_slot(slot: ShelfSlot, tilt_threshold_deg: float = 10.0) -> SlotResult:
    if slot.occupancy < 0.2 or slot.observed_sku is None:
        return SlotResult(slot.slot_id, slot.expected_sku, slot.observed_sku, 'missing', slot.tilt_deg, '格口空缺或占用率过低')
    if slot.observed_sku != slot.expected_sku:
        return SlotResult(slot.slot_id, slot.expected_sku, slot.observed_sku, 'misplaced', slot.tilt_deg, '观察商品与目标 SKU 不一致')
    if slot.tilt_deg > tilt_threshold_deg:
        return SlotResult(slot.slot_id, slot.expected_sku, slot.observed_sku, 'tilted', slot.tilt_deg, '商品倾角过大，需扶正')
    return SlotResult(slot.slot_id, slot.expected_sku, slot.observed_sku, 'normal', slot.tilt_deg, '状态正常')


def summarize(results: list[SlotResult]) -> dict[str, Any]:
    counts: dict[str, int] = {'normal': 0, 'missing': 0, 'misplaced': 0, 'tilted': 0}
    for r in results:
        counts[r.status] = counts.get(r.status, 0) + 1
    if counts['missing'] > 0:
        priority = 'restock_missing_items'
    elif counts['misplaced'] > 0:
        priority = 'correct_wrong_slot_items'
    elif counts['tilted'] > 0:
        priority = 'straighten_tilted_items'
    else:
        priority = 'no_action_required'
    return {
        'num_slots': len(results),
        'status_counter': counts,
        'priority_action': priority,
        'action_order': [
            'missing -> 补货',
            'misplaced -> 调整格口',
            'tilted -> 扶正并对齐',
        ],
    }


def write_markdown(results: list[SlotResult], summary: dict[str, Any], path: Path) -> None:
    lines = [
        '# Chapter 19 Shelf Anomaly Report',
        '',
        f"- num_slots: `{summary['num_slots']}`",
        f"- status_counter: `{summary['status_counter']}`",
        f"- priority_action: `{summary['priority_action']}`",
        '',
        '## Per-slot Result',
        '',
        '| slot_id | expected_sku | observed_sku | status | tilt_deg | note |',
        '|---|---|---|---|---:|---|',
    ]
    for r in results:
        lines.append(f"| {r.slot_id} | {r.expected_sku} | {r.observed_sku} | {r.status} | {r.tilt_deg:.1f} | {r.note} |")
    lines += [
        '',
        '## Interpretation',
        '',
        '本报告展示了理货机器人中的一个典型前置问题：在进行扶正、补货或抓取前，系统首先需要知道每个格口处于什么状态。',
        '在真实系统中，`missing / misplaced / tilted / normal` 的判断会由多模态感知模块完成；此处使用教学化规则脚本，帮助读者先理解数据结构与任务分解。',
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('\n'.join(lines), encoding='utf-8')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_json', type=Path, required=True)
    parser.add_argument('--output_md', type=Path, required=True)
    parser.add_argument('--tilt_threshold_deg', type=float, default=10.0)
    args = parser.parse_args()

    shelf = default_shelf_state()
    results = [classify_slot(slot, args.tilt_threshold_deg) for slot in shelf]
    summary = summarize(results)
    payload = {
        'shelf_slots': [asdict(s) for s in shelf],
        'results': [asdict(r) for r in results],
        'summary': summary,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    write_markdown(results, summary, args.output_md)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
