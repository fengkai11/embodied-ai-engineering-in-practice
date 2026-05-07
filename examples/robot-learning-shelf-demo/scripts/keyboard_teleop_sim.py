#!/usr/bin/env python3
"""Keyboard teleoperation simulator for Chapter 14.

This script simulates low-cost keyboard teleoperation and records the result
as episode data compatible with the book's running project.
"""
from __future__ import annotations

import argparse
import json
import random
import shutil
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from robot_arm_interface import MockRobotArm  # noqa: E402

try:
    from PIL import Image, ImageDraw
except Exception:  # pragma: no cover
    Image = None
    ImageDraw = None

HOME_POSE = [0.30, -0.10, 0.25, 3.14, 0.0, 0.0]
BIN_XYZ = [0.62, -0.08, 0.02]
KEY_MAP = {
    'w': [0.00, 0.02, 0.00],
    's': [0.00, -0.02, 0.00],
    'a': [-0.02, 0.00, 0.00],
    'd': [0.02, 0.00, 0.00],
    'q': [0.00, 0.00, 0.02],
    'e': [0.00, 0.00, -0.02],
    'o': [0.00, 0.00, 0.00],  # open gripper
    'c': [0.00, 0.00, 0.00],  # close gripper
    'h': [0.00, 0.00, 0.00],  # home
}


def world_to_px(x: float, y: float) -> tuple[int, int]:
    px = int(70 + (x - 0.20) / 0.50 * 180)
    py = int(170 - (y + 0.35) / 0.60 * 90)
    return px, py


def render_frame(output_path: Path, ee_xyz: list[float], obj_xyz: list[float], phase: str, pressed_key: str, grasped: bool) -> None:
    if Image is None or ImageDraw is None:
        return
    img = Image.new('RGB', (320, 240), color=(246, 248, 251))
    draw = ImageDraw.Draw(img)
    draw.rectangle([30, 170, 290, 210], outline=(100, 100, 100), fill=(235, 235, 235))
    draw.rectangle([215, 130, 290, 190], outline=(50, 90, 180), fill=(70, 120, 200))

    objx, objy = world_to_px(obj_xyz[0], obj_xyz[1])
    eex, _ = world_to_px(ee_xyz[0], ee_xyz[1])
    ee_top = max(25, int(140 - ee_xyz[2] * 250))
    if grasped:
        objy = ee_top + 24
        objx = eex
    draw.rectangle([objx - 10, objy - 10, objx + 10, objy + 10], outline=(130, 70, 20), fill=(190, 140, 90))

    draw.line([eex, 30, eex, ee_top], fill=(60, 60, 60), width=4)
    draw.line([eex, ee_top, eex - 9, ee_top + 14], fill=(35, 35, 35), width=3)
    draw.line([eex, ee_top, eex + 9, ee_top + 14], fill=(35, 35, 35), width=3)
    draw.text((12, 8), f'phase: {phase}', fill=(15, 15, 15))
    draw.text((12, 25), f'key: {pressed_key}', fill=(15, 15, 15))
    draw.text((12, 42), f'ee: {[round(v, 3) for v in ee_xyz]}', fill=(15, 15, 15))
    draw.text((12, 59), f'obj: {[round(v, 3) for v in obj_xyz]}', fill=(15, 15, 15))
    draw.text((12, 76), 'keys: WASD xy / QE z / C close / O open / H home', fill=(50, 70, 120))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)


def choose_key(curr: list[float], target: list[float]) -> str:
    dx, dy, dz = target[0] - curr[0], target[1] - curr[1], target[2] - curr[2]
    comps = [('d' if dx > 0 else 'a', abs(dx)), ('w' if dy > 0 else 's', abs(dy)), ('q' if dz > 0 else 'e', abs(dz))]
    key, mag = max(comps, key=lambda x: x[1])
    return key if mag > 0.005 else ' '


def stepped_move(arm: MockRobotArm, curr_pose: list[float], target_xyz: list[float], phase: str) -> list[dict[str, Any]]:
    rows = []
    step_idx = 0
    while step_idx < 30:
        key = choose_key(curr_pose[:3], target_xyz)
        if key == ' ':
            break
        delta = KEY_MAP[key]
        new_pose = list(curr_pose)
        for i in range(3):
            new_pose[i] = round(new_pose[i] + delta[i], 4)
        # clamp to workspace
        new_pose[0] = min(max(new_pose[0], 0.20), 0.68)
        new_pose[1] = min(max(new_pose[1], -0.25), 0.18)
        new_pose[2] = min(max(new_pose[2], 0.02), 0.30)
        arm.move_to_pose(new_pose, label=f'{phase}_{step_idx:02d}')
        rows.append({'key': key, 'pose': new_pose, 'phase': phase})
        curr_pose[:] = new_pose
        step_idx += 1
    return rows


def make_state(t: int, timestamp: float, arm: MockRobotArm, object_xyz: list[float], phase: str, pressed_key: str, intervention_count: int) -> dict[str, Any]:
    s = arm.get_state()
    return {
        't': t,
        'timestamp': round(timestamp, 3),
        'ee_pose_xyzrpy': [round(v, 4) for v in s.ee_pose_xyzrpy],
        'gripper_open': bool(s.gripper_open),
        'object_pose_xyz': [round(v, 4) for v in object_xyz],
        'bin_pose_xyz': [round(v, 4) for v in BIN_XYZ],
        'phase': phase,
        'pressed_key': pressed_key,
        'intervention_count': intervention_count,
    }


def make_action(t: int, timestamp: float, prev_pose: list[float], curr_pose: list[float], key: str, gripper_delta: float, comment: str) -> dict[str, Any]:
    delta_xyz = [round(curr_pose[i] - prev_pose[i], 4) for i in range(3)]
    return {
        't': t,
        'timestamp': round(timestamp, 3),
        'delta_ee_xyzrpy': delta_xyz + [0.0, 0.0, 0.0],
        'gripper_delta': round(gripper_delta, 3),
        'pressed_key': key,
        'comment': comment,
    }


def create_episode(ep_dir: Path, episode_idx: int, operator_id: str, success: bool, failure_reason: str | None, seed: int) -> dict[str, Any]:
    rng = random.Random(seed + episode_idx)
    arm = MockRobotArm(home_pose_xyzrpy=HOME_POSE)
    ep_dir.mkdir(parents=True, exist_ok=True)
    (ep_dir / 'images' / 'front').mkdir(parents=True, exist_ok=True)
    (ep_dir / 'images' / 'wrist').mkdir(parents=True, exist_ok=True)

    object_xyz = [round(0.38 + rng.uniform(-0.05, 0.05), 4), round(0.03 + rng.uniform(-0.07, 0.07), 4), 0.02]
    if failure_reason == 'bad_alignment':
        target_offset = [0.05, -0.02, 0.0]
    else:
        target_offset = [0.0, 0.0, 0.0]
    pre_grasp = [object_xyz[0] + target_offset[0], object_xyz[1] + target_offset[1], 0.18]
    grasp = [object_xyz[0] + target_offset[0], object_xyz[1] + target_offset[1], 0.05]
    lift = [object_xyz[0], object_xyz[1], 0.22]
    pre_place = [BIN_XYZ[0], BIN_XYZ[1], 0.18]
    place = [BIN_XYZ[0], BIN_XYZ[1], 0.08]

    timestamp = 30.0 + episode_idx
    states: list[dict[str, Any]] = []
    actions: list[dict[str, Any]] = []
    prev_pose = HOME_POSE
    curr_pose = list(HOME_POSE)
    step_counter = 0
    grasped = False
    intervention_count = 0 if success else 1 + (episode_idx % 2)

    def record_step(phase: str, key: str, gripper_delta: float, comment: str) -> None:
        nonlocal timestamp, prev_pose, step_counter, object_xyz, grasped
        current = list(arm.get_state().ee_pose_xyzrpy)
        if grasped:
            object_xyz = [current[0], current[1], max(0.02, current[2])]
        states.append(make_state(step_counter, timestamp, arm, object_xyz, phase, key, intervention_count))
        actions.append(make_action(step_counter, timestamp, prev_pose, current, key, gripper_delta, comment))
        render_frame(ep_dir / 'images' / 'front' / f'frame_{step_counter:04d}.png', current[:3], object_xyz, phase, key, grasped)
        render_frame(ep_dir / 'images' / 'wrist' / f'frame_{step_counter:04d}.png', current[:3], object_xyz, phase, key, grasped)
        prev_pose = current
        timestamp += 0.05
        step_counter += 1

    # initial observation
    record_step('observe', ' ', 0.0, 'Start teleop observation')

    for phase, target_xyz in [('move_above_object', pre_grasp), ('descend_to_grasp', grasp)]:
        for row in stepped_move(arm, curr_pose, target_xyz, phase):
            record_step(phase, row['key'], 0.0, f'Teleop key {row["key"]}')

    arm.close_gripper()
    if failure_reason != 'bad_alignment':
        grasped = True
    record_step('close_gripper', 'c', -1.0, 'Close gripper')

    for phase, target_xyz in [('lift', lift), ('move_to_bin', pre_place), ('descend_to_bin', place)]:
        for row in stepped_move(arm, curr_pose, target_xyz, phase):
            if failure_reason == 'drop_during_transfer' and phase == 'move_to_bin' and step_counter > 10:
                grasped = False
                object_xyz = [round(curr_pose[0] - 0.03, 4), round(curr_pose[1] + 0.02, 4), 0.02]
            record_step(phase, row['key'], 0.0, f'Teleop key {row["key"]}')

    if success:
        arm.open_gripper()
        grasped = False
        object_xyz = list(BIN_XYZ)
        record_step('release', 'o', 1.0, 'Release object into bin')
    else:
        if failure_reason == 'timeout':
            # do not finish place properly
            record_step('timeout', ' ', 0.0, 'Operator hesitated and task timed out')
        else:
            arm.open_gripper()
            grasped = False
            record_step('release_failed', 'o', 1.0, 'Release but task failed')

    # return home via H then stepped move
    arm.move_to_pose(HOME_POSE, label='home')
    curr_pose[:] = HOME_POSE
    record_step('return_home', 'h', 0.0, 'Return home')

    meta = {
        'episode_id': ep_dir.name,
        'task_name': 'pick_box_to_bin_teleop_keyboard',
        'instruction': '使用键盘遥操作机械臂把桌面方块抓起并放入右侧收纳盒。',
        'source': 'teleop_keyboard_sim',
        'teleop_device': 'keyboard',
        'operator_id': operator_id,
        'success': success,
        'failure_reason': failure_reason,
        'intervention_count': intervention_count,
        'num_steps': len(states),
        'control_mode': 'delta_end_effector_pose_with_gripper',
        'observation_modalities': ['front_rgb', 'wrist_rgb', 'robot_state'],
        'notes': 'Simulated keyboard teleoperation episode for Chapter 14.',
    }
    (ep_dir / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    with (ep_dir / 'states.jsonl').open('w', encoding='utf-8') as f:
        for row in states:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    with (ep_dir / 'actions.jsonl').open('w', encoding='utf-8') as f:
        for row in actions:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    return {
        'episode_id': ep_dir.name,
        'success': success,
        'failure_reason': failure_reason,
        'operator_id': operator_id,
        'num_steps': len(states),
    }


def write_summary(items: list[dict[str, Any]], summary_md: Path, summary_json: Path | None) -> None:
    success_count = sum(1 for x in items if x['success'])
    fail_count = len(items) - success_count
    lines = [
        '# Chapter 14 Keyboard Teleop Summary',
        '',
        f'- total_episodes: `{len(items)}`',
        f'- success_episodes: `{success_count}`',
        f'- failure_episodes: `{fail_count}`',
        '',
        '## Episode Details',
        '',
    ]
    for item in items:
        badge = '✅' if item['success'] else '❌'
        lines.append(f"- {badge} `{item['episode_id']}` | operator=`{item['operator_id']}` | steps={item['num_steps']} | failure_reason={item['failure_reason']}")
    summary_md.parent.mkdir(parents=True, exist_ok=True)
    summary_md.write_text('\n'.join(lines), encoding='utf-8')
    if summary_json is not None:
        summary_json.write_text(json.dumps({'items': items, 'success_count': success_count, 'failure_count': fail_count}, ensure_ascii=False, indent=2), encoding='utf-8')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_dir', type=Path, required=True)
    parser.add_argument('--num_success', type=int, default=5)
    parser.add_argument('--num_failure', type=int, default=3)
    parser.add_argument('--operator_id_prefix', type=str, default='opA')
    parser.add_argument('--seed', type=int, default=123)
    parser.add_argument('--summary_md', type=Path, default=None)
    parser.add_argument('--summary_json', type=Path, default=None)
    parser.add_argument('--reset', action='store_true')
    args = parser.parse_args()

    if args.reset and args.output_dir.exists():
        shutil.rmtree(args.output_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    failure_modes = ['bad_alignment', 'drop_during_transfer', 'timeout']
    items = []
    idx = 1
    for i in range(args.num_success):
        op_id = f'{args.operator_id_prefix}_{(i % 2) + 1:02d}'
        ep = args.output_dir / f'episode_{2000 + idx:04d}'
        items.append(create_episode(ep, idx, op_id, True, None, args.seed))
        idx += 1
    for i in range(args.num_failure):
        op_id = f'{args.operator_id_prefix}_{((i + 1) % 2) + 1:02d}'
        ep = args.output_dir / f'episode_{2000 + idx:04d}'
        items.append(create_episode(ep, idx, op_id, False, failure_modes[i % len(failure_modes)], args.seed))
        idx += 1

    if args.summary_md is not None:
        write_summary(items, args.summary_md, args.summary_json)
    print(json.dumps({'total_episodes': len(items), 'success': sum(1 for x in items if x['success'])}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
