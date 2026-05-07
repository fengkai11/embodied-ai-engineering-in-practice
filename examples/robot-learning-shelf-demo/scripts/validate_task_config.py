#!/usr/bin/env python3
"""Validate robot task YAML configs for the shelf demo project."""
from __future__ import annotations

from pathlib import Path
import argparse
import json

REQUIRED_TOP_LEVEL_KEYS = [
    'task_name',
    'version',
    'description',
    'initial_state',
    'goal_state',
    'action_space',
    'observation',
    'success_criteria',
    'failure_criteria',
]

REQUIRED_ACTION_KEYS = ['mode', 'action_dim']
REQUIRED_OBS_KEYS = ['modalities']


def load_yaml(path: Path) -> dict:
    try:
        import yaml  # type: ignore
    except Exception as exc:
        raise RuntimeError('PyYAML is required to validate YAML configs.') from exc
    with path.open('r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError('YAML root must be a mapping / dict.')
    return data


def validate_config(data: dict) -> dict:
    errors: list[str] = []
    warnings: list[str] = []

    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in data:
            errors.append(f'missing top-level key: {key}')

    action_space = data.get('action_space', {})
    if isinstance(action_space, dict):
        for key in REQUIRED_ACTION_KEYS:
            if key not in action_space:
                errors.append(f'missing action_space.{key}')
        if 'limits' not in action_space:
            warnings.append('action_space.limits is missing; action bounds may be unclear')
    else:
        errors.append('action_space must be a dict')

    obs = data.get('observation', {})
    if isinstance(obs, dict):
        for key in REQUIRED_OBS_KEYS:
            if key not in obs:
                errors.append(f'missing observation.{key}')
    else:
        errors.append('observation must be a dict')

    succ = data.get('success_criteria', {})
    fail = data.get('failure_criteria', {})
    if not succ:
        errors.append('success_criteria cannot be empty')
    if not fail:
        errors.append('failure_criteria cannot be empty')
    if 'timeout_sec' not in fail:
        warnings.append('failure_criteria.timeout_sec missing; timeout behavior may be ambiguous')

    rand = data.get('randomization')
    if rand is None:
        warnings.append('randomization section missing; training/evaluation diversity may be limited')

    summary = {
        'task_name': data.get('task_name'),
        'version': data.get('version'),
        'observation_modalities': data.get('observation', {}).get('modalities', []),
        'action_mode': data.get('action_space', {}).get('mode'),
        'num_success_criteria': len(data.get('success_criteria', {})) if isinstance(data.get('success_criteria', {}), dict) else 0,
        'num_failure_criteria': len(data.get('failure_criteria', {})) if isinstance(data.get('failure_criteria', {}), dict) else 0,
    }

    return {
        'ok': len(errors) == 0,
        'errors': errors,
        'warnings': warnings,
        'summary': summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=None)
    args = parser.parse_args()

    data = load_yaml(args.config)
    report = validate_config(data)
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'Saved validation report to: {args.output}')


if __name__ == '__main__':
    main()
