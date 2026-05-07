#!/usr/bin/env python3
"""Geometry utilities for Chapter 11.

This module provides small, dependency-light helpers for the shelf demo:
1. Project pixel + depth to a 3D point in camera coordinates.
2. Convert roll-pitch-yaw and translation to a 4x4 transform.
3. Transform 3D points across frames.

It is intentionally compact and educational.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import argparse
import json
import math
from typing import Any


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except Exception as exc:
        raise RuntimeError('PyYAML is required to read YAML config files.') from exc
    with path.open('r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError('YAML root must be a dict.')
    return data


@dataclass
class CameraIntrinsics:
    fx: float
    fy: float
    cx: float
    cy: float


def rpy_to_rotation_matrix(roll: float, pitch: float, yaw: float) -> list[list[float]]:
    cr, sr = math.cos(roll), math.sin(roll)
    cp, sp = math.cos(pitch), math.sin(pitch)
    cy, sy = math.cos(yaw), math.sin(yaw)
    rx = [[1, 0, 0], [0, cr, -sr], [0, sr, cr]]
    ry = [[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]]
    rz = [[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]]

    def mm(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
        out = [[0.0] * len(b[0]) for _ in range(len(a))]
        for i in range(len(a)):
            for j in range(len(b[0])):
                out[i][j] = sum(a[i][k] * b[k][j] for k in range(len(b)))
        return out

    return mm(rz, mm(ry, rx))


def pose_to_matrix(translation_xyz: list[float], rpy_rad: list[float]) -> list[list[float]]:
    r = rpy_to_rotation_matrix(rpy_rad[0], rpy_rad[1], rpy_rad[2])
    tx, ty, tz = translation_xyz
    return [
        [r[0][0], r[0][1], r[0][2], tx],
        [r[1][0], r[1][1], r[1][2], ty],
        [r[2][0], r[2][1], r[2][2], tz],
        [0.0, 0.0, 0.0, 1.0],
    ]


def transform_point(transform: list[list[float]], point_xyz: list[float]) -> list[float]:
    x, y, z = point_xyz
    v = [x, y, z, 1.0]
    out = [sum(transform[i][j] * v[j] for j in range(4)) for i in range(4)]
    return out[:3]


def pixel_to_camera_point(u: float, v: float, depth: float, intr: CameraIntrinsics) -> list[float]:
    x = (u - intr.cx) * depth / intr.fx
    y = (v - intr.cy) * depth / intr.fy
    z = depth
    return [float(x), float(y), float(z)]


def matrix_to_pretty_rows(m: list[list[float]]) -> list[str]:
    return ['[' + ', '.join(f'{v: .4f}' for v in row) + ']' for row in m]


def run_demo(camera_config_path: Path, u: float, v: float, depth: float) -> dict[str, Any]:
    cfg = load_yaml(camera_config_path)
    intr = CameraIntrinsics(fx=cfg['fx'], fy=cfg['fy'], cx=cfg['cx'], cy=cfg['cy'])
    p_c = pixel_to_camera_point(u, v, depth, intr)
    extr = cfg['extrinsics']
    t_base_camera = pose_to_matrix(extr['translation_xyz_m'], extr['rpy_rad'])
    p_b = transform_point(t_base_camera, p_c)

    result = {
        'input': {
            'pixel_uv': [u, v],
            'depth_m': depth,
            'camera_name': cfg.get('camera_name'),
            'mount_type': cfg.get('mount_type'),
        },
        'camera_intrinsics': asdict(intr),
        'point_in_camera_frame_xyz': p_c,
        'T_base_camera': t_base_camera,
        'point_in_base_frame_xyz': p_b,
        'interpretation': 'The point can now be used to construct a pre-grasp or grasp pose in base_link.',
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--camera_config', type=Path, required=True)
    parser.add_argument('--u', type=float, default=356.0)
    parser.add_argument('--v', type=float, default=242.0)
    parser.add_argument('--depth', type=float, default=0.58)
    parser.add_argument('--output', type=Path, default=None)
    args = parser.parse_args()

    result = run_demo(args.camera_config, args.u, args.v, args.depth)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'Saved demo result to: {args.output}')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
