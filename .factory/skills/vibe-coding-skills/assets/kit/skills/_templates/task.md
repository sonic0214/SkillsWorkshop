---
description: "功能实现任务清单模板"
---

# 任务清单：<FEATURE NAME>

**输入**：`requirements/<feature>/` 下的设计文档（spec.md, ux.md, design.md, review.md）
**前置条件**：spec.md（必需）、design.md（必需）、review.md（已签字）

**测试**：强制 TDD。每个用户故事必须包含测试任务，先写测试再实现。验收阶段必须包含至少 1 条自动化冒烟用例，并在 status.md 记录运行结果。若涉及外部依赖，任务需包含最小联通性测试与请求/响应日志记录，并标明路径。

**组织方式**：按用户故事分组，确保每个故事可独立实现与验证。

## 格式：`[ID] [P?] [Story] 说明`

- **[P]**：可并行（不同文件、无依赖）
- **[Story]**：所属用户故事（如 US1, US2, US3）
- 描述必须包含 `workspace/` 下的准确文件路径

## 路径约定

- 以 `requirements/<feature>/design.md` 的目录结构为准
- 统一放在 `workspace/` 下

## 阶段 1：初始化（共享基础设施）

**目的**：项目初始化与基础结构

- [ ] T001 按设计创建 `workspace/` 结构
- [ ] T002 初始化项目基础（框架/构建/依赖）（`workspace/`）
- [ ] T003 [P] 配置 lint/format 与测试运行器（`workspace/`）
- [ ] CR01 阶段 1 代码评审（使用 `vibe-code-review`；产出：`requirements/<feature>/reviews/CR01.md`，模板：`skills/_templates/code-review.md`；通过后进入阶段 2）

---

## 阶段 2：基础能力（阻塞前置）

**目的**：所有用户故事实现前必须完成的基础能力

- [ ] T004 搭建核心入口/接口骨架（按设计路径）
- [ ] T005 [P] 实现共享类型/DTO/Schema（按设计路径）
- [ ] T006 [P] 实现核心存储/适配层（如有）（按设计路径）
- [ ] T007 配置环境变量示例/配置模板（`workspace/`）
- [ ] CR02 阶段 2 代码评审（使用 `vibe-code-review`；产出：`requirements/<feature>/reviews/CR02.md`，模板：`skills/_templates/code-review.md`；通过后进入用户故事阶段）

**检查点**：基础能力完成且代码评审通过后，用户故事可并行推进

---

## 阶段 3：用户故事 1 - [Title]（优先级：P1）

**目标**：[该故事交付的结果]

**独立验证**：[如何单独验证该故事可用]

### 用户故事 1 的测试（强制 TDD，MECE）

- [ ] T010 [P] [US1] API 测试：[endpoint]（按设计路径）
- [ ] T011 [P] [US1] 集成测试：[模块边界]（按设计路径）
- [ ] T012 [P] [US1] E2E 测试：[故事流程]（按设计路径）

### 用户故事 1 的实现

- [ ] T013 [P] [US1] 实现 [module]（按设计路径）
- [ ] T014 [US1] 实现 [API]（按设计路径）
- [ ] T015 [US1] 实现 [UI]（按设计路径）
- [ ] CR03 阶段 3 代码评审（覆盖 US1 测试与实现；使用 `vibe-code-review`；产出：`requirements/<feature>/reviews/CR03.md`，模板：`skills/_templates/code-review.md`；通过后进入阶段 4）

**检查点**：用户故事 1 可独立运行与测试，且代码评审通过

---

## 阶段 4：用户故事 2 - [Title]（优先级：P2）

**目标**：[该故事交付的结果]

**独立验证**：[如何单独验证该故事可用]

### 用户故事 2 的测试（强制 TDD，MECE）

- [ ] T020 [P] [US2] API 测试：[endpoint]（按设计路径）
- [ ] T021 [P] [US2] 集成测试：[模块边界]（按设计路径）
- [ ] T022 [P] [US2] E2E 测试：[故事流程]（按设计路径）

### 用户故事 2 的实现

- [ ] T023 [P] [US2] 实现 [module]（按设计路径）
- [ ] T024 [US2] 实现 [API]（按设计路径）
- [ ] T025 [US2] 实现 [UI]（按设计路径）
- [ ] CR04 阶段 4 代码评审（覆盖 US2 测试与实现；使用 `vibe-code-review`；产出：`requirements/<feature>/reviews/CR04.md`，模板：`skills/_templates/code-review.md`；通过后进入下一阶段）

**检查点**：用户故事 2 可独立运行与测试，且代码评审通过

---

## 阶段 N：收尾与横切关注点

**目的**：影响多个用户故事的改进

- [ ] TXXX [P] 更新文档（`requirements/<feature>/` 与 `workspace/`）
- [ ] TXXX 代码清理与重构
- [ ] TXXX 跨故事性能优化
- [ ] TXXX 安全加固
- [ ] CR06 收尾阶段代码评审（覆盖变更与验收；使用 `vibe-code-review`；产出：`requirements/<feature>/reviews/CR06.md`，模板：`skills/_templates/code-review.md`；通过后进入验收）

---

## 依赖与执行顺序

- 初始化（阶段1）→ 代码评审 → 基础能力（阶段2）→ 代码评审 → 用户故事（阶段3+，每阶段结束代码评审）→ 收尾（最终）
- 每个用户故事内：测试先行 → 实现 → 验证 → 检查点

## 并行机会

- 所有标记 [P] 的任务可并行
- 基础能力完成后，不同用户故事可并行推进
