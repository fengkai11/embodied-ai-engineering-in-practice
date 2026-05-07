#!/usr/bin/env python3
"""Generate scripted pick-and-place episodes for Chapter 13.

The goal is not physical realism, but to create a clear bridge between:
- a rule-based expert policy,
- a finite-state pick-and-place routine,
- and the episode data format used later for training.
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Any

from robot_arm_interface import MockRobotArm

try:
    from PIL import Image, ImageDraw
except Exception:  # pragma: no cover
    Image = None
    ImageDraw = None

HOME_POSE = [0.30, -0.10, 0.25, 3.14, 0.0, 0.0]
BIN_POSE = [0.62, -0.08, 0.04]


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def pose_from_xyz(xyz: list[float]) -> list[float]:
    return [xyz[0], xyz[1], xyz[2], 3.14, 0.0, 0.0]


def render_frame(output_path: Path, ee_xyz: list[float], obj_xyz: list[float], bin_xyz: list[float], phase: str, grasped: bool) -> None:
    if Image is None or ImageDraw is None:
        return
    img = Image.new('RGB', (320, 240), color=(245, 247, 250))
    draw = ImageDraw.Draw(img)
    draw.rectangle([30, 170, 290, 210], outline=(90, 90, 90), fill=(230, 230, 230))
    draw.rectangle([215, 130, 290, 190], outline=(60, 100, 180), fill=(66, 124, 201))

    def world_to_px(x: float, y: float) -> tuple[int, int]:
        px = int(70 + (x - 0.20) / 0.50 * 180)
        py = int(170 - (y + 0.35) / 0.60 * 90)
        return px, py

    objx, objy = world_to_px(obj_xyz[0], obj_xyz[1])
    eex, _ = world_to_px(ee_xyz[0], ee_xyz[1])
    ee_top = max(25, int(140 - ee_xyz[2] * 250))

    if not grasped:
        draw.rectangle([objx - 12, objy - 12, objx + 12, objy + 12], outline=(120, 70, 30), fill=(190, 140, 90))
    else:
        objy = ee_top + 24
        draw.rectangle([eex - 10, objy - 10, eex + 10, objy + 10], outline=(120, 70, 30), fill=(190, 140, 90))

    draw.line([eex, 30, eex, ee_top], fill=(70, 70, 70), width=4)
    draw.line([eex, ee_top, eex - 8, ee_top + 14], fill=(40, 40, 40), width=3)
    draw.line([eex, ee_top, eex + 8, ee_top + 14], fill=(40, 40, 40), width=3)
    draw.text((12, 10), f'phase: {phase}', fill=(20, 20, 20))
    draw.text((12, 28), f'ee_xyz: {[round(v, 3) for v in ee_xyz]}', fill=(20, 20, 20))
    draw.text((12, 46), f'obj_xyz: {[round(v, 3) for v in obj_xyz]}', fill=(20, 20, 20))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)


def make_state(t: int, timestamp: float, ee_pose: list[float], gripper_open: bool, obj_xyz: list[float], phase: str) -> dict[str, Any]:
    return {
        't': t,
        'timestamp': round(timestamp, 3),
        'ee_pose_xyzrpy': [round(v, 4) for v in ee_pose],
        'gripper_open': bool(gripper_open),
        'object_pose_xyz': [round(v, 4) for v in obj_xyz],
        'bin_pose_xyz': [round(v, 4) for v in BIN_POSE],
        'phase': phase,
    }


def make_action(t: int, timestamp: float, prev_pose: list[float], curr_pose: list[float], gripper_delta: float, comment: str) -> dict[str, Any]:
    raw = [c - p for p, c in zip(prev_pose[:3], curr_pose[:3])]
    delta_xyz = [round(max(-0.19, min(0.19, v)), 4) for v in raw]
    delta = delta_xyz + [0.0, 0.0, 0.0]
    return {
        't': t,
        'timestamp': round(timestamp, 3),
        'delta_ee_xyzrpy': delta,
        'gripper_delta': round(gripper_delta, 3),
        'comment': comment,
    }


def generate_episode(ep_dir: Path, episode_index: int, fail_mode: str = 'none', seed: int = 0) -> dict[str, Any]:
    rng = random.Random(seed + episode_index)
    arm = MockRobotArm(home_pose_xyzrpy=HOME_POSE)

    obj_xyz = [round(0.38 + rng.uniform(-0.04, 0.04), 4), round(0.03 + rng.uniform(-0.06, 0.06), 4), 0.02]
    pre_grasp_xyz = [obj_xyz[0], obj_xyz[1], 0.18]
    grasp_xyz = [obj_xyz[0], obj_xyz[1], 0.05]
    lift_xyz = [obj_xyz[0], obj_xyz[1], 0.22]
    pre_place_xyz = [BIN_POSE[0], BIN_POSE[1], 0.18]
    place_xyz = [BIN_POSE[0], BIN_POSE[1], 0.08]

    plan = [
        ('reset', HOME_POSE, 0.0, 'Episode start'),
        ('observe', HOME_POSE, 0.0, 'Observe scene'),
        ('pre_grasp', pose_from_xyz(pre_grasp_xyz), 0.0, 'Move above object'),
        ('approach', pose_from_xyz(grasp_xyz), 0.0, 'Move down'),
        ('grasp', pose_from_xyz(grasp_xyz), -1.0, 'Close gripper'),
        ('lift', pose_from_xyz(lift_xyz), 0.0, 'Lift object'),
        ('transfer', pose_from_xyz(pre_place_xyz), 0.0, 'Move above bin'),
        ('place', pose_from_xyz(place_xyz), 0.0, 'Move down to bin'),
        ('release', pose_from_xyz(place_xyz), 1.0, 'Open gripper'),
        ('return_home', HOME_POSE, 0.0, 'Return home'),
    ]

    success = True
    failure_reason = None
    if fail_mode == 'drop' and episode_index % 4 == 0:
        success = False
        failure_reason = 'object_dropped_during_transfer'
    elif fail_mode == 'offset' and episode_index % 5 == 0:
        success = False
        failure_reason = 'grasp_offset_too_large'
    elif fail_mode == 'collision' and episode_index % 6 == 0:
        success = False
        failure_reason = 'collision_risk_detected'

    if failure_reason == 'grasp_offset_too_large':
        pre_grasp_xyz[0] += 0.05
        grasp_xyz[0] += 0.05
        plan[2] = ('pre_grasp', pose_from_xyz(pre_grasp_xyz), 0.0, 'Move above object with offset error')
        plan[3] = ('approach', pose_from_xyz(grasp_xyz), 0.0, 'Move down with offset error')
        plan[4] = ('grasp', pose_from_xyz(grasp_xyz), -1.0, 'Close gripper but miss object')
    if failure_reason == 'collision_risk_detected':
        pre_place_xyz[1] += 0.12
        plan[6] = ('transfer', pose_from_xyz(pre_place_xyz), 0.0, 'Move above bin but path near obstacle')

    ep_dir.mkdir(parents=True, exist_ok=True)
    (ep_dir / 'images' / 'front').mkdir(parents=True, exist_ok=True)
    (ep_dir / 'images' / 'wrist').mkdir(parents=True, exist_ok=True)

    states: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []
    current_obj_xyz = list(obj_xyz)
    prev_pose = HOME_POSE
    grasped = False
    timestamp = 20.0 + episode_index

    for step_idx, (phase, target_pose, gripper_delta, comment) in enumerate(plan):
        if phase != 'reset':
            arm.move_to_pose(target_pose, label=phase)
        if gripper_delta < 0:
            arm.close_gripper()
            if failure_reason != 'grasp_offset_too_large':
                grasped = True
        elif gripper_delta > 0:
            arm.open_gripper()
            if success:
                grasped = False
                current_obj_xyz = [BIN_POSE[0], BIN_POSE[1], BIN_POSE[2]]

        if grasped:
            current_obj_xyz = [target_pose[0], target_pose[1], max(0.02, target_pose[2])]
        elif phase == 'place' and failure_reason == 'object_dropped_during_transfer':
            current_obj_xyz = [BIN_POSE[0] - 0.07, BIN_POSE[1] + 0.05, 0.02]
            grasped = False
        elif phase == 'release' and failure_reason == 'grasp_offset_too_large':
            current_obj_xyz = [obj_xyz[0], obj_xyz[1], 0.02]
            grasped = False
        elif phase == 'transfer' and failure_reason == 'collision_risk_detected':
            current_obj_xyz = [obj_xyz[0], obj_xyz[1], 0.12]
            grasped = True

        if phase == 'release' and failure_reason == 'collision_risk_detected':
            success = False
            grasped = True
            current_obj_xyz = [BIN_POSE[0], BIN_POSE[1] + 0.10, 0.10]

        state = make_state(step_idx, timestamp, target_pose, arm.get_state().gripper_open, current_obj_xyz, phase)
        action = make_action(step_idx, timestamp, prev_pose, target_pose, gripper_delta, comment)
        states.append(state)
        actions.append(action)
        render_frame(ep_dir / 'images' / 'front' / f'frame_{step_idx:04d}.png', target_pose[:3], current_obj_xyz, BIN_POSE, phase, grasped)
        render_frame(ep_dir / 'images' / 'wrist' / f'frame_{step_idx:04d}.png', target_pose[:3], current_obj_xyz, BIN_POSE, phase, grasped)
        prev_pose = target_pose
        timestamp += 0.04

    meta = {
        'episode_id': ep_dir.name,
        'task_name': 'pick_box_to_bin_scripted',
        'instruction': '把桌面上的盒子抓起并放入右侧收纳盒。',
        'success': success,
        'failure_reason': failure_reason,
        'num_steps': len(states),
        'control_mode': 'delta_end_effector_pose_with_gripper',
        'observation_modalities': ['front_rgb', 'wrist_rgb', 'robot_state'],
        'action_definition': '[dx, dy, dz, droll, dpitch, dyaw, gripper_delta]',
        'dataset_version': 'v1.0-scripted',
        'expert_type': 'scripted_state_machine',
        'notes': 'Generated by Chapter 13 scripted expert.',
    }

    (ep_dir / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    with (ep_dir / 'states.jsonl').open('w', encoding='utf-8') as f:
        for row in states:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    with (ep_dir / 'actions.jsonl').open('w', encoding='utf-8') as f:
        for row in actions:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')

    return {'episode_id': ep_dir.name, 'success': success, 'failure_reason': failure_reason, 'num_steps': len(states)}


def write_summary(items: list[dict[str, Any]], output_md: Path) -> None:
    ok_count = sum(1 for x in items if x['success'])
    fail_count = len(items) - ok_count
    lines = [
        '# Chapter 13 Scripted Rollout Summary',
        '',
        f'- total_episodes: `{len(items)}`',
        f'- success_episodes: `{ok_count}`',
        f'- failure_episodes: `{fail_count}`',
        '',
        '## Episode List',
        '',
    ]
    for item in items:
        status = '✅' if item['success'] else '❌'
        lines.append(f"- {status} `{item['episode_id']}` | steps={item['num_steps']} | failure_reason={item['failure_reason']}")
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text('\n'.join(lines), encoding='utf-8')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_dir', type=Path, required=True)
    parser.add_argument('--num_episodes', type=int, default=10)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--fail_mode', type=str, default='mixed', choices=['none', 'drop', 'offset', 'collision', 'mixed'])
    parser.add_argument('--summary_md', type=Path, default=None)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    items = []
    fail_modes = ['none', 'drop', 'offset', 'collision']
    for i in range(1, args.num_episodes + 1):
        fail_mode = fail_modes[i % len(fail_modes)] if args.fail_mode == 'mixed' else args.fail_mode
        ep_dir = args.output_dir / f'episode_{1000 + i:04d}'
        items.append(generate_episode(ep_dir, episode_index=i, fail_mode=fail_mode, seed=args.seed))

    if args.summary_md is not None:
        write_summary(items, args.summary_md)
    print(json.dumps({'total': len(items), 'success': sum(1 for x in items if x['success'])}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
