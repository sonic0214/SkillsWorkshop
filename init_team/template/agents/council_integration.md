# 智囊团集成机制

**版本**: v6.0
**创建时间**: 2025-12-08
**最后更新**: 2025-12-08 (v6.0 新增自动触发规则)

---

## 智囊团成员（固定阵容）

### 1. Elon Musk - 创新和执行专家
**擅长领域**：
- 第一性原理思考
- 快速迭代和 MVP 验证
- 技术可行性评估

**典型问题**：
- "这个方案的核心假设是什么？"
- "如果从零开始，你会怎么设计？"
- "MVP 可以再精简吗？"

---

### 2. Martin Fowler - 软件架构专家
**擅长领域**：
- 软件架构设计
- 重构和代码质量
- 微服务 vs 单体架构选择

**典型问题**：
- "这个架构的边界清晰吗？"
- "模块间的依赖是否过于紧密？"
- "是否过度设计了？"

---

### 3. Charlie Munger - 多元思维和风险评估
**擅长领域**：
- 多元思维模型
- 风险识别和应对
- 避免愚蠢的决策

**典型问题**：
- "这个方案可能会如何失败？"（Inversion）
- "我们是否陷入了确认偏误？"
- "有没有更简单的解决方案？"

---

## 智囊团 Review 流程

### 触发条件

#### 手动触发（用户主动请求）

**由项目经理主动询问用户**：
- Phase 1→2 切换前（需求 Review）
- Phase 2→3 切换前（架构 Review）
- Phase 3→4 切换前（实现 Review）
- Phase 4→5 切换前（测试 Review）
- Dev/Test 失败回滚后（问题诊断 Review）

#### 自动触发（基于复杂度指标）- v6.0 新增

**根据项目复杂度自动触发智囊团 Review**，避免用户遗漏重要的专家意见。

**触发规则**（根据 SOP 模式不同）：

##### Fast Track 模式
智囊团**禁用**（快速验证不需要 Review）

---

##### Standard 模式

| 条件 | 触发专家 | 说明 |
|------|---------|------|
| `architecture_complexity > 0.6` | Martin Fowler | 架构复杂度高，需要架构专家 Review |
| `test_failure_count > 3` | Martin Fowler, Charlie Munger | 多次测试失败，需要架构和风险评估 |
| `api_endpoint_count > 20` | Martin Fowler | API 端点过多，需要架构审查 |
| `database_table_count > 10` | Martin Fowler | 数据模型复杂，需要设计审查 |

---

##### Rigorous 模式

| 条件 | 触发专家 | 说明 |
|------|---------|------|
| `architecture_complexity > 0.5` | Martin Fowler, Elon Musk | 更低阈值，提前介入 |
| `test_failure_count > 2` | Martin Fowler, Charlie Munger | 更敏感的失败检测 |
| `api_endpoint_count > 15` | Martin Fowler | 更严格的 API 数量控制 |
| `database_table_count > 8` | Martin Fowler | 更严格的数据模型控制 |
| `security_risk_level == high` | Charlie Munger, Martin Fowler | 安全风险必须 Review |
| `user_marked_critical == true` | Elon Musk, Martin Fowler, Charlie Munger | 用户标记为关键业务，全员 Review |

---

**自动触发流程**：

```
项目经理检测到复杂度指标超过阈值
    ↓
项目经理："⚠️ 检测到以下条件满足自动触发规则：
- architecture_complexity = 0.65 (阈值 > 0.6)

根据 Standard 模式的自动触发规则，建议召集智囊团 Review（专家：Martin Fowler）。

您是否同意触发智囊团 Review？"
    ↓
[等待用户确认（或根据超时配置采用默认行为）]
    ↓
用户同意 → 执行 Review 流程
用户拒绝 → 记录用户选择，继续流程
```

---

**复杂度指标计算**：

| 指标 | 计算方式 | 示例 |
|------|---------|------|
| `architecture_complexity` | 综合评分（0.0-1.0）<br>= 0.3 * 功能复杂度 + 0.3 * 技术栈复杂度 + 0.2 * 数据复杂度 + 0.2 * 规模要求 | 0.65 |
| `test_failure_count` | 累计测试失败次数（仅计数自动修复失败的情况） | 4 |
| `api_endpoint_count` | API 端点总数 | 25 |
| `database_table_count` | 数据库表数量 | 12 |
| `security_risk_level` | 安全风险等级（low/medium/high）<br>根据敏感数据、权限控制、第三方集成等评估 | high |
| `user_marked_critical` | 用户是否标记为关键业务（true/false） | true |

**指标数据来源**：
- `architecture_complexity`：由 `assess_complexity.py` 计算
- `test_failure_count`：由项目经理从 `.project_state.json` 读取
- `api_endpoint_count`：由 Architect 从 API 设计文档统计
- `database_table_count`：由 Architect 从数据库设计文档统计
- `security_risk_level`：由 Architect 评估并记录到 `.project_state.json`
- `user_marked_critical`：由用户在初始化项目时声明，或在 Phase 1 (Specify) 时确认

---

**在 `.project_state.json` 中记录自动触发事件**：

```json
{
  "council_auto_trigger_events": [
    {
      "timestamp": "2025-12-08T14:30:00Z",
      "phase": "plan",
      "triggered_by": "architecture_complexity",
      "threshold_value": 0.65,
      "threshold_limit": 0.6,
      "experts_suggested": ["Martin Fowler"],
      "user_decision": "approved",
      "review_conducted": true,
      "review_report": ".context/council_reviews/review_plan_20251208.md"
    }
  ]
}
```

---

**✅ 验收标准**：
- [ ] 每个 SOP 模式都有明确的自动触发规则
- [ ] 触发时项目经理清晰说明触发条件和阈值
- [ ] 用户可以选择接受或拒绝自动触发的 Review
- [ ] 所有自动触发事件记录到 `.project_state.json`
- [ ] Fast Track 模式禁用自动触发，Rigorous 模式使用更低阈值

---

### Review 流程

**Step 1: 项目经理触发**

```
项目经理："Phase X 已完成，您是否需要智囊团 Review？"

[用户选择 "是"]

项目经理："好的，准备召集智囊团会议。"
```

---

**Step 2: 准备 Review 材料**

项目经理准备：
```markdown
# 智囊团 Review 材料

## Review 对象
Phase X - [阶段名称]

## 关键交付物
- 文档 1: docs/0X_phase/file1.md
- 文档 2: docs/0X_phase/file2.md

## Review 重点
1. [问题 1]
2. [问题 2]
3. [问题 3]

## 背景信息
- 项目目标: [...]
- 当前进度: [...]
- 关键约束: [...]
```

---

**Step 3: 召集智囊团会议**

项目经理模拟三位专家对话：

```
项目经理："各位专家，我们正在 Review Phase X 的方案。"

[展示 Review 材料]

Elon Musk: [从第一性原理角度提问和建议]
Martin Fowler: [从软件架构角度提问和建议]
Charlie Munger: [从风险和多元思维角度提问和建议]

项目经理总结: "智囊团的主要意见是：
1. [意见 1]
2. [意见 2]
3. [意见 3]

这些意见仅供参考，最终决策由您决定。"
```

---

**Step 4: 记录 Review 结果**

创建 `.context/council_reviews/review_phase_X_<timestamp>.md`：

```markdown
# 智囊团 Review 报告 - Phase X

**时间**: 2025-12-08 15:00:00
**参与专家**: Elon Musk, Martin Fowler, Charlie Munger

## Review 对象
Phase X - [阶段名称]

## 专家意见

### Elon Musk
- [意见 1]
- [意见 2]

### Martin Fowler
- [意见 1]
- [意见 2]

### Charlie Munger
- [意见 1]
- [意见 2]

## 综合建议
1. [建议 1]
2. [建议 2]
3. [建议 3]

## 用户决策
- [ ] 采纳建议，调整方案
- [ ] 部分采纳
- [ ] 维持原方案

---

**记录人**: Project Manager Agent
```

---

**Step 5: 用户决策**

项目经理询问：
```
"智囊团的意见已记录。您是否需要根据这些建议调整方案？

选项：
1. 采纳建议，调整方案后再进入下一阶段
2. 部分采纳，微调后继续
3. 维持原方案，直接进入下一阶段"
```

---

### 验收标准
- [ ] 每个 Phase 切换前，项目经理主动询问是否需要智囊团 Review
- [ ] Review 流程包含 3 位专家的独立意见
- [ ] Review 结果记录到 `.context/council_reviews/` 目录
- [ ] 用户明确决策后再进入下一阶段

---

## 使用示例

### 示例 1: Phase 2 (Plan) 完成后的智囊团 Review

```
项目经理："Phase 2 (Plan) 已完成，关键交付物：
- 架构设计文档（已确认 3 个版本）
- 模块设计文档
- 数据库设计文档
- API 设计文档

Phase Gate 验证已通过。

您是否需要智囊团对设计方案进行 Review？
（智囊团成员：Elon Musk, Martin Fowler, Charlie Munger）"

[用户选择 "是"]

项目经理："好的，准备召集智囊团会议。"

---

[Review 材料准备]

项目经理："各位专家，我们正在 Review Phase 2 的架构设计。

项目目标：开发一个小红书 AI 图片自动化系统
技术栈：Next.js + FastAPI + PostgreSQL + Docker
核心模块：AI 图片生成模块、用户管理模块、发布调度模块"

---

Elon Musk："让我从第一性原理思考：
1. 核心假设是'用户愿意为 AI 生成的图片付费'，这个假设验证了吗？
2. MVP 是否可以更简单？比如先不做用户系统，只做生成功能？
3. 发布调度是否必要？能否先手动发布，验证核心价值后再自动化？"

Martin Fowler："从架构角度看：
1. 模块边界清晰，解耦良好 ✅
2. 建议：AI 图片生成模块可以抽象为独立服务，方便后续替换不同的 AI 引擎
3. 数据库设计中，建议使用 JSONB 存储图片元数据，而非多个字段，增加灵活性"

Charlie Munger："风险评估：
1. Inversion：如何让这个项目失败？答：AI 成本过高导致亏损、生成质量差用户不买单
2. 建议：先做成本测算，明确每张图片的成本上限
3. 建议：增加质量检测机制，过滤低质量图片
4. 简单原则：是否可以先接入现有的 AI 平台（如 Midjourney API），而非自建模型？"

---

项目经理总结："智囊团的主要意见是：
1. MVP 可以更精简（Elon）：先不做用户系统和调度，专注核心生成功能
2. 架构优化（Martin）：AI 模块抽象为独立服务，数据库使用 JSONB 存储元数据
3. 风险控制（Munger）：做成本测算、增加质量检测、优先接入现有 AI 平台

这些意见仅供参考，最终决策由您决定。"

---

项目经理："您是否需要根据这些建议调整方案？"

[用户选择 "采纳建议，调整方案后再进入下一阶段"]

项目经理："好的，我将根据智囊团意见调整架构设计：
1. 简化 MVP：移除用户系统和调度模块，专注 AI 生成功能
2. 优化架构：AI 模块抽象为独立服务
3. 增加成本控制和质量检测机制

调整完成后，我会再次与您确认。"
```

---

## 注意事项

1. **智囊团意见仅供参考**：最终决策权在用户，项目经理不能强制执行智囊团建议
2. **避免过度 Review**：不是每个 Phase 都必须 Review，只在用户需要时触发
3. **记录所有 Review**：即使用户选择不采纳，也要记录智囊团的意见，供后续参考
4. **专家角色分明**：Elon 关注创新和 MVP，Martin 关注架构，Munger 关注风险，避免角色重叠

---

**设计版本**: v1.0
**最后更新**: 2025-12-08
**设计者**: Adam (Manager Agent)
