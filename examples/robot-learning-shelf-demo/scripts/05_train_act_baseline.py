#!/usr/bin/env python3
"""Train a toy Behavior Cloning baseline and a toy chunk predictor.

This script uses a 2D point-mass task to explain the intuition behind
Behavior Cloning (BC) and action chunk prediction (ACT-style intuition).

Task:
    Move a point from a random start position to a target position.

Observation:
    [x, y, gx, gy]

Action:
    [dx, dy]

Chunk Action:
    [dx_t, dy_t, dx_t+1, dy_t+1, ..., dx_t+k-1, dy_t+k-1]

The "expert" is a simple hand-crafted proportional controller.
The models are trained with linear least squares to keep dependencies minimal.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import argparse
import json
import math
import numpy as np
from typing import Iterable


@dataclass
class RolloutResult:
    final_error: float
    success: bool
    num_steps: int
    trajectory: list[list[float]]


def set_seed(seed: int) -> None:
    np.random.seed(seed)


def clip_norm(vec: np.ndarray, max_step: float) -> np.ndarray:
    norm = np.linalg.norm(vec)
    if norm < 1e-12:
        return vec.copy()
    if norm <= max_step:
        return vec.copy()
    return vec / norm * max_step


def expert_action(state_xy: np.ndarray, goal_xy: np.ndarray, max_step: float = 0.12) -> np.ndarray:
    delta = goal_xy - state_xy
    return clip_norm(delta, max_step=max_step)


def generate_trajectory(start: np.ndarray, goal: np.ndarray, horizon: int = 20) -> list[tuple[np.ndarray, np.ndarray]]:
    state = start.copy()
    traj: list[tuple[np.ndarray, np.ndarray]] = []
    for _ in range(horizon):
        action = expert_action(state, goal)
        traj.append((state.copy(), action.copy()))
        state = state + action
        if np.linalg.norm(goal - state) < 0.03:
            break
    return traj


def generate_dataset(num_episodes: int, horizon: int = 20) -> list[dict[str, np.ndarray]]:
    dataset: list[dict[str, np.ndarray]] = []
    for _ in range(num_episodes):
        start = np.random.uniform(low=-1.0, high=1.0, size=(2,))
        goal = np.random.uniform(low=-1.0, high=1.0, size=(2,))
        traj = generate_trajectory(start, goal, horizon=horizon)
        states = np.array([s for s, _ in traj], dtype=np.float64)
        actions = np.array([a for _, a in traj], dtype=np.float64)
        dataset.append({'start': start, 'goal': goal, 'states': states, 'actions': actions})
    return dataset


def build_bc_samples(dataset: list[dict[str, np.ndarray]]) -> tuple[np.ndarray, np.ndarray]:
    xs, ys = [], []
    for ep in dataset:
        goal = ep['goal']
        for s, a in zip(ep['states'], ep['actions']):
            obs = np.concatenate([s, goal], axis=0)
            xs.append(obs)
            ys.append(a)
    return np.array(xs), np.array(ys)


def build_chunk_samples(dataset: list[dict[str, np.ndarray]], chunk_size: int) -> tuple[np.ndarray, np.ndarray]:
    xs, ys = [], []
    for ep in dataset:
        goal = ep['goal']
        states = ep['states']
        actions = ep['actions']
        if len(actions) < chunk_size:
            continue
        for i in range(0, len(actions) - chunk_size + 1):
            obs = np.concatenate([states[i], goal], axis=0)
            chunk = actions[i:i + chunk_size].reshape(-1)
            xs.append(obs)
            ys.append(chunk)
    return np.array(xs), np.array(ys)


def fit_linear_regression(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    x_aug = np.concatenate([x, np.ones((len(x), 1))], axis=1)
    w, *_ = np.linalg.lstsq(x_aug, y, rcond=None)
    return w


def predict_linear(w: np.ndarray, x: np.ndarray) -> np.ndarray:
    if x.ndim == 1:
        x = x[None, :]
    x_aug = np.concatenate([x, np.ones((len(x), 1))], axis=1)
    return x_aug @ w


def rollout_bc(w: np.ndarray, start: np.ndarray, goal: np.ndarray, max_steps: int = 20) -> RolloutResult:
    state = start.copy()
    traj = [state.tolist()]
    for t in range(max_steps):
        obs = np.concatenate([state, goal], axis=0)
        action = predict_linear(w, obs)[0]
        action = clip_norm(action, max_step=0.2)
        state = state + action
        traj.append(state.tolist())
        if np.linalg.norm(goal - state) < 0.05:
            return RolloutResult(float(np.linalg.norm(goal - state)), True, t + 1, traj)
    return RolloutResult(float(np.linalg.norm(goal - state)), False, max_steps, traj)


def rollout_chunk(w: np.ndarray, start: np.ndarray, goal: np.ndarray, chunk_size: int = 4, max_steps: int = 20) -> RolloutResult:
    state = start.copy()
    traj = [state.tolist()]
    t = 0
    while t < max_steps:
        obs = np.concatenate([state, goal], axis=0)
        chunk = predict_linear(w, obs)[0].reshape(chunk_size, 2)
        for action in chunk:
            action = clip_norm(action, max_step=0.2)
            state = state + action
            traj.append(state.tolist())
            t += 1
            if np.linalg.norm(goal - state) < 0.05:
                return RolloutResult(float(np.linalg.norm(goal - state)), True, t, traj)
            if t >= max_steps:
                break
    return RolloutResult(float(np.linalg.norm(goal - state)), False, max_steps, traj)


def evaluate_policy(
    bc_w: np.ndarray,
    chunk_w: np.ndarray,
    num_eval: int,
    chunk_size: int,
    max_steps: int,
) -> dict[str, object]:
    bc_results: list[RolloutResult] = []
    chunk_results: list[RolloutResult] = []
    for _ in range(num_eval):
        start = np.random.uniform(low=-1.0, high=1.0, size=(2,))
        goal = np.random.uniform(low=-1.0, high=1.0, size=(2,))
        bc_results.append(rollout_bc(bc_w, start, goal, max_steps=max_steps))
        chunk_results.append(rollout_chunk(chunk_w, start, goal, chunk_size=chunk_size, max_steps=max_steps))

    def aggregate(results: list[RolloutResult]) -> dict[str, object]:
        success_rate = float(np.mean([r.success for r in results]))
        mean_final_error = float(np.mean([r.final_error for r in results]))
        mean_steps = float(np.mean([r.num_steps for r in results]))
        return {
            'success_rate': success_rate,
            'mean_final_error': mean_final_error,
            'mean_steps': mean_steps,
            'sample_trajectories': [asdict(r) for r in results[:3]],
        }

    return {
        'bc': aggregate(bc_results),
        'chunk': aggregate(chunk_results),
    }


def maybe_plot(
    bc_w: np.ndarray,
    chunk_w: np.ndarray,
    chunk_size: int,
    output_path: Path,
) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        print('matplotlib not available, skip plotting.')
        return

    start = np.array([-0.9, -0.8], dtype=np.float64)
    goal = np.array([0.9, 0.8], dtype=np.float64)
    bc_result = rollout_bc(bc_w, start, goal)
    chunk_result = rollout_chunk(chunk_w, start, goal, chunk_size=chunk_size)

    bc_xy = np.array(bc_result.trajectory)
    chunk_xy = np.array(chunk_result.trajectory)

    plt.figure(figsize=(7, 6))
    plt.plot(bc_xy[:, 0], bc_xy[:, 1], marker='o', label='BC rollout')
    plt.plot(chunk_xy[:, 0], chunk_xy[:, 1], marker='o', label='Chunk rollout')
    plt.scatter([start[0]], [start[1]], marker='o', s=100, label='start')
    plt.scatter([goal[0]], [goal[1]], marker='*', s=200, label='goal')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Toy 2D point-mass rollout comparison')
    plt.legend()
    plt.axis('equal')
    plt.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_path)
    print(f'Saved plot to: {output_path}')


def save_report(report: dict[str, object], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f'Saved report to: {output_path}')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--num_train', type=int, default=400)
    parser.add_argument('--num_eval', type=int, default=80)
    parser.add_argument('--horizon', type=int, default=20)
    parser.add_argument('--chunk_size', type=int, default=4)
    parser.add_argument('--report_path', type=Path, default=Path('reports/ch04_toy_act_report.json'))
    parser.add_argument('--plot_path', type=Path, default=Path('reports/ch04_toy_act_rollout.png'))
    args = parser.parse_args()

    set_seed(args.seed)
    dataset = generate_dataset(num_episodes=args.num_train, horizon=args.horizon)

    bc_x, bc_y = build_bc_samples(dataset)
    chunk_x, chunk_y = build_chunk_samples(dataset, chunk_size=args.chunk_size)

    bc_w = fit_linear_regression(bc_x, bc_y)
    chunk_w = fit_linear_regression(chunk_x, chunk_y)

    report = {
        'task': 'toy_2d_point_mass',
        'seed': args.seed,
        'num_train': args.num_train,
        'num_eval': args.num_eval,
        'horizon': args.horizon,
        'chunk_size': args.chunk_size,
        'num_bc_samples': int(len(bc_x)),
        'num_chunk_samples': int(len(chunk_x)),
        'evaluation': evaluate_policy(
            bc_w=bc_w,
            chunk_w=chunk_w,
            num_eval=args.num_eval,
            chunk_size=args.chunk_size,
            max_steps=args.horizon,
        ),
    }
    save_report(report, args.report_path)
    maybe_plot(bc_w, chunk_w, chunk_size=args.chunk_size, output_path=args.plot_path)

    print('\nSummary')
    print('-' * 60)
    print(json.dumps(report['evaluation'], ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
