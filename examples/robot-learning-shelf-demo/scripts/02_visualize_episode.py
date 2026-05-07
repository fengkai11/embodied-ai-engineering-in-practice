#!/usr/bin/env python3
"""Visualize and summarize one synthetic episode."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import argparse
import json
from typing import Any


@dataclass
class EpisodeSummary:
    episode_id: str
    task_name: str
    success: bool
    failure_reason: str | None
    num_steps: int
    phases: list[str]
    gripper_closed_steps: list[int]
    front_frames: int
    wrist_frames: int


def load_json(path: Path) -> Any:
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


def load_episode(episode_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    meta = load_json(episode_dir / 'meta.json')
    states = load_jsonl(episode_dir / 'states.jsonl')
    actions = load_jsonl(episode_dir / 'actions.jsonl')
    return meta, states, actions


def summarize_episode(episode_dir: Path, meta: dict[str, Any], states: list[dict[str, Any]]) -> EpisodeSummary:
    phases = [row['phase'] for row in states]
    gripper_closed_steps = [row['t'] for row in states if not row['gripper_open']]
    front_frames = len(list((episode_dir / 'images' / 'front').glob('*.png')))
    wrist_frames = len(list((episode_dir / 'images' / 'wrist').glob('*.png')))
    return EpisodeSummary(
        episode_id=meta['episode_id'],
        task_name=meta['task_name'],
        success=meta['success'],
        failure_reason=meta.get('failure_reason'),
        num_steps=meta['num_steps'],
        phases=phases,
        gripper_closed_steps=gripper_closed_steps,
        front_frames=front_frames,
        wrist_frames=wrist_frames,
    )


def check_episode_integrity(episode_dir: Path, meta: dict[str, Any], states: list[dict[str, Any]], actions: list[dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    if len(states) != meta['num_steps']:
        issues.append(f'states length {len(states)} != num_steps {meta["num_steps"]}')
    if len(actions) != meta['num_steps']:
        issues.append(f'actions length {len(actions)} != num_steps {meta["num_steps"]}')
    if len(list((episode_dir / 'images' / 'front').glob('*.png'))) != len(states):
        issues.append('front image count != state count')
    if len(list((episode_dir / 'images' / 'wrist').glob('*.png'))) != len(states):
        issues.append('wrist image count != state count')
    state_ts = [row['timestamp'] for row in states]
    action_ts = [row['timestamp'] for row in actions]
    if state_ts != sorted(state_ts):
        issues.append('state timestamps are not monotonically increasing')
    if action_ts != sorted(action_ts):
        issues.append('action timestamps are not monotonically increasing')
    if state_ts != action_ts:
        issues.append('state timestamps do not match action timestamps')
    return issues


def write_summary_markdown(summary: EpisodeSummary, issues: list[str], output_path: Path) -> None:
    lines = [
        f'# Episode Summary: {summary.episode_id}',
        '',
        f'- task_name: `{summary.task_name}`',
        f'- success: `{summary.success}`',
        f'- failure_reason: `{summary.failure_reason}`',
        f'- num_steps: `{summary.num_steps}`',
        f'- front_frames: `{summary.front_frames}`',
        f'- wrist_frames: `{summary.wrist_frames}`',
        f'- phases: `{" -> ".join(summary.phases)}`',
        f'- gripper_closed_steps: `{summary.gripper_closed_steps}`',
        '',
        '## Integrity Check',
        '',
    ]
    if issues:
        lines.extend([f'- [ ] {x}' for x in issues])
    else:
        lines.append('- [x] No integrity issues found.')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text('\n'.join(lines), encoding='utf-8')


def print_episode_summary(summary: EpisodeSummary, issues: list[str]) -> None:
    print('=' * 72)
    print(f'Episode ID          : {summary.episode_id}')
    print(f'Task                : {summary.task_name}')
    print(f'Success             : {summary.success}')
    print(f'Failure reason      : {summary.failure_reason}')
    print(f'Num steps           : {summary.num_steps}')
    print(f'Phases              : {" -> ".join(summary.phases)}')
    print(f'Gripper closed steps: {summary.gripper_closed_steps}')
    print(f'Front frames        : {summary.front_frames}')
    print(f'Wrist frames        : {summary.wrist_frames}')
    print('Integrity issues    : none' if not issues else 'Integrity issues    :')
    for item in issues:
        print(f'  - {item}')
    print('=' * 72)


def maybe_plot_actions(actions: list[dict[str, Any]], output_path: Path | None) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        print('matplotlib is not available; skip plotting.')
        return

    steps = [row['t'] for row in actions]
    dx = [row['delta_ee_xyzrpy'][0] for row in actions]
    dy = [row['delta_ee_xyzrpy'][1] for row in actions]
    dz = [row['delta_ee_xyzrpy'][2] for row in actions]
    dg = [row['gripper_delta'] for row in actions]

    plt.figure(figsize=(9, 5))
    plt.plot(steps, dx, marker='o', label='dx')
    plt.plot(steps, dy, marker='o', label='dy')
    plt.plot(steps, dz, marker='o', label='dz')
    plt.plot(steps, dg, marker='o', label='gripper_delta')
    plt.xlabel('Step t')
    plt.ylabel('Action value')
    plt.title('Synthetic episode action timeline')
    plt.legend()
    plt.tight_layout()
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(output_path)
        print(f'Saved plot to: {output_path}')
    else:
        plt.show()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--episode_dir', type=Path, required=True)
    parser.add_argument('--save_plot', type=Path, default=None)
    parser.add_argument('--save_summary', type=Path, default=None)
    args = parser.parse_args()

    meta, states, actions = load_episode(args.episode_dir)
    summary = summarize_episode(args.episode_dir, meta, states)
    issues = check_episode_integrity(args.episode_dir, meta, states, actions)
    print_episode_summary(summary, issues)
    maybe_plot_actions(actions, args.save_plot)
    if args.save_summary is not None:
        write_summary_markdown(summary, issues, args.save_summary)
        print(f'Saved summary to: {args.save_summary}')


if __name__ == '__main__':
    main()
