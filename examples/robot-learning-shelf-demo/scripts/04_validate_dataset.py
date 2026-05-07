#!/usr/bin/env python3
"""Validate an episode dataset and generate summary reports."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ACTION_LIMITS = {
    'dx': (-0.20, 0.20),
    'dy': (-0.20, 0.20),
    'dz': (-0.20, 0.20),
    'gripper_delta': (-1.0, 1.0),
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def check_episode(ep_dir: Path) -> dict[str, Any]:
    issues: list[str] = []
    warnings: list[str] = []
    meta_path = ep_dir / 'meta.json'
    states_path = ep_dir / 'states.jsonl'
    actions_path = ep_dir / 'actions.jsonl'
    front_dir = ep_dir / 'images' / 'front'
    wrist_dir = ep_dir / 'images' / 'wrist'

    meta = None
    states: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []

    if not meta_path.exists():
        issues.append('missing meta.json')
    else:
        meta = load_json(meta_path)

    if not states_path.exists():
        issues.append('missing states.jsonl')
    else:
        states = load_jsonl(states_path)

    if not actions_path.exists():
        issues.append('missing actions.jsonl')
    else:
        actions = load_jsonl(actions_path)

    if not front_dir.exists():
        issues.append('missing images/front directory')
    if not wrist_dir.exists():
        warnings.append('missing images/wrist directory')

    front_count = len(list(front_dir.glob('*.png'))) if front_dir.exists() else 0
    wrist_count = len(list(wrist_dir.glob('*.png'))) if wrist_dir.exists() else 0

    if meta is not None:
        if meta.get('success') is True and meta.get('failure_reason') not in [None, '', 'none']:
            issues.append('label conflict: success=true but failure_reason is non-empty')
        if meta.get('success') is False and meta.get('failure_reason') in [None, '', 'none']:
            warnings.append('success=false but failure_reason is empty')
        if 'num_steps' in meta and states and len(states) != meta['num_steps']:
            issues.append(f"states length {len(states)} != num_steps {meta['num_steps']}")
        if 'num_steps' in meta and actions and len(actions) != meta['num_steps']:
            issues.append(f"actions length {len(actions)} != num_steps {meta['num_steps']}")

    if states and actions:
        state_ts = [row['timestamp'] for row in states]
        action_ts = [row['timestamp'] for row in actions]
        if state_ts != sorted(state_ts):
            issues.append('state timestamps are not monotonically increasing')
        if action_ts != sorted(action_ts):
            issues.append('action timestamps are not monotonically increasing')
        if len(state_ts) == len(action_ts) and state_ts != action_ts:
            issues.append('state timestamps do not match action timestamps')

    if states and front_count not in (0, len(states)):
        issues.append(f'front image count {front_count} != state count {len(states)}')
    if states and wrist_count not in (0, len(states)):
        issues.append(f'wrist image count {wrist_count} != state count {len(states)}')

    out_of_range_samples = []
    for row in actions:
        vec = row.get('delta_ee_xyzrpy', [0, 0, 0, 0, 0, 0])
        mapping = {'dx': vec[0], 'dy': vec[1], 'dz': vec[2], 'gripper_delta': row.get('gripper_delta', 0.0)}
        for name, value in mapping.items():
            lower, upper = ACTION_LIMITS[name]
            if value < lower or value > upper:
                out_of_range_samples.append({'t': row.get('t'), 'field': name, 'value': value, 'limit': [lower, upper]})
    if out_of_range_samples:
        issues.append(f'action out of range: {len(out_of_range_samples)} sample(s)')

    return {
        'episode_id': ep_dir.name,
        'ok': len(issues) == 0,
        'issues': issues,
        'warnings': warnings,
        'front_image_count': front_count,
        'wrist_image_count': wrist_count,
        'num_states': len(states),
        'num_actions': len(actions),
        'success': None if meta is None else meta.get('success'),
        'failure_reason': None if meta is None else meta.get('failure_reason'),
        'task_name': None if meta is None else meta.get('task_name'),
        'action_out_of_range_samples': out_of_range_samples,
    }


def gather_action_values(dataset_dir: Path) -> dict[str, list[float]]:
    values = {'dx': [], 'dy': [], 'dz': [], 'gripper_delta': []}
    for ep_dir in sorted([p for p in dataset_dir.iterdir() if p.is_dir()]):
        ap = ep_dir / 'actions.jsonl'
        if not ap.exists():
            continue
        for row in load_jsonl(ap):
            vec = row.get('delta_ee_xyzrpy', [0, 0, 0, 0, 0, 0])
            values['dx'].append(vec[0])
            values['dy'].append(vec[1])
            values['dz'].append(vec[2])
            values['gripper_delta'].append(row.get('gripper_delta', 0.0))
    return values


def maybe_plot_action_distribution(values: dict[str, list[float]], output_path: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        print('matplotlib not available, skip plotting.')
        return
    keys = ['dx', 'dy', 'dz', 'gripper_delta']
    labels = ['dx', 'dy', 'dz', 'gripper_delta']
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    axes = axes.ravel()
    for ax, key, label in zip(axes, keys, labels):
        ax.hist(values[key], bins=20)
        ax.set_title(f'{label} distribution')
        ax.set_xlabel(label)
        ax.set_ylabel('count')
        if key in ACTION_LIMITS:
            lower, upper = ACTION_LIMITS[key]
            ax.axvline(lower, linestyle='--')
            ax.axvline(upper, linestyle='--')
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    print(f'Saved plot to: {output_path}')


def write_markdown_report(report: dict[str, Any], output_path: Path) -> None:
    lines = [
        '# Dataset Validation Report',
        '',
        f"- dataset_dir: `{report['dataset_dir']}`",
        f"- total_episodes: `{report['summary']['total_episodes']}`",
        f"- ok_episodes: `{report['summary']['ok_episodes']}`",
        f"- bad_episodes: `{report['summary']['bad_episodes']}`",
        '',
        '## Episode Results',
        '',
    ]
    for item in report['episodes']:
        mark = '✅' if item['ok'] else '❌'
        lines.append(f"### {mark} {item['episode_id']}")
        lines.append('')
        lines.append(f"- task_name: `{item['task_name']}`")
        lines.append(f"- success: `{item['success']}`")
        lines.append(f"- failure_reason: `{item['failure_reason']}`")
        lines.append(f"- num_states: `{item['num_states']}`")
        lines.append(f"- num_actions: `{item['num_actions']}`")
        lines.append(f"- front_image_count: `{item['front_image_count']}`")
        lines.append(f"- wrist_image_count: `{item['wrist_image_count']}`")
        if item['issues']:
            lines.append('- issues:')
            for x in item['issues']:
                lines.append(f'  - {x}')
        else:
            lines.append('- issues: none')
        if item['warnings']:
            lines.append('- warnings:')
            for x in item['warnings']:
                lines.append(f'  - {x}')
        lines.append('')
    output_path.write_text('\n'.join(lines), encoding='utf-8')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_dir', type=Path, required=True)
    parser.add_argument('--output_json', type=Path, required=True)
    parser.add_argument('--output_md', type=Path, required=True)
    parser.add_argument('--plot_path', type=Path, required=True)
    args = parser.parse_args()

    episodes = [p for p in sorted(args.dataset_dir.iterdir()) if p.is_dir()]
    results = [check_episode(ep) for ep in episodes]
    report = {
        'dataset_dir': str(args.dataset_dir),
        'summary': {
            'total_episodes': len(results),
            'ok_episodes': sum(1 for x in results if x['ok']),
            'bad_episodes': sum(1 for x in results if not x['ok']),
        },
        'episodes': results,
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    write_markdown_report(report, args.output_md)
    values = gather_action_values(args.dataset_dir)
    maybe_plot_action_distribution(values, args.plot_path)
    print(json.dumps(report['summary'], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
