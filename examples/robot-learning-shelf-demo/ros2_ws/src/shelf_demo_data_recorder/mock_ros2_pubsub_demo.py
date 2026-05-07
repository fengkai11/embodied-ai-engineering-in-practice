#!/usr/bin/env python3
"""A pure-Python mock ROS2 pub/sub demo for the book project."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Callable


class EventBus:
    def __init__(self) -> None:
        self.subscribers: dict[str, list[Callable[[dict[str, Any]], None]]] = {}
        self.log: list[dict[str, Any]] = []

    def publish(self, topic: str, msg: dict[str, Any]) -> None:
        self.log.append({'topic': topic, 'msg': msg})
        for cb in self.subscribers.get(topic, []):
            cb(msg)

    def subscribe(self, topic: str, callback: Callable[[dict[str, Any]], None]) -> None:
        self.subscribers.setdefault(topic, []).append(callback)


@dataclass
class RecorderSummary:
    camera_messages: int = 0
    joint_messages: int = 0
    action_messages: int = 0
    task_messages: int = 0


class DataRecorderNode:
    def __init__(self, bus: EventBus) -> None:
        self.summary = RecorderSummary()
        bus.subscribe('/camera/front/image_raw', self.on_camera)
        bus.subscribe('/joint_states', self.on_joint)
        bus.subscribe('/action_cmd', self.on_action)
        bus.subscribe('/task_info', self.on_task)

    def on_camera(self, msg: dict[str, Any]) -> None:
        self.summary.camera_messages += 1

    def on_joint(self, msg: dict[str, Any]) -> None:
        self.summary.joint_messages += 1

    def on_action(self, msg: dict[str, Any]) -> None:
        self.summary.action_messages += 1

    def on_task(self, msg: dict[str, Any]) -> None:
        self.summary.task_messages += 1


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_json', type=Path, required=True)
    args = parser.parse_args()

    bus = EventBus()
    recorder = DataRecorderNode(bus)

    bus.publish('/task_info', {'instruction': '把红色盒子放进右边收纳盒。', 'task_name': 'pick_box_to_bin'})
    for i in range(5):
        bus.publish('/camera/front/image_raw', {'frame_id': i, 'timestamp': 1.0 + 0.04 * i})
        bus.publish('/joint_states', {'frame_id': i, 'joint_positions': [0.1*i, 0.2*i, 0.3*i]})
        bus.publish('/action_cmd', {'frame_id': i, 'delta_ee_xyzrpy': [0.01, 0.0, 0.0, 0.0, 0.0, 0.0], 'gripper_delta': 0.0})

    report = {
        'topics_observed': ['/camera/front/image_raw', '/joint_states', '/action_cmd', '/task_info'],
        'summary': asdict(recorder.summary),
        'total_published_messages': len(bus.log),
        'note': 'This is a pure-Python mock demo used to explain ROS2 topic flow without requiring a ROS2 runtime.',
    }
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
