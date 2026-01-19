---
name: vibe-ux-flow-design
description: "为功能定义用户交互与数据/状态流。在 spec 通过后使用，用于明确 UX 流程。"
---

# UX 流程设计

- 宣告："使用 vibe-ux-flow-design 定义交互流程。"
- 要求存在 `requirements/<feature>/spec.md`，缺失则停止并请求补齐。
- 读取 `requirements/<feature>/ux.md`，不存在则基于 `skills/_templates/ux.md` 创建。
- 记录入口、主流程、边界场景、状态转移、文案与权限。
- 将流程与用户故事、验收标准逐条对应。
- 汇总流程请求确认，并更新 `requirements/<feature>/status.md`。
