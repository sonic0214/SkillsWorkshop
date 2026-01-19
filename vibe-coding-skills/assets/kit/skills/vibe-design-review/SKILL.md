---
name: vibe-design-review
description: "审查技术方案是否完整且合理（包含接口、模型、领域/业务/代码架构、数据流与测试），并评估设计模式、领域拆分、性能、安全、异常处理与改进空间。在任务拆解与实现前使用。"
---

# 方案评审

- 宣告："使用 vibe-design-review 审查方案。"
- 要求存在 `requirements/<feature>/spec.md` 与 `requirements/<feature>/design.md`。
- 基于 `skills/_templates/review.md` 创建或更新 `requirements/<feature>/review.md`。
- 验证 design 是否包含：接口设计、数据模型、领域模型、业务架构、代码架构、代码目录结构、数据流、测试用例（接口/集成/E2E）。
- 如涉及 LLM/图像模型，验证提示词模板、变量占位符与存放路径是否完整。
- 执行清单并记录差距与需整改项。
- 给出评审结论：设计模式是否合理、领域拆分是否清晰、可改进点、性能问题、安全漏洞、异常处理方案是否充分。
- 如存在阻塞问题，停止并请求更新设计。
- 在评审文档中获取签字确认。
- 将 `requirements/<feature>/status.md` 阶段更新为 `review`。
