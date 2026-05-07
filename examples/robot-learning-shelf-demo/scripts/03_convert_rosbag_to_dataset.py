#!/usr/bin/env python3
"""Convert a mock rosbag jsonl file to episode-style dataset directory.

The input is a simplified stand-in for rosbag. Each line contains:
{
  "topic": "/joint_states",
  "timestamp": 1.23,
  "data": {...}
}
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def group_by_topic(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        groups.setdefault(row['topic'], []).append(row)
    for k in groups:
        groups[k] = sorted(groups[k], key=lambda x: x['timestamp'])
    return groups


def resample_streams(groups: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    front = groups.get('/camera/front/image_raw', [])
    wrist = groups.get('/camera/wrist/image_raw', [])
    joint = groups.get('/joint_states', [])
    action = groups.get('/action_cmd', [])
    task = groups.get('/task_info', [])
    n = min(len(front), len(joint), len(action))
    steps: list[dict[str, Any]] = []
    for i in range(n):
        ts = front[i]['timestamp']
        task_info = task[min(i, len(task)-1)]['data'] if task else {'instruction': 'Pick the box and place it into the bin.'}
        wrist_row = wrist[min(i, len(wrist)-1)] if wrist else None
        steps.append({
            't': i,
            'timestamp': ts,
            'front_frame_name': front[i]['data']['frame_name'],
            'wrist_frame_name': None if wrist_row is None else wrist_row['data']['frame_name'],
            'state': joint[i]['data'],
            'action': action[i]['data'],
            'task_info': task_info,
        })
    return steps


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


def maybe_import_pil():
    try:
        from PIL import Image, ImageDraw
        return Image, ImageDraw
    except Exception as exc:
        raise RuntimeError('Pillow is required to create placeholder images.') from exc


def render_placeholder(save_path: Path, label: str, step: int, color: tuple[int, int, int]) -> None:
    Image, ImageDraw = maybe_import_pil()
    img = Image.new('RGB', (320, 240), (248, 250, 252))
    draw = ImageDraw.Draw(img)
    draw.rectangle([30, 90, 290, 220], fill=(223, 183, 122), outline=(120, 90, 60), width=3)
    draw.rectangle([220, 80, 285, 140], fill=(180, 185, 190), outline=(90, 95, 100), width=3)
    x = 80 + step * 18
    y = 160 - step * 8
    draw.rectangle([x-12, y-12, x+12, y+12], fill=color, outline=(80, 40, 40), width=2)
    draw.text((10, 10), f'{label} | step={step}', fill=(20, 50, 110))
    save_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(save_path)


def convert(rows: list[dict[str, Any]], output_episode_dir: Path) -> dict[str, Any]:
    groups = group_by_topic(rows)
    steps = resample_streams(groups)

    meta = {
        'episode_id': output_episode_dir.name,
        'task_name': 'pick_box_to_bin',
        'instruction': steps[0]['task_info'].get('instruction', 'Pick the box and place it into the bin.') if steps else 'unknown',
        'success': True,
        'failure_reason': None,
        'num_steps': len(steps),
        'dataset_version': 'v0.3_from_mock_rosbag',
        'source': 'mock_rosbag_jsonl',
    }

    states = []
    actions = []
    for row in steps:
        states.append({
            't': row['t'],
            'timestamp': row['timestamp'],
            'ee_pose_xyzrpy': row['state']['ee_pose_xyzrpy'],
            'gripper_open': row['state']['gripper_open'],
            'object_pose_xyz': row['state']['object_pose_xyz'],
            'bin_pose_xyz': row['state']['bin_pose_xyz'],
            'phase': row['state']['phase'],
        })
        actions.append({
            't': row['t'],
            'timestamp': row['timestamp'],
            'delta_ee_xyzrpy': row['action']['delta_ee_xyzrpy'],
            'gripper_delta': row['action']['gripper_delta'],
            'comment': row['action']['comment'],
        })

    write_json(output_episode_dir/'meta.json', meta)
    write_jsonl(output_episode_dir/'states.jsonl', states)
    write_jsonl(output_episode_dir/'actions.jsonl', actions)

    for i, row in enumerate(steps):
        render_placeholder(output_episode_dir/'images'/'front'/row['front_frame_name'], 'front camera', i, (220, 60, 60))
        wrist_name = row['wrist_frame_name'] or f'frame_{i:04d}.png'
        render_placeholder(output_episode_dir/'images'/'wrist'/wrist_name, 'wrist camera', i, (60, 110, 220))

    return {
        'episode_dir': str(output_episode_dir),
        'num_steps': len(steps),
        'topics': sorted(list(groups.keys())),
        'front_frames': len(list((output_episode_dir/'images'/'front').glob('*.png'))),
        'wrist_frames': len(list((output_episode_dir/'images'/'wrist').glob('*.png'))),
    }


def write_summary_md(summary: dict[str, Any], path: Path) -> None:
    lines = [
        '# Mock rosbag Conversion Summary',
        '',
        f"- episode_dir: `{summary['episode_dir']}`",
        f"- num_steps: `{summary['num_steps']}`",
        f"- front_frames: `{summary['front_frames']}`",
        f"- wrist_frames: `{summary['wrist_frames']}`",
        '- topics:',
    ]
    for topic in summary['topics']:
        lines.append(f'  - `{topic}`')
    path.write_text('\n'.join(lines), encoding='utf-8')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--bag_jsonl', type=Path, required=True)
    parser.add_argument('--output_episode_dir', type=Path, required=True)
    parser.add_argument('--summary_md', type=Path, required=True)
    args = parser.parse_args()
    rows = load_jsonl(args.bag_jsonl)
    summary = convert(rows, args.output_episode_dir)
    write_summary_md(summary, args.summary_md)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
