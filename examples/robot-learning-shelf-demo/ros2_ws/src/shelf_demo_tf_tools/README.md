# shelf_demo_tf_tools

本目录对应第 11 章的教学型 ROS2/TF 辅助模块，用于说明：

- `world / base_link / camera_link / ee_link / object_frame` 之间的关系；
- 如何通过静态变换描述相机安装；
- 如何把视觉点位转换到机器人可执行坐标系。

当前整合包不强依赖完整 ROS2 环境，因此这里保留轻量目录结构与说明文档，读者可后续扩展为：

```text
shelf_demo_tf_tools/
  launch/
    static_tf_demo.launch.py
  config/
    camera_extrinsics.yaml
  scripts/
    publish_demo_tf.py
```

在本书主线里，真正可直接运行的几何计算示例位于：

```text
scripts/geometry_utils.py
```
