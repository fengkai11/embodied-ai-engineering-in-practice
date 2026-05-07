#!/usr/bin/env python3
"""Train a tiny ACT-like baseline on dataset_v0.

This is a teaching implementation: it predicts a fixed-length action chunk from a
single-step observation feature vector using a lightweight linear model trained
with gradient descent.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import matplotlib.pyplot as plt


@dataclass
class Sample:
    x: np.ndarray
    y: np.ndarray


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def feature_from_state(state: dict[str, Any]) -> np.ndarray:
    ee = np.array(state['ee_pose_xyzrpy'][:3], dtype=np.float32)
    gripper = np.array([1.0 if state.get('gripper_open', False) else 0.0], dtype=np.float32)
    obj = np.array(state.get('object_pose_xyz', [0.0, 0.0, 0.0]), dtype=np.float32)
    bin_xyz = np.array(state.get('bin_pose_xyz', [0.0, 0.0, 0.0]), dtype=np.float32)
    rel_obj = obj - ee
    rel_bin = bin_xyz - ee
    return np.concatenate([ee, gripper, obj, bin_xyz, rel_obj, rel_bin], axis=0)


def action_vec(action: dict[str, Any]) -> np.ndarray:
    d = np.array(action['delta_ee_xyzrpy'][:3] + [action.get('gripper_delta', 0.0)], dtype=np.float32)
    return d


def load_split(dataset_root: Path, split: str, chunk_size: int = 4) -> list[Sample]:
    split_dir = dataset_root / split
    samples: list[Sample] = []
    for ep_dir in sorted(x for x in split_dir.iterdir() if x.is_dir()):
        states = load_jsonl(ep_dir / 'states.jsonl')
        actions = load_jsonl(ep_dir / 'actions.jsonl')
        if len(states) < chunk_size + 1 or len(actions) < chunk_size:
            continue
        T = min(len(states), len(actions))
        for t in range(T - chunk_size):
            x = feature_from_state(states[t])
            chunk = [action_vec(actions[t + k]) for k in range(chunk_size)]
            y = np.concatenate(chunk, axis=0)
            samples.append(Sample(x=x, y=y))
    return samples


def stack_samples(samples: list[Sample]) -> tuple[np.ndarray, np.ndarray]:
    X = np.stack([s.x for s in samples], axis=0)
    Y = np.stack([s.y for s in samples], axis=0)
    return X, Y


def normalize(train_x: np.ndarray, val_x: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    mean = train_x.mean(axis=0, keepdims=True)
    std = train_x.std(axis=0, keepdims=True) + 1e-6
    return (train_x - mean) / std, (val_x - mean) / std, mean.squeeze(0), std.squeeze(0)


def mse(pred: np.ndarray, target: np.ndarray) -> float:
    return float(np.mean((pred - target) ** 2))


def train_linear_chunk_model(X_train: np.ndarray, Y_train: np.ndarray, X_val: np.ndarray, Y_val: np.ndarray, epochs: int, lr: float, weight_decay: float) -> tuple[np.ndarray, dict[str, list[float]]]:
    n, d = X_train.shape
    out_dim = Y_train.shape[1]
    rng = np.random.default_rng(0)
    W = rng.normal(scale=0.05, size=(d, out_dim)).astype(np.float32)
    b = np.zeros((1, out_dim), dtype=np.float32)
    history = {'train_loss': [], 'val_loss': []}
    for _ in range(epochs):
        pred = X_train @ W + b
        err = pred - Y_train
        grad_W = (2.0 / n) * (X_train.T @ err) + weight_decay * W
        grad_b = (2.0 / n) * err.sum(axis=0, keepdims=True)
        W -= lr * grad_W
        b -= lr * grad_b
        history['train_loss'].append(mse(X_train @ W + b, Y_train))
        history['val_loss'].append(mse(X_val @ W + b, Y_val))
    params = np.concatenate([W, b], axis=0)
    return params, history


def predict(params: np.ndarray, X: np.ndarray) -> np.ndarray:
    W = params[:-1]
    b = params[-1:]
    return X @ W + b


def save_curve(history: dict[str, list[float]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(6, 4))
    plt.plot(history['train_loss'], label='train_loss')
    plt.plot(history['val_loss'], label='val_loss')
    plt.xlabel('epoch')
    plt.ylabel('MSE loss')
    plt.title('ACT-like baseline training curve')
    plt.legend()
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def rollout_preview(dataset_root: Path, split: str, params: np.ndarray, mean: np.ndarray, std: np.ndarray, chunk_size: int) -> dict[str, Any]:
    split_dir = dataset_root / split
    ep_dir = next(x for x in sorted(split_dir.iterdir()) if x.is_dir())
    states = load_jsonl(ep_dir / 'states.jsonl')
    actions = load_jsonl(ep_dir / 'actions.jsonl')
    records = []
    horizon = min(5, len(actions) - chunk_size)
    for t in range(horizon):
        x = feature_from_state(states[t])
        x_n = ((x - mean) / std)[None, :]
        pred = predict(params, x_n)[0].reshape(chunk_size, 4)
        gt = np.stack([action_vec(actions[t + k]) for k in range(chunk_size)], axis=0)
        records.append({
            't': t,
            'pred_first_action': pred[0].round(4).tolist(),
            'gt_first_action': gt[0].round(4).tolist(),
        })
    return {'episode_id': ep_dir.name, 'records': records}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset_root', type=Path, required=True)
    parser.add_argument('--chunk_size', type=int, default=4)
    parser.add_argument('--epochs', type=int, default=60)
    parser.add_argument('--lr', type=float, default=0.08)
    parser.add_argument('--weight_decay', type=float, default=1e-4)
    parser.add_argument('--checkpoint_path', type=Path, required=True)
    parser.add_argument('--report_json', type=Path, required=True)
    parser.add_argument('--curve_path', type=Path, required=True)
    args = parser.parse_args()

    train_samples = load_split(args.dataset_root, 'train', chunk_size=args.chunk_size)
    val_samples = load_split(args.dataset_root, 'val', chunk_size=args.chunk_size)
    X_train, Y_train = stack_samples(train_samples)
    X_val, Y_val = stack_samples(val_samples)
    X_train_n, X_val_n, mean, std = normalize(X_train, X_val)
    params, history = train_linear_chunk_model(X_train_n, Y_train, X_val_n, Y_val, epochs=args.epochs, lr=args.lr, weight_decay=args.weight_decay)

    pred_train = predict(params, X_train_n)
    pred_val = predict(params, X_val_n)
    train_loss = mse(pred_train, Y_train)
    val_loss = mse(pred_val, Y_val)
    first_step_train = mse(pred_train.reshape(-1, args.chunk_size, 4)[:, 0], Y_train.reshape(-1, args.chunk_size, 4)[:, 0])
    first_step_val = mse(pred_val.reshape(-1, args.chunk_size, 4)[:, 0], Y_val.reshape(-1, args.chunk_size, 4)[:, 0])

    rollout = rollout_preview(args.dataset_root, 'val', params, mean, std, args.chunk_size)

    args.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(args.checkpoint_path, params=params, mean=mean, std=std, chunk_size=args.chunk_size)
    save_curve(history, args.curve_path)

    report = {
        'dataset_root': str(args.dataset_root),
        'chunk_size': args.chunk_size,
        'feature_dim': int(X_train.shape[1]),
        'output_dim': int(Y_train.shape[1]),
        'num_train_samples': int(X_train.shape[0]),
        'num_val_samples': int(X_val.shape[0]),
        'epochs': args.epochs,
        'learning_rate': args.lr,
        'weight_decay': args.weight_decay,
        'final_train_loss': round(train_loss, 6),
        'final_val_loss': round(val_loss, 6),
        'first_step_train_loss': round(first_step_train, 6),
        'first_step_val_loss': round(first_step_val, 6),
        'rollout_preview': rollout,
    }
    args.report_json.parent.mkdir(parents=True, exist_ok=True)
    args.report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
