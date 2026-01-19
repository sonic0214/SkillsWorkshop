---
name: vibe-acceptance-verification
description: "对照 spec 与测试进行验收验证。在所有任务完成后、宣布完成前使用。"
---

# 验收验证

## 核心流程

- 宣告："使用 vibe-acceptance-verification 进行验收。"
- 读取 `requirements/<feature>/spec.md` 与 `requirements/<feature>/status.md`。
- 将验收标准转为清单并逐条验证（验收标准在 accept 阶段完成，冒烟用例只是最低自动化门槛）。
- 检查是否存在冒烟 case（至少 1 条自动化验收检查）；若缺失则停止验收并回到任务补齐。
- 若存在外部依赖（API/SDK/服务），必须执行至少 1 个真实验收案例：端到端完整流程 + 真实调用（非 mock/伪造）。
- 真实验收案例需记录：输入样例、命令/脚本、产物路径、日志路径与运行结果（写入 `requirements/<feature>/status.md`）。
- 运行相关测试并记录结果。
- 任一项失败则重新打开任务并停止验收。
- 将 `requirements/<feature>/status.md` 阶段更新为 `accept`。
- 宣称成功前必须遵循本文内嵌的完成前验证规则。

## 内嵌规则：完成前验证

- 铁律：没有新鲜验证证据，不能宣称完成。
- Gate Function：识别验证命令 → 运行 → 读取输出与退出码 → 验证结果 → 再宣称。
- 验证失败时：进入系统化排障，修复后重跑同一命令。
- 红旗：使用“应该/大概/看起来”，或未验证就表达完成/满意。
