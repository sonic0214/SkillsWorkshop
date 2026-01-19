---
name: vibe-requirement-clarification
description: "将模糊需求澄清为最小可执行的 spec，包含用户故事与验收标准。用于新功能启动或目标不清晰时，在任何设计或代码变更之前。"
---

# 需求澄清

- 宣告："使用 vibe-requirement-clarification 生成 spec。"
- 若存在则读取 `requirements/<feature>/spec.md`，否则基于 `skills/_templates/spec.md` 创建。
- 一次只问一个问题，优先多选。聚焦目标、非目标、主要用户、核心流程、约束与成功标准。
- 存在歧义时给出 2-3 个方案并推荐其一。
- 执行 YAGNI：从目标与用户故事中剔除不必要范围。
- 完整填写 spec：背景、目标/非目标、用户故事、验收标准、约束与风险。
- 与用户确认并将 `requirements/<feature>/status.md` 阶段更新为 `spec`。
