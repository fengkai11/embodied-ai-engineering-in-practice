#!/usr/bin/env python3
"""Build dataset_v0 by merging scripted and teleop demo episodes."""
from __future__ import annotations

import argparse
import json
import math
import random
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Any


def scan_episode_dirs(dataset_dir: Path) -> list[Path]:
    if not dataset_dir.exists():
        return []
    candidates = []
    for p in sorted(dataset_dir.rglob('meta.json')):
        candidates.append(p.parent)
    return candidates


def load_meta(ep_dir: Path) -> dict[str, Any]:
    meta = json.loads((ep_dir / 'meta.json').read_text(encoding='utf-8'))
    if 'source' not in meta:
        if 'expert_type' in meta:
            meta['source'] = meta['expert_type']
        elif 'scripted' in ep_dir.as_posix():
            meta['source'] = 'scripted_expert'
        else:
            meta['source'] = 'unknown'
    return meta


def stratified_split(items: list[dict[str, Any]], seed: int, ratios: tuple[float, float, float]) -> dict[str, list[dict[str, Any]]]:
    rng = random.Random(seed)
    groups: dict[tuple[str, bool], list[dict[str, Any]]] = defaultdict(list)
    for item in items:
        key = (item['meta'].get('source', 'unknown'), bool(item['meta'].get('success', False)))
        groups[key].append(item)

    out = {'train': [], 'val': [], 'test': []}
    for key, group in groups.items():
        rng.shuffle(group)
        n = len(group)
        n_train = max(1, int(round(n * ratios[0]))) if n >= 3 else max(1, n - 2 if n > 2 else n)
        n_val = max(1, int(round(n * ratios[1]))) if n >= 3 else (1 if n >= 2 else 0)
        n_test = n - n_train - n_val
        if n >= 3 and n_test <= 0:
            n_test = 1
            n_train = max(1, n_train - 1)
        if n_val < 0:
            n_val = 0
        train_group = group[:n_train]
        val_group = group[n_train:n_train + n_val]
        test_group = group[n_train + n_val:]
        out['train'].extend(train_group)
        out['val'].extend(val_group)
        out['test'].extend(test_group)
    for split in out:
        rng.shuffle(out[split])
    return out


def copy_episode(src: Path, dst: Path, new_id: str) -> dict[str, Any]:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    meta_path = dst / 'meta.json'
    meta = json.loads(meta_path.read_text(encoding='utf-8'))
    meta['episode_id'] = new_id
    meta['original_episode_id'] = src.name
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
    return meta


def summarize(split_map: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    report: dict[str, Any] = {'splits': {}, 'overall': {}}
    overall_counter = Counter()
    success_counter = Counter()
    for split, items in split_map.items():
        source_counter = Counter(item['meta'].get('source', 'unknown') for item in items)
        split_success = sum(1 for item in items if item['meta'].get('success'))
        report['splits'][split] = {
            'num_episodes': len(items),
            'success_count': split_success,
            'failure_count': len(items) - split_success,
            'success_rate': round(split_success / len(items), 4) if items else 0.0,
            'source_counter': dict(source_counter),
        }
        overall_counter.update(source_counter)
        success_counter['success'] += split_success
        success_counter['failure'] += len(items) - split_success
    total = success_counter['success'] + success_counter['failure']
    report['overall'] = {
        'num_episodes': total,
        'success_count': success_counter['success'],
        'failure_count': success_counter['failure'],
        'success_rate': round(success_counter['success'] / total, 4) if total else 0.0,
        'source_counter': dict(overall_counter),
    }
    return report


def write_markdown(report: dict[str, Any], output_path: Path, dataset_name: str, version: str) -> None:
    lines = [
        f'# {dataset_name} report',
        '',
        f'- version: `{version}`',
        f"- total_episodes: `{report['overall']['num_episodes']}`",
        f"- success_rate: `{report['overall']['success_rate']}`",
        '',
        '## Splits',
        '',
        '| split | episodes | success | failure | success_rate | sources |',
        '|---|---:|---:|---:|---:|---|',
    ]
    for split in ('train', 'val', 'test'):
        r = report['splits'][split]
        lines.append(f"| {split} | {r['num_episodes']} | {r['success_count']} | {r['failure_count']} | {r['success_rate']} | {r['source_counter']} |")
    lines += [
        '',
        '## Design Notes',
        '',
        '- 本教学版数据集来自规则 expert 数据与键盘遥操作模拟数据。',
        '- 数据按 `source × success` 做轻量分层，再划分 train/val/test。',
        '- 该紧凑版本用于教学与 baseline 训练；实际项目可进一步扩展数据规模、随机化与场景覆盖。',
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text('\n'.join(lines), encoding='utf-8')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--source_dirs', nargs='+', type=Path, required=True)
    parser.add_argument('--output_dir', type=Path, required=True)
    parser.add_argument('--seed', type=int, default=2026)
    parser.add_argument('--dataset_name', type=str, default='dataset_v0')
    parser.add_argument('--version', type=str, default='v0.0.0')
    parser.add_argument('--report_json', type=Path, default=None)
    parser.add_argument('--report_md', type=Path, default=None)
    args = parser.parse_args()

    if args.output_dir.exists():
        shutil.rmtree(args.output_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / 'train').mkdir()
    (args.output_dir / 'val').mkdir()
    (args.output_dir / 'test').mkdir()
    (args.output_dir / 'splits').mkdir()

    items = []
    for src_root in args.source_dirs:
        for ep_dir in scan_episode_dirs(src_root):
            meta = load_meta(ep_dir)
            items.append({'path': ep_dir, 'meta': meta, 'source_root': str(src_root)})

    split_map = stratified_split(items, seed=args.seed, ratios=(0.7, 0.15, 0.15))

    manifest = {'dataset_name': args.dataset_name, 'version': args.version, 'source_dirs': [str(p) for p in args.source_dirs], 'splits': {}}
    new_index = 1
    for split in ('train', 'val', 'test'):
        manifest['splits'][split] = []
        for item in split_map[split]:
            new_id = f'episode_{new_index:05d}'
            dst = args.output_dir / split / new_id
            new_meta = copy_episode(item['path'], dst, new_id)
            manifest['splits'][split].append({'episode_id': new_id, 'source': new_meta.get('source'), 'success': new_meta.get('success')})
            new_index += 1
        (args.output_dir / 'splits' / f'{split}.json').write_text(json.dumps(manifest['splits'][split], ensure_ascii=False, indent=2), encoding='utf-8')

    report = summarize({split: [{'meta': load_meta(args.output_dir / split / x['episode_id'])} for x in manifest['splits'][split]] for split in ('train', 'val', 'test')})
    dataset_card = {
        'dataset_name': args.dataset_name,
        'version': args.version,
        'num_episodes': report['overall']['num_episodes'],
        'success_rate': report['overall']['success_rate'],
        'splits': {k: report['splits'][k]['num_episodes'] for k in report['splits']},
        'source_counter': report['overall']['source_counter'],
        'task_name': 'pick_box_to_bin',
        'modalities': ['front_rgb', 'wrist_rgb', 'robot_state'],
        'note': 'Compact teaching dataset used for Chapter 15 and Chapter 16 baseline training.',
    }
    (args.output_dir / 'dataset_card.json').write_text(json.dumps(dataset_card, ensure_ascii=False, indent=2), encoding='utf-8')
    (args.output_dir / 'README.md').write_text(
        f"# {args.dataset_name}\n\n- version: `{args.version}`\n- num_episodes: `{report['overall']['num_episodes']}`\n- splits: train/val/test\n- source_counter: `{report['overall']['source_counter']}`\n",
        encoding='utf-8',
    )
    (args.output_dir / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

    if args.report_json is not None:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    if args.report_md is not None:
        write_markdown(report, args.report_md, args.dataset_name, args.version)

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
