# Pseudo launch file used for teaching purposes only.
from dataclasses import dataclass

@dataclass
class NodeSpec:
    package: str
    executable: str
    name: str


def generate_launch_description():
    return [
        NodeSpec(package='shelf_demo_camera', executable='camera_node', name='camera_node'),
        NodeSpec(package='shelf_demo_state', executable='robot_state_node', name='robot_state_node'),
        NodeSpec(package='shelf_demo_data_recorder', executable='data_recorder_node', name='data_recorder_node'),
    ]
