# Chapter 19 Shelf Anomaly Report

- num_slots: `6`
- status_counter: `{'normal': 3, 'missing': 1, 'misplaced': 1, 'tilted': 1}`
- priority_action: `restock_missing_items`

## Per-slot Result

| slot_id | expected_sku | observed_sku | status | tilt_deg | note |
|---|---|---|---|---:|---|
| A1 | tea_01 | tea_01 | normal | 2.0 | 状态正常 |
| A2 | tea_02 | None | missing | 0.0 | 格口空缺或占用率过低 |
| A3 | juice_01 | juice_02 | misplaced | 4.0 | 观察商品与目标 SKU 不一致 |
| B1 | milk_01 | milk_01 | tilted | 18.5 | 商品倾角过大，需扶正 |
| B2 | milk_02 | milk_02 | normal | 3.0 | 状态正常 |
| B3 | snack_01 | snack_01 | normal | 1.0 | 状态正常 |

## Interpretation

本报告展示了理货机器人中的一个典型前置问题：在进行扶正、补货或抓取前，系统首先需要知道每个格口处于什么状态。
在真实系统中，`missing / misplaced / tilted / normal` 的判断会由多模态感知模块完成；此处使用教学化规则脚本，帮助读者先理解数据结构与任务分解。