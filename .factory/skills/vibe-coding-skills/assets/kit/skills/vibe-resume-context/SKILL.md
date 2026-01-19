---
name: vibe-resume-context
description: "在没有聊天上下文时恢复项目状态。用于重启需求或接手现有工作区。"
---

# 恢复上下文

- 宣告："使用 vibe-resume-context 恢复上下文。"
- 读取 `context/facts.md`、`context/architecture.md`、`context/decisions.md`。
- 读取 `requirements/<feature>/status.md` 与 `requirements/<feature>/changes.md`（如存在）。
- 识别当前阶段、未完成任务、阻塞与下一步。
- 汇总当前状态并询问要继续哪个任务。
