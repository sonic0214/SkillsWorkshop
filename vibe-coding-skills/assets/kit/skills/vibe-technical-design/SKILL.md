---
name: vibe-technical-design
description: "在 spec/UX 稳定后产出完整技术方案（接口、模型、领域模型、业务架构、代码架构、数据流与测试用例）。在任务拆解或实现前使用。"
---

# 技术方案设计

- 宣告："使用 vibe-technical-design 生成技术方案。"
- 要求存在 `requirements/<feature>/spec.md`；如有 `requirements/<feature>/ux.md` 也需读取。
- 基于 `skills/_templates/design.md` 创建或更新 `requirements/<feature>/design.md`。
- 必须包含：接口设计、数据模型、领域模型、业务架构、代码架构、代码目录结构、关键数据流。
- 如涉及 LLM/图像模型，必须给出提示词模板、占位符变量与模板存放路径。
- 明确设计模式/原则与关键权衡（例如：管道/状态机/队列、单体/拆分）。
- 定义异常处理策略、安全与性能假设。
- 测试用例必须覆盖：
  - 接口层级（API 请求/响应与错误码）
  - 模块层级的集成测试
  - 基于用户故事的端到端测试
- 明确非目标以避免范围蔓延。
- 将 `requirements/<feature>/status.md` 阶段更新为 `design`。
