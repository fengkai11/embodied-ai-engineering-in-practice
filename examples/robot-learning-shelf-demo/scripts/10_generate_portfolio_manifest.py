#!/usr/bin/env python3
"""Generate a compact portfolio manifest and README template for the project."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


KEY_FILES = [
    'reports/ch16_act_dataset_v0_report.md',
    'reports/experiment_v1.md',
    'reports/experiment_v2.md',
    'reports/ch19_shelf_anomaly_report.md',
    'docs/portfolio_notes.md',
    'docs/interview_qa.md',
    'docs/resume_project_description.md',
]


def build_manifest(project_root: Path) -> dict:
    scripts = sorted([p.name for p in (project_root / 'scripts').glob('*.py')])
    reports = sorted([p.name for p in (project_root / 'reports').iterdir() if p.is_file()])
    docs = sorted([p.name for p in (project_root / 'docs').iterdir() if p.is_file()])
    datasets = sorted([p.name for p in (project_root / 'datasets').iterdir() if p.is_dir()])
    return {
        'project_name': project_root.name,
        'core_story': '从桌面任务的数据闭环出发，逐步扩展到评测、失败回流和货架理货方向。',
        'scripts': scripts,
        'datasets': datasets,
        'reports': reports,
        'docs': docs,
        'recommended_showcase_files': [k for k in KEY_FILES if (project_root / k).exists()],
    }


def build_readme_template(manifest: dict) -> str:
    lines = [
        '# 项目作品集模板',
        '',
        '## 1. 项目简介',
        manifest['core_story'],
        '',
        '## 2. 关键能力',
        '- 数据采集与 episode 设计',
        '- 模型训练与评测协议',
        '- 失败分析与数据闭环',
        '- 从桌面任务扩展到货架理货任务',
        '',
        '## 3. 推荐展示文件',
    ]
    for item in manifest['recommended_showcase_files']:
        lines.append(f'- `{item}`')
    lines += [
        '',
        '## 4. 项目结构',
        '- scripts/: 训练、评测、分析脚本',
        '- datasets/: 教学数据集',
        '- reports/: 实验报告与结果',
        '- docs/: 作品集、简历和面试材料',
        '',
        '## 5. 结果亮点',
        '- policy_v1 / policy_v2 的评测与对比',
        '- 失败 taxonomy 和 targeted data collection',
        '- 货架异常检测与任务扩展演示',
    ]
    return '\n'.join(lines) + '\n'


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--project_root', type=Path, required=True)
    parser.add_argument('--manifest_json', type=Path, required=True)
    parser.add_argument('--readme_template_md', type=Path, required=True)
    args = parser.parse_args()
    manifest = build_manifest(args.project_root)
    args.manifest_json.parent.mkdir(parents=True, exist_ok=True)
    args.manifest_json.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    args.readme_template_md.write_text(build_readme_template(manifest), encoding='utf-8')
    print(json.dumps({'recommended_showcase_files': manifest['recommended_showcase_files']}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
