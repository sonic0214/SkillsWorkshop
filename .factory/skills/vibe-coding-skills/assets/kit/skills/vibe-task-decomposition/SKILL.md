---
name: vibe-task-decomposition
description: "将已通过评审的方案拆分为小而可执行的任务清单（tasks.md），按用户故事组织并以TDD驱动开发、MECE拆解测试任务。在实现前使用。"
---

# 任务拆解

- 宣告："使用 vibe-task-decomposition 生成任务。"
- 要求存在 `requirements/<feature>/spec.md`、`requirements/<feature>/design.md`，且 `requirements/<feature>/review.md` 已签字。
- 在 `requirements/<feature>/tasks.md` 输出清单，按 `skills/_templates/task.md` 的格式生成（参考 spec-kit tasks-template）。
- 任务按用户故事组织（US1/US2/...），每个故事可独立实现与验证。
- 任务拆解粒度必须到“方法实现级别”，单任务执行时间不超过 1 小时。
- 每个任务聚焦单一模块或单一变更点，描述中包含**准确文件路径**，上下文自洽即可执行。
- 每个用户故事**必须**先列出测试任务（TDD：红→绿→重构），再列实现任务。
- 测试任务采用 MECE 拆解（互斥且穷尽），每个测试只能属于一个类型：
  - API 级（请求/响应/错误码）
  - 模块集成级（模块协作边界）
  - 端到端（User Story 流程）
- 使用任务格式：`- [ ] T001 [P?] [US?] 说明（含路径）`，并标注可并行项 `[P]`。
- 禁止直接输出模板中的占位阶段名（如“阶段 N”）；阶段名称必须具体（如“收尾与横切关注点”/“验收准备”），或在不需要时移除该阶段。
- 若模板结构与任务规模不匹配，允许精简/合并阶段，但不得牺牲测试先行与独立验证要求。
- 更新 `requirements/<feature>/status.md` 中的任务清单。
