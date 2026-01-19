---
name: vibe-single-change
description: Use when handling a single requirement change or scope adjustment that needs clarification and sign-off before implementation
---

# 单个需求点变更

## 宣告

- 宣告："使用 vibe-single-change 处理单个需求点变更。"

## 适用范围

- 仅适用于单个需求点变更或单一行为调整。
- 不适用于多需求联动或大范围改造；需改用 `vibe-requirement-clarification` 与 `vibe-technical-design`。

## 核心流程

1. 苏格拉底式提问澄清需求（一次只问一个问题，优先多选）。
2. 给出技术方案建议（含变更文件、变更内容、影响范围、兼容性判断、验收标准）。
3. 用户确认执行后，创建变更文件夹并落地需求/方案文档。
4. 用户签字后开始开发；未签字不得开发。
5. 严格 TDD：先写单测并确认失败，再实现，测试全绿。
6. 按验收标准验收通过后，更新上下文沉淀。

## 澄清问题模板（一次一个问题）

- 背景：变更触发原因是什么？现有行为哪里不满足？
- 目的：希望解决的核心问题是什么？成功标准是什么？
- 范围：涉及哪些页面/接口/模块？明确不做的范围？
- 行为：当前行为与期望行为差异是什么？
- 约束：时间、兼容性、外部依赖、数据迁移是否受限？
- 验收：用 2-3 条可测试的验收标准描述结果。

## 变更文件夹规范

默认路径：`requirements/<feature>/changes/<YYYYMMDD>-<slug>/`

文件清单：
- `requirement.md`：需求描述文件
- `tech-plan.md`：技术方案文件

> 若用户指定其他路径，以用户意见为准。

## 需求描述模板（requirement.md）

```
# 需求描述：<变更标题>

## 背景
- 现状与痛点：

## 目的
- 目标：

## 范围
- 做：
- 不做：

## 当前行为
- 现状：

## 期望行为
- 目标行为：

## 验收标准
- [ ] 条件 1：
- [ ] 条件 2：

## 风险与约束
- 风险：
- 约束：
```

## 技术方案模板（tech-plan.md）

```
# 技术方案：<变更标题>

## 变更文件
- <路径>：<变更内容>

## 影响范围
- 影响模块：
- 影响用户：

## 兼容性判断
- 向前兼容：
- 向后兼容：
- 迁移/回滚：

## 验收标准
- [ ] 条件 1：
- [ ] 条件 2：
```

## 执行规则

- 未确认执行前，不创建变更文件夹。
- 未签字前，不开始开发。
- 发现与设计/约束冲突，立刻停止并请求确认。

## TDD 与验收

- Red：新增/调整单测并确认失败。
- Green：最小实现通过测试。
- Refactor：保持全绿再重构。
- 验收：对照 `tech-plan.md` 的验收标准逐条验证。

## 上下文沉淀

- 更新 `requirements/<feature>/changes.md` 与 `requirements/<feature>/status.md`。
- 若涉及架构/决策变化，更新 `context/architecture.md` 与 `context/decisions.md`。
- 必要时补充 `context/facts.md`。
