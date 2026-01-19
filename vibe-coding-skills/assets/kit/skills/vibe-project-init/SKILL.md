---
name: vibe-project-init
description: "初始化项目上下文与结构：空项目创建基础模板；已有项目基于现状分析并初始化 context 文档。"
---

# 项目初始化

- 宣告："使用 vibe-project-init 初始化项目。"
- 目标：保证 `context/*` 与项目基础说明可用，为后续需求与实现提供起点。

## 1. 判定项目类型

- **空项目**（满足多数即可）：
  - `context/facts.md` / `context/architecture.md` / `context/decisions.md` 不存在
  - `requirements/` 下没有任何 `<feature>` 子目录
  - 代码目录缺失或仅为空目录（如 `workspace/` 不存在）
- **已有项目**：存在可读的代码/文档结构（README、包管理文件、配置、源码目录等）。
- 若判断不确定，先用 1 个问题与用户确认，不要猜。

## 2. 空项目初始化

- 基于 `context/_templates/` 创建：
  - `context/facts.md`
  - `context/architecture.md`
  - `context/decisions.md`
- 在 `requirements/README.md` 简述目录用途与后续流程入口（引用 AGENTS 规则即可）。
- 不臆造业务内容；仅提供模板与待填项。

## 3. 已有项目初始化

- 快速盘点：读取 README、依赖/构建配置、主要目录结构与入口文件。
- 生成/更新 `context/*`：
  - **facts**：产品背景、目标、约束、里程碑（未知项标注 TODO）。
  - **architecture**：系统边界、关键模块、主要数据流、目录约定。
  - **decisions**：记录显式技术选型与取舍（未知项标注 TODO）。
- 结尾输出：已填内容、未确认点、需要用户补充的问题（不超过 3 个）。

## 4. 约束

- 不对业务/架构做推测性结论。
- 不修改 `requirements/<feature>` 中的业务产物。
- 若发现与既有事实冲突，先停并请用户确认。
