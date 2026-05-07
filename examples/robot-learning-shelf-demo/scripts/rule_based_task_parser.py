#!/usr/bin/env python3
"""Rule-based task parser for simple robot instructions.

This script converts simple natural language instructions into a structured task.
It is intentionally deterministic and constrained to help readers understand
why VLA systems still need structured task representations.
"""
from __future__ import annotations

from pathlib import Path
import argparse
import json
import re
from typing import Any

COLOR_PATTERNS = {
    'red': ['红色', '红', 'red'],
    'blue': ['蓝色', '蓝', 'blue'],
    'green': ['绿色', '绿', 'green'],
    'yellow': ['黄色', '黄', 'yellow'],
}

OBJECT_PATTERNS = {
    'box': ['盒子', '方块', 'box', 'cube'],
    'bottle': ['瓶子', 'bottle'],
}

TARGET_PATTERNS = {
    'right_storage_box': ['右边收纳盒', '右侧收纳盒', '右边盒子', 'right bin', 'right storage box'],
    'left_storage_box': ['左边收纳盒', '左侧收纳盒', 'left bin', 'left storage box'],
    'table_center': ['桌面中央', '中心区域', 'table center'],
}


def find_first_match(text: str, patterns: dict[str, list[str]]) -> str | None:
    for key, aliases in patterns.items():
        for item in aliases:
            if item.lower() in text.lower():
                return key
    return None


def infer_task_name(text: str) -> str:
    lowered = text.lower()
    if '放' in text or 'place' in lowered or 'put' in lowered:
        return 'pick_box_to_bin'
    if '移动' in text or 'move' in lowered:
        return 'move_object'
    return 'generic_pick_and_place'


def infer_constraints(text: str) -> dict[str, Any]:
    constraints: dict[str, Any] = {
        'workspace': 'table_top',
        'avoid_collision': True,
        'keep_upright': False,
        'max_time_sec': 30,
    }
    if '轻放' in text or '保持竖直' in text or 'upright' in text.lower():
        constraints['keep_upright'] = True
    if '快速' in text or '尽快' in text or 'quickly' in text.lower():
        constraints['max_time_sec'] = 10
    return constraints


def parse_instruction(text: str) -> dict[str, Any]:
    task_name = infer_task_name(text)
    color = find_first_match(text, COLOR_PATTERNS)
    obj_type = find_first_match(text, OBJECT_PATTERNS) or 'box'
    target = find_first_match(text, TARGET_PATTERNS)

    if target is None:
        if re.search(r'右', text):
            target = 'right_storage_box'
        elif re.search(r'左', text):
            target = 'left_storage_box'
        else:
            target = 'table_center'

    result = {
        'task_name': task_name,
        'instruction': text,
        'object': {
            'type': obj_type,
            'color': color,
        },
        'target': {
            'name': target,
        },
        'constraints': infer_constraints(text),
        'success_criteria': {
            'in_target': True,
            'released': True,
            'object_upright': '竖直' in text or 'upright' in text.lower(),
        },
    }
    return result


def maybe_dump_yaml(data: dict[str, Any]) -> str | None:
    try:
        import yaml  # type: ignore
    except Exception:
        return None
    return yaml.safe_dump(data, allow_unicode=True, sort_keys=False)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--instruction', type=str, required=True)
    parser.add_argument('--output_json', type=Path, default=None)
    parser.add_argument('--output_yaml', type=Path, default=None)
    args = parser.parse_args()

    parsed = parse_instruction(args.instruction)
    json_text = json.dumps(parsed, ensure_ascii=False, indent=2)
    print(json_text)

    if args.output_json is not None:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(json_text, encoding='utf-8')
        print(f'Saved JSON to: {args.output_json}')

    if args.output_yaml is not None:
        yaml_text = maybe_dump_yaml(parsed)
        if yaml_text is None:
            print('PyYAML not available, skip writing YAML file.')
        else:
            args.output_yaml.parent.mkdir(parents=True, exist_ok=True)
            args.output_yaml.write_text(yaml_text, encoding='utf-8')
            print(f'Saved YAML to: {args.output_yaml}')


if __name__ == '__main__':
    main()
