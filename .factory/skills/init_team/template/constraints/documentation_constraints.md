# 文档约束规范

## 概述

本文档定义了 project-team-system v3.1 中强制性的文档沉淀约束。**这些约束不可违反，所有开发活动必须遵守**。

## 核心约束原则

### 1. 文档优先原则
- **无文档，不开发**：任何功能开发前必须先完成相关文档
- **文档驱动开发**：代码实现必须严格对应文档设计
- **实时同步**：代码变更必须同步更新相关文档

### 2. 阶段门禁原则
- **顺序不可逆**：必须按 Phase 1→2→3→4→5 顺序执行
- **阶段完整**：当前阶段所有文档必须完成才能进入下一阶段
- **质量门禁**：每个阶段都有明确的质量标准，不达标不能进入下一阶段

### 3. 可追溯性原则
- **决策记录**：所有重要技术决策必须记录在相应文档中
- **变更追踪**：文档变更必须有变更记录
- **版本管理**：每个阶段完成必须保存 checkpoint

## Phase 约束详解

### Phase 1: Specify 约束

#### 强制文档
1. **`docs/01_specify/prd.md`** - 产品需求文档
   - 必须包含：项目背景、目标用户、功能清单、优先级、验收标准
   - 不得有模糊描述，所有功能必须有明确验收标准
   - 优先级必须明确（高/中/低）

2. **`docs/01_specify/user_stories.md`** - 用户故事清单
   - 必须使用标准格式：作为...我希望...以便...
   - 每个故事必须包含验收标准（Given/When/Then）
   - 必须按 Epic 组织，故事点必须估算

3. **`docs/01_specify/api_spec.md`** - API 规范（如需要）
   - 必须包含完整的请求/响应格式
   - 必须定义错误码和错误处理
   - 必须包含认证和授权说明

#### 质量标准
- [ ] PRD 覆盖所有需求点，无遗漏
- [ ] 用户故事具有可测试性
- [ ] API 规范完整无歧义
- [ ] 所有文档通过 stakeholder 评审

#### 门禁规则
- **阻止进入 Phase 2**：PRD 未完成或用户故事不完整
- **必须完成**：保存 `specify_complete` checkpoint

### Phase 2: Plan 约束

#### 强制文档
1. **`docs/02_plan/architecture.md`** - 技术架构设计
   - 必须包含架构图和技术栈选择
   - 必须说明技术选择的理由
   - 必须包含数据流和组件交互

2. **`docs/02_plan/module_design.md`** - 模块设计方案
   - 必须明确模块职责和边界
   - 必须定义模块间接口
   - 必须包含依赖关系图

3. **`docs/02_plan/database_design.md`** - 数据库设计
   - 必须包含完整的表结构
   - 必须定义索引策略
   - 必须说明数据关系

#### 强制工具使用
- **必须执行**：`python ../project_team/skills/build_main_index.py .`
- **验证**：`.context/main_index.json` 必须生成
- **索引质量**：必须包含所有模块和接口定义

#### 质量标准
- [ ] 架构设计满足所有 PRD 需求
- [ ] 模块划分清晰，职责单一
- [ ] 接口设计完整，无歧义
- [ ] 数据库设计满足性能要求

#### 门禁规则
- **阻止进入 Phase 3**：main_index.json 不存在或架构设计不完整
- **必须完成**：保存 `plan_complete` checkpoint

### Phase 3: Implement 约束

#### 强制文档
1. **`docs/03_implement/task_breakdown.md`** - 任务分解清单
   - 必须将所有功能分解到可执行任务
   - 每个任务必须有估算和依赖
   - 必须明确负责人和截止时间

2. **`docs/03_implement/progress_track.md`** - 进度跟踪
   - 必须实时更新任务状态
   - 必须记录阻塞和风险
   - 必须跟踪里程碑进度

#### 强制开发流程
1. **TDD 强制流程**：
   ```
   红色阶段：编写测试，必须失败
   绿色阶段：最小实现，使测试通过
   重构阶段：优化代码，保持测试通过
   ```

2. **模块开发强制流程**：
   ```
   构建模块索引：python ../project_team/skills/build_module_index.py . <module>
   执行 TDD 循环：python ../project_team/skills/run_tdd_cycle.py . <task>
   更新进度：docs/03_implement/progress_track.md
   ```

#### 质量标准
- [ ] 代码覆盖率 > 80%
- [ ] 所有测试通过
- [ ] 代码符合编码规范
- [ ] 无已知严重 bug

#### 门禁规则
- **阻止进入 Phase 4**：代码覆盖率不达标或存在失败测试
- **必须完成**：保存 `implement_complete` checkpoint

### Phase 4: Test 约束

#### 强制文档
1. **`docs/04_test/test_plan.md`** - 测试计划
   - 必须包含测试策略和范围
   - 必须定义测试环境和数据
   - 必须包含时间安排和资源分配

2. **`docs/04_test/test_cases.md`** - 测试用例
   - 必须覆盖所有功能需求
   - 必须包含边界条件和异常情况
   - 必须包含预期结果

3. **`docs/04_test/quality_report.md`** - 质量报告
   - 必须记录所有发现的缺陷
   - 必须包含测试覆盖率报告
   - 必须评估发布风险

#### 强制测试流程
1. **完整测试套件**：
   ```bash
   pytest tests/ --cov --cov-report=term-missing
   ```

2. **质量检查**：
   - 代码覆盖率必须 > 80%
   - 所有测试必须 100% 通过
   - 性能测试必须满足要求

#### 质量标准
- [ ] 测试覆盖率 > 80%
- [ ] 所有测试用例通过
- [ ] 无严重缺陷
- [ ] 性能指标达标

#### 门禁规则
- **阻止进入 Phase 5**：存在失败测试或严重缺陷
- **必须完成**：保存 `test_complete` checkpoint

### Phase 5: Release 约束

#### 强制文档
1. **`docs/05_release/release_notes.md`** - 发布说明
   - 必须包含新功能列表
   - 必须包含已知问题和限制
   - 必须包含升级指南

2. **`docs/05_release/deployment.md`** - 部署文档
   - 必须包含详细的部署步骤
   - 必须包含环境要求和配置
   - 必须包含回滚方案

#### 强制发布流程
1. **代码审查**：所有代码必须经过审查
2. **文档审查**：所有文档必须经过审查
3. **最终测试**：在类生产环境验证
4. **保存最终状态**：`python ../project_team/skills/checkpoint.py save . release`

#### 质量标准
- [ ] 所有文档完整准确
- [ ] 部署流程经过验证
- [ ] 回滚方案可行
- [ ] 发布风险可接受

## 违规处理（v4.0 增强）

### 约束违规级别

1. **严重违规**（P0 - 立即阻止）：
   - 跳过 Phase 直接开发
   - 伪造文档或测试
   - 忽略质量门禁
   - 绕过 Phase Gate 验证
   - 修改 `.project_state.json` 绕过检查

2. **一般违规**（P1 - 阻止进入下一阶段）：
   - 文档不完整
   - 未及时更新文档
   - 未使用强制工具
   - 代码覆盖率不达标
   - 测试通过率不达标

3. **轻微违规**（P2 - 警告但不阻止）：
   - 文档格式不规范
   - 小遗漏不影响质量
   - 注释不完整

---

### 违反约束的自动检测和处理流程

#### 1. Phase Gate 强制验证机制（v4.0 新增）

**验证时机**：
- Project Agent 请求 Phase 切换时
- Supervisor 必须运行 Phase Gate Validator

**验证命令**：
```bash
python project_team/skills/validate_phase_gate.py . <from_phase> <to_phase>
```

**验证内容**：
- ✅ 必需文档是否存在
- ✅ 文档字数是否达标
- ✅ 自定义检查（用户故事数量、架构图、测试覆盖率等）
- ✅ Git 提交状态

**验证结果**：
```json
{
  "passed": true/false,
  "from_phase": "specify",
  "to_phase": "plan",
  "checks": {
    "required_docs": [...],
    "word_count": {...},
    "custom_checks": [...]
  },
  "errors": [...],
  "warnings": [...]
}
```

---

#### 2. 违反约束的处理流程

**场景 1：文档不完整**

```
[Project Agent]
Supervisor，我已完成 Phase 1 的所有任务。
请验证 Phase Gate 并批准切换到 Phase 2。

[Supervisor 运行验证]
python validate_phase_gate.py . specify plan

[验证结果：失败]
{
  "passed": false,
  "errors": [
    "缺少必需文档: docs/01_specify/user_stories.md",
    "文档字数不足: 800 (要求 >= 1000)"
  ]
}

[Supervisor 响应]
❌ Phase Gate 验证失败：
- 缺少必需文档: docs/01_specify/user_stories.md
- 文档字数不足: 800 (要求 >= 1000)

🛑 拒绝切换到 Phase 2。

请完成以下任务：
1. 创建 user_stories.md（至少 10 个用户故事）
2. 补充 prd.md 内容（至少 200 字）

完成后重新请求 Phase Gate 验证。

[记录违规到 .project_state.json]
{
  "violations": [
    {
      "phase": "specify",
      "type": "documentation_incomplete",
      "severity": "P1",
      "timestamp": "2025-12-06T10:30:00Z",
      "details": "缺少 user_stories.md，prd.md 字数不足"
    }
  ]
}
```

---

**场景 2：代码覆盖率不达标**

```
[Project Agent]
Supervisor，我已完成 Phase 3 的所有任务。
请验证 Phase Gate 并批准切换到 Phase 4。

关键指标：
- 代码覆盖率: 75%

[Supervisor 运行验证]
python validate_phase_gate.py . implement test

[验证结果：失败]
{
  "passed": false,
  "errors": [
    "代码覆盖率不达标: 75% (要求 >= 80%)"
  ]
}

[Supervisor 响应]
❌ Phase Gate 验证失败：
- 代码覆盖率不达标: 75% (要求 >= 80%)

🛑 拒绝切换到 Phase 4。

请完成以下任务：
1. 补充单元测试，提升覆盖率到 >= 80%
2. 重新运行测试：pytest tests/ --cov
3. 更新 progress_track.md 记录覆盖率

完成后重新请求 Phase Gate 验证。

[记录违规]
{
  "violations": [
    {
      "phase": "implement",
      "type": "test_coverage_insufficient",
      "severity": "P1",
      "timestamp": "2025-12-06T14:00:00Z",
      "details": "代码覆盖率 75%，要求 >= 80%"
    }
  ]
}
```

---

**场景 3：测试通过率不达标**

```
[Project Agent]
Supervisor，我已完成 Phase 4 的所有任务。
请验证 Phase Gate 并批准切换到 Phase 5。

关键指标：
- 测试通过率: 90%
- P0 Bug: 1

[Supervisor 运行验证]
python validate_phase_gate.py . test release

[验证结果：失败]
{
  "passed": false,
  "errors": [
    "测试通过率不达标: 90% (要求 >= 95%)",
    "P0 Bug 数量: 1 (要求 <= 0)"
  ]
}

[Supervisor 响应]
❌ Phase Gate 验证失败：
- 测试通过率不达标: 90% (要求 >= 95%)
- P0 Bug 数量: 1 (要求 <= 0)

🛑 拒绝切换到 Phase 5。

请完成以下任务：
1. 修复 P0 Bug（参考 quality_report.md）
2. 修复失败的测试用例
3. 重新运行完整测试：pytest tests/ --cov
4. 更新 quality_report.md

完成后重新请求 Phase Gate 验证。

[记录违规]
{
  "violations": [
    {
      "phase": "test",
      "type": "quality_gate_failed",
      "severity": "P1",
      "timestamp": "2025-12-06T16:00:00Z",
      "details": "通过率 90%，P0 Bug 1 个"
    }
  ]
}
```

---

#### 3. 严重违规的强制处理

**场景：绕过 Phase Gate 直接切换**

```
[Project Agent 未经验证直接声称]
"我已经切换到 Phase 2，开始架构设计。"

[Supervisor 检查 .project_state.json]
{
  "current_phase": "specify",
  "phase_gate_validations": []  // 没有验证记录！
}

[Supervisor 响应]
🚨 严重违规：检测到未经 Phase Gate 验证直接切换 Phase。

🛑 立即停止当前工作。

❌ 违规记录：
- 类型: 绕过 Phase Gate 验证
- 严重程度: P0（严重违规）
- 时间: 2025-12-06T11:00:00Z

📋 强制回退流程：
1. 回退到 Phase 1（Specify）
2. 补全 Phase 1 的所有文档
3. 运行 Phase Gate 验证：python validate_phase_gate.py . specify plan
4. 验证通过后，Supervisor 批准切换到 Phase 2

⚠️  警告：严重违规将被记录到项目日志。

[记录违规]
{
  "violations": [
    {
      "phase": "specify",
      "type": "bypass_phase_gate",
      "severity": "P0",
      "timestamp": "2025-12-06T11:00:00Z",
      "details": "未经验证直接切换到 Plan 阶段",
      "action_taken": "强制回退到 Phase 1"
    }
  ]
}
```

---

#### 4. 违规恢复流程

**Step 1: 识别违规**
- Supervisor 运行 Phase Gate Validator
- 验证失败 → 识别违规类型和严重程度

**Step 2: 记录违规**
- 记录到 `.project_state.json` → `violations` 数组
- 包含：phase, type, severity, timestamp, details

**Step 3: 阻止进行**
- 🛑 拒绝 Phase 切换请求
- 📝 告知 Project Agent 缺失的内容
- 📋 提供修复清单

**Step 4: 修复验证**
- Project Agent 补全缺失的文档/指标
- 重新请求 Phase Gate 验证
- 验证通过 → 批准切换

**Step 5: 清除违规记录**
- 验证通过后，Supervisor 将违规标记为 "resolved"
- 记录修复时间和修复方式

---

### 处理措施总结

#### P0 - 严重违规（立即阻止）

**处理流程**：
1. 🛑 立即停止当前工作
2. 📝 记录违规到 `.project_state.json`
3. ↩️  强制回退到违规前的状态
4. 🔄 重新执行完整的 Phase 流程
5. ✅ Phase Gate 验证通过后才能继续

**示例**：
- 绕过 Phase Gate 直接切换
- 伪造文档或测试
- 修改 `.project_state.json` 绕过检查

---

#### P1 - 一般违规（阻止进入下一阶段）

**处理流程**：
1. ⏸️  暂停 Phase 切换
2. 📝 记录违规到 `.project_state.json`
3. 📋 提供修复清单
4. 🔧 Project Agent 补全缺失内容
5. ✅ 重新验证通过后才能切换

**示例**：
- 文档不完整
- 代码覆盖率不达标
- 测试通过率不达标

---

#### P2 - 轻微违规（警告但不阻止）

**处理流程**：
1. ⚠️  记录警告到 `.project_state.json`
2. 📋 提供改进建议
3. ✅ 允许继续工作，但需在下一阶段前修复

**示例**：
- 文档格式不规范
- 注释不完整
- 命名不一致（不影响功能）

---

### 违规记录格式

```json
{
  "violations": [
    {
      "id": "violation_001",
      "phase": "specify",
      "type": "documentation_incomplete",
      "severity": "P1",
      "timestamp": "2025-12-06T10:30:00Z",
      "details": "缺少 user_stories.md，prd.md 字数不足",
      "status": "pending",
      "resolution": null
    },
    {
      "id": "violation_002",
      "phase": "implement",
      "type": "test_coverage_insufficient",
      "severity": "P1",
      "timestamp": "2025-12-06T14:00:00Z",
      "details": "代码覆盖率 75%，要求 >= 80%",
      "status": "resolved",
      "resolution": {
        "resolved_at": "2025-12-06T15:00:00Z",
        "action": "补充单元测试，覆盖率提升至 85%"
      }
    }
  ]
}

## 工具支持

### 强制使用的技能脚本
- `build_main_index.py` - 构建主索引（Phase 2）
- `build_module_index.py` - 构建模块索引（Phase 3）
- `run_tdd_cycle.py` - 执行 TDD 开发（Phase 3）
- `checkpoint.py` - 保存阶段状态（所有 Phase）
- `validate_phase_gate.py` - Phase Gate 验证（v4.0 新增）
- `recovery.py` - 断点恢复（v4.0 新增）

### 自动化检查（v4.0 增强）
- **文档完整性检查**：验证必需文档是否存在
- **质量标准验证**：验证代码覆盖率、测试通过率
- **阶段门禁验证**：Phase Gate Validator 强制验证
- **违规自动记录**：违规自动记录到 `.project_state.json`
- **断点恢复验证**：新 Agent 启动时验证状态完整性

---

**重要提醒**：这些约束是项目成功的关键保障，任何情况下都不得违反或绕过。

---

**版本历史**：
- v3.1 (2024-12-05): 初始版本 - 定义 5 Phase 文档约束
- v4.0 (2024-12-06): 增强版本 - 新增 Phase Gate 强制验证机制和违规处理流程