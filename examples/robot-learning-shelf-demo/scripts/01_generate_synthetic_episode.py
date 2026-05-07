#!/usr/bin/env python3
"""Generate synthetic episodes with RGB frame sequences.

This script updates the earlier minimal generator by adding:
- front / wrist RGB image folders
- richer meta.json
- success / failure reason fields
- consistent timestamps across states, actions, and images
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import math
import random
from typing import Any

FRAME_W = 320
FRAME_H = 240
TABLE_MARGIN = 20
TABLE_TOP = 120


@dataclass
class EpisodeMeta:
    episode_id: str
    task_name: str
    instruction: str
    success: bool
    failure_reason: str | None
    num_steps: int
    control_mode: str
    observation_modalities: list[str]
    action_definition: str
    dataset_version: str
    notes: str


@dataclass
class StateRecord:
    t: int
    timestamp: float
    ee_pose_xyzrpy: list[float]
    gripper_open: bool
    object_pose_xyz: list[float]
    bin_pose_xyz: list[float]
    phase: str


@dataclass
class ActionRecord:
    t: int
    timestamp: float
    delta_ee_xyzrpy: list[float]
    gripper_delta: float
    comment: str


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


def world_to_front_px(x: float, y: float) -> tuple[int, int]:
    px = int(60 + x * 250)
    py = int(170 - y * 180)
    return px, py


def world_to_wrist_px(x: float, y: float) -> tuple[int, int]:
    px = int(110 + x * 180)
    py = int(150 - y * 130)
    return px, py


def maybe_import_pil():
    try:
        from PIL import Image, ImageDraw  # type: ignore
        return Image, ImageDraw
    except Exception as exc:
        raise RuntimeError('Pillow is required to render synthetic RGB frames.') from exc


def draw_front_frame(save_path: Path, state: StateRecord) -> None:
    Image, ImageDraw = maybe_import_pil()
    img = Image.new('RGB', (FRAME_W, FRAME_H), (245, 248, 252))
    draw = ImageDraw.Draw(img)
    draw.rectangle([20, 110, 300, 220], fill=(223, 183, 122), outline=(130, 92, 55), width=3)
    draw.rectangle([220, 85, 290, 140], fill=(180, 185, 190), outline=(90, 95, 100), width=3)

    bx, by = world_to_front_px(state.object_pose_xyz[0], state.object_pose_xyz[1])
    draw.rectangle([bx-12, by-12, bx+12, by+12], fill=(210, 45, 45), outline=(120, 20, 20), width=2)

    ex, ey = world_to_front_px(state.ee_pose_xyzrpy[0], state.ee_pose_xyzrpy[1])
    draw.line([250, 55, 220, 75, ex, ey], fill=(165, 170, 176), width=8)
    draw.ellipse([245, 50, 255, 60], fill=(40, 40, 40))
    draw.ellipse([214, 69, 226, 81], fill=(40, 40, 40))
    grip_color = (30, 30, 30)
    gap = 7 if state.gripper_open else 2
    draw.line([ex-4, ey, ex-4-gap, ey+14], fill=grip_color, width=4)
    draw.line([ex+4, ey, ex+4+gap, ey+14], fill=grip_color, width=4)

    draw.text((10, 10), f'front | t={state.t} | phase={state.phase}', fill=(20, 50, 110))
    save_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(save_path)


def draw_wrist_frame(save_path: Path, state: StateRecord) -> None:
    Image, ImageDraw = maybe_import_pil()
    img = Image.new('RGB', (FRAME_W, FRAME_H), (250, 250, 250))
    draw = ImageDraw.Draw(img)
    draw.rectangle([35, 120, 285, 220], fill=(223, 183, 122), outline=(130, 92, 55), width=3)

    bx, by = world_to_wrist_px(state.object_pose_xyz[0], state.object_pose_xyz[1])
    draw.rectangle([bx-16, by-16, bx+16, by+16], fill=(210, 45, 45), outline=(120, 20, 20), width=2)

    # wrist arm and gripper occupy foreground
    draw.rectangle([130, 30, 190, 110], fill=(205, 210, 216), outline=(120, 120, 120), width=3)
    draw.ellipse([145, 90, 175, 120], fill=(40, 40, 40))
    gap = 14 if state.gripper_open else 5
    draw.line([153, 115, 153-gap, 140], fill=(25, 25, 25), width=5)
    draw.line([167, 115, 167+gap, 140], fill=(25, 25, 25), width=5)

    draw.text((10, 10), f'wrist | t={state.t} | phase={state.phase}', fill=(20, 50, 110))
    save_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(save_path)


def build_success_episode() -> tuple[EpisodeMeta, list[StateRecord], list[ActionRecord]]:
    meta = EpisodeMeta(
        episode_id='episode_0001',
        task_name='pick_box_to_bin',
        instruction='把红色盒子放进右边收纳盒。',
        success=True,
        failure_reason=None,
        num_steps=7,
        control_mode='delta_end_effector_pose_with_gripper',
        observation_modalities=['front_rgb', 'wrist_rgb', 'robot_state'],
        action_definition='[dx, dy, dz, droll, dpitch, dyaw, gripper_delta]',
        dataset_version='v0.2',
        notes='Synthetic success episode for Chapter 7.',
    )

    states = [
        StateRecord(0, 12.00, [0.30, -0.10, 0.25, 3.14, 0.0, 0.0], True,  [0.42, 0.05, 0.02], [0.62, -0.08, 0.04], 'reset'),
        StateRecord(1, 12.04, [0.30, -0.10, 0.25, 3.14, 0.0, 0.0], True,  [0.42, 0.05, 0.02], [0.62, -0.08, 0.04], 'observe'),
        StateRecord(2, 12.08, [0.42,  0.05, 0.18, 3.14, 0.0, 0.0], True,  [0.42, 0.05, 0.02], [0.62, -0.08, 0.04], 'pre_grasp'),
        StateRecord(3, 12.12, [0.42,  0.05, 0.05, 3.14, 0.0, 0.0], True,  [0.42, 0.05, 0.02], [0.62, -0.08, 0.04], 'approach'),
        StateRecord(4, 12.16, [0.42,  0.05, 0.05, 3.14, 0.0, 0.0], False, [0.42, 0.05, 0.05], [0.62, -0.08, 0.04], 'grasp'),
        StateRecord(5, 12.20, [0.62, -0.08, 0.18, 3.14, 0.0, 0.0], False, [0.62, -0.08, 0.18], [0.62, -0.08, 0.04], 'transfer'),
        StateRecord(6, 12.24, [0.62, -0.08, 0.10, 3.14, 0.0, 0.0], True,  [0.62, -0.08, 0.04], [0.62, -0.08, 0.04], 'release'),
    ]
    actions = [
        ActionRecord(0, 12.00, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  0.0, 'Episode start'),
        ActionRecord(1, 12.04, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  0.0, 'Observe'),
        ActionRecord(2, 12.08, [0.12, 0.15, -0.07, 0.0, 0.0, 0.0], 0.0, 'Move above the object'),
        ActionRecord(3, 12.12, [0.0, 0.0, -0.13, 0.0, 0.0, 0.0], 0.0, 'Move down'),
        ActionRecord(4, 12.16, [0.0, 0.0,  0.0, 0.0, 0.0, 0.0], -1.0, 'Close gripper'),
        ActionRecord(5, 12.20, [0.20, -0.13, 0.13, 0.0, 0.0, 0.0], 0.0, 'Transfer to bin'),
        ActionRecord(6, 12.24, [0.0, 0.0, -0.08, 0.0, 0.0, 0.0], +1.0, 'Open gripper and release'),
    ]
    return meta, states, actions


def build_failure_episode() -> tuple[EpisodeMeta, list[StateRecord], list[ActionRecord]]:
    meta = EpisodeMeta(
        episode_id='episode_0002',
        task_name='pick_box_to_bin',
        instruction='把红色盒子放进右边收纳盒。',
        success=False,
        failure_reason='drop_during_transfer',
        num_steps=7,
        control_mode='delta_end_effector_pose_with_gripper',
        observation_modalities=['front_rgb', 'wrist_rgb', 'robot_state'],
        action_definition='[dx, dy, dz, droll, dpitch, dyaw, gripper_delta]',
        dataset_version='v0.2',
        notes='Synthetic failure episode for Chapter 7.',
    )

    states = [
        StateRecord(0, 18.00, [0.30, -0.10, 0.25, 3.14, 0.0, 0.0], True,  [0.45, 0.02, 0.02], [0.62, -0.06, 0.04], 'reset'),
        StateRecord(1, 18.04, [0.30, -0.10, 0.25, 3.14, 0.0, 0.0], True,  [0.45, 0.02, 0.02], [0.62, -0.06, 0.04], 'observe'),
        StateRecord(2, 18.08, [0.45,  0.02, 0.18, 3.14, 0.0, 0.0], True,  [0.45, 0.02, 0.02], [0.62, -0.06, 0.04], 'pre_grasp'),
        StateRecord(3, 18.12, [0.45,  0.02, 0.05, 3.14, 0.0, 0.0], False, [0.45, 0.02, 0.05], [0.62, -0.06, 0.04], 'grasp'),
        StateRecord(4, 18.16, [0.53, -0.02, 0.12, 3.14, 0.0, 0.0], False, [0.53, -0.02, 0.12], [0.62, -0.06, 0.04], 'transfer'),
        StateRecord(5, 18.20, [0.60, -0.05, 0.13, 3.14, 0.0, 0.0], True,  [0.56, -0.03, 0.03], [0.62, -0.06, 0.04], 'drop'),
        StateRecord(6, 18.24, [0.60, -0.05, 0.13, 3.14, 0.0, 0.0], True,  [0.56, -0.03, 0.03], [0.62, -0.06, 0.04], 'abort'),
    ]
    actions = [
        ActionRecord(0, 18.00, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  0.0, 'Episode start'),
        ActionRecord(1, 18.04, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],  0.0, 'Observe'),
        ActionRecord(2, 18.08, [0.15, 0.12, -0.07, 0.0, 0.0, 0.0], 0.0, 'Move above the object'),
        ActionRecord(3, 18.12, [0.0, 0.0, -0.13, 0.0, 0.0, 0.0], -1.0, 'Close gripper'),
        ActionRecord(4, 18.16, [0.08, -0.04, 0.07, 0.0, 0.0, 0.0], 0.0, 'Lift and start transfer'),
        ActionRecord(5, 18.20, [0.07, -0.03, 0.01, 0.0, 0.0, 0.0], +1.0, 'Unintended gripper release'),
        ActionRecord(6, 18.24, [0.0, 0.0,  0.0, 0.0, 0.0, 0.0], 0.0, 'Abort'),
    ]
    return meta, states, actions


def save_episode(project_root: Path, meta: EpisodeMeta, states: list[StateRecord], actions: list[ActionRecord]) -> None:
    episode_dir = project_root / 'datasets' / 'dataset_v0_sample' / meta.episode_id
    (episode_dir / 'images' / 'front').mkdir(parents=True, exist_ok=True)
    (episode_dir / 'images' / 'wrist').mkdir(parents=True, exist_ok=True)
    write_json(episode_dir / 'meta.json', asdict(meta))
    write_jsonl(episode_dir / 'states.jsonl', [asdict(x) for x in states])
    write_jsonl(episode_dir / 'actions.jsonl', [asdict(x) for x in actions])

    for state in states:
        draw_front_frame(episode_dir / 'images' / 'front' / f'frame_{state.t:04d}.png', state)
        draw_wrist_frame(episode_dir / 'images' / 'wrist' / f'frame_{state.t:04d}.png', state)


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    for builder in [build_success_episode, build_failure_episode]:
        meta, states, actions = builder()
        save_episode(project_root, meta, states, actions)
        print(f'Generated {meta.episode_id} at {project_root / "datasets" / "dataset_v0_sample" / meta.episode_id}')


if __name__ == '__main__':
    main()
