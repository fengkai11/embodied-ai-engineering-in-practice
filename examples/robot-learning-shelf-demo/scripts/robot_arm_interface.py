#!/usr/bin/env python3
"""Minimal robot arm interface for Chapter 12."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from pathlib import Path
import argparse
import json
from typing import Any


@dataclass
class RobotArmState:
    ee_pose_xyzrpy: list[float]
    gripper_open: bool
    command_count: int


class RobotArmInterface(ABC):
    @abstractmethod
    def move_to_pose(self, target_pose_xyzrpy: list[float], label: str = '') -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def open_gripper(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def close_gripper(self) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def get_state(self) -> RobotArmState:
        raise NotImplementedError


class MockRobotArm(RobotArmInterface):
    def __init__(self, home_pose_xyzrpy: list[float]) -> None:
        self._state = RobotArmState(ee_pose_xyzrpy=list(home_pose_xyzrpy), gripper_open=True, command_count=0)
        self.history: list[dict[str, Any]] = []

    def move_to_pose(self, target_pose_xyzrpy: list[float], label: str = '') -> dict[str, Any]:
        self._state.ee_pose_xyzrpy = list(target_pose_xyzrpy)
        self._state.command_count += 1
        event = {
            'type': 'move',
            'label': label,
            'target_pose_xyzrpy': list(target_pose_xyzrpy),
            'command_index': self._state.command_count,
        }
        self.history.append(event)
        return event

    def open_gripper(self) -> dict[str, Any]:
        self._state.gripper_open = True
        self._state.command_count += 1
        event = {'type': 'open_gripper', 'command_index': self._state.command_count}
        self.history.append(event)
        return event

    def close_gripper(self) -> dict[str, Any]:
        self._state.gripper_open = False
        self._state.command_count += 1
        event = {'type': 'close_gripper', 'command_index': self._state.command_count}
        self.history.append(event)
        return event

    def get_state(self) -> RobotArmState:
        return RobotArmState(
            ee_pose_xyzrpy=list(self._state.ee_pose_xyzrpy),
            gripper_open=self._state.gripper_open,
            command_count=self._state.command_count,
        )


def run_demo(output_path: Path | None = None) -> dict[str, Any]:
    arm = MockRobotArm(home_pose_xyzrpy=[0.30, -0.10, 0.25, 3.14, 0.0, 0.0])
    arm.move_to_pose([0.42, 0.05, 0.18, 3.14, 0.0, 0.0], label='pre_grasp')
    arm.move_to_pose([0.42, 0.05, 0.05, 3.14, 0.0, 0.0], label='grasp')
    arm.close_gripper()
    arm.move_to_pose([0.42, 0.05, 0.22, 3.14, 0.0, 0.0], label='lift')
    arm.move_to_pose([0.62, -0.08, 0.18, 3.14, 0.0, 0.0], label='pre_place')
    arm.move_to_pose([0.62, -0.08, 0.08, 3.14, 0.0, 0.0], label='place')
    arm.open_gripper()
    arm.move_to_pose([0.30, -0.10, 0.25, 3.14, 0.0, 0.0], label='return_home')

    report = {
        'demo_name': 'chapter_12_mock_robot_arm_demo',
        'final_state': asdict(arm.get_state()),
        'history': arm.history,
    }
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=None)
    args = parser.parse_args()
    report = run_demo(args.output)
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
