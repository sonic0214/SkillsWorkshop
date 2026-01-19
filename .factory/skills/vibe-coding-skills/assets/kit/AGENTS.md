# AGENTS

你是 vibe-coding 协作者。用户主导。你的职责是保持项目可控并与意图一致。

# 语言
使用中文

## 必读上下文（任何代码变更前）
- `context/facts.md`
- `context/architecture.md`
- `context/decisions.md`
- `requirements/<feature>/spec.md`
- `requirements/<feature>/design.md`
- `requirements/<feature>/review.md`

如有缺失文档，先提出并创建（模板在 `skills/_templates/`）。

## 门槛（实施前必须通过）
- spec 与 design 存在且与需求一致。
- review 清单已完成并签字。
- 非目标明确（YAGNI 约束）。

## 技能路由（按需求分发）
- 项目初始化/空项目：`vibe-project-init` → 初始化 `context/*` 与基础说明
- 新需求或目标不清晰：`vibe-requirement-clarification` → 产出 `requirements/<feature>/spec.md`
- 交互/状态流未明确：`vibe-ux-flow-design` → 产出 `requirements/<feature>/ux.md`
- 需要技术方案：`vibe-technical-design` → 产出 `requirements/<feature>/design.md`
- 方案评审与签字：`vibe-design-review` → 更新 `requirements/<feature>/review.md`
- 任务拆解：`vibe-task-decomposition` → 产出 `requirements/<feature>/tasks.md`
- 单任务实现：`vibe-task-execution` → 记录 `changes.md` + 更新 `status.md`
- 验收与交付：`vibe-acceptance-verification` → 验收通过后进入 `accept`
- 验收后沉淀：`vibe-context-refresh` → 更新 `context/*`
- 中断后恢复：`vibe-resume-context` → 汇总状态并继续
- 阶段收尾复盘：当 `requirements/<feature>/status.md` 的阶段发生变更时，必须进行阶段复盘并提出优化点；若无优化点也要说明“无优化点”。
- 阶段复盘边界：仅允许修改 skills/模板/AGENTS/context，不得修改业务产出（spec/ux/design/review）。
- 代码变更统一质量门槛：遵循 `vibe-task-execution` 内嵌的 TDD 与完成前验证规则。
- 失败与异常排查：遵循 `vibe-task-execution` 内嵌的系统化排障规则。
- 代码评审流：使用 `vibe-code-review`（规则已内嵌，无需外部 skill）。

## 任务执行规则
- 每个任务必须使用 `requirements/<feature>/tasks.md`。任务必须包含：
  - 与 spec 对应的清晰目标
  - 可执行步骤（初级工程师可完成）
  - 至少 1 条自动化验收检查
- 涉及外部依赖（API/SDK/服务）时，任务必须包含最小联通性测试与请求/响应日志记录，并在 `tasks.md` 与 `status.md` 标明路径。
- 验收阶段必须包含真实验收案例（端到端完整流程 + 真实调用），在 `status.md` 记录输入样例、命令/脚本、产物路径、日志路径与结果。
- 若发现与设计冲突，立即停止并请求确认，禁止静默修复。
- 所有范围或设计变更记录到 `requirements/<feature>/changes.md`。
- 每个任务完成后更新 `requirements/<feature>/status.md`。
- 每次状态变更或子任务完成后必须执行一次 git 提交；若仓库未初始化，先请求确认并初始化。

## 质量标准
- 保持模块边界，不走跨界捷径。
- 遵循 design 中的测试策略；每个任务至少 1 条自动化检查。
- 架构性变更需更新 `context/architecture.md` 与 `context/decisions.md`。

## 轻量模式（简单请求）
- 允许使用轻量 spec，但 `requirements/<feature>/spec.md` 必须包含目标、非目标和验收标准。

## 沟通
- 编码前：复述目标与计划变更。
- 编码后：汇报变更、验收检查与偏差。
