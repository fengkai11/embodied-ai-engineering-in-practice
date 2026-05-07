# Dataset Validation Report

- dataset_dir: `datasets/dataset_v0_bad_examples`
- total_episodes: `4`
- ok_episodes: `0`
- bad_episodes: `4`

## Episode Results

### ❌ episode_bad_action_range

- task_name: `pick_box_to_bin`
- success: `True`
- failure_reason: `None`
- num_states: `7`
- num_actions: `7`
- front_image_count: `7`
- wrist_image_count: `7`
- issues:
  - action out of range: 2 sample(s)

### ❌ episode_bad_label_conflict

- task_name: `pick_box_to_bin`
- success: `True`
- failure_reason: `drop_during_transfer`
- num_states: `7`
- num_actions: `7`
- front_image_count: `7`
- wrist_image_count: `7`
- issues:
  - label conflict: success=true but failure_reason is non-empty

### ❌ episode_bad_missing_meta

- task_name: `None`
- success: `None`
- failure_reason: `None`
- num_states: `7`
- num_actions: `7`
- front_image_count: `7`
- wrist_image_count: `7`
- issues:
  - missing meta.json

### ❌ episode_bad_timestamp

- task_name: `pick_box_to_bin`
- success: `True`
- failure_reason: `None`
- num_states: `7`
- num_actions: `7`
- front_image_count: `7`
- wrist_image_count: `7`
- issues:
  - state timestamps are not monotonically increasing
  - state timestamps do not match action timestamps
