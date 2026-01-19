---
name: product-competitor-analysis
description: Systematic product and competitor analysis for AI or other products using GOSPEL + 竞品分析模块, including 叙事式 v4.0 模板输出. Use when the user asks to analyze a product or update prior analyses, or to generate/maintain the competitor knowledge base (81 AI产品研究). Analysis modules include 增长系统、市场机会、战略定位、产品设计、商业模式、洞察提炼、竞品分析.
---

# Product Competitor Analysis

## Usage

- 分析 <产品名> → 分析（默认覆盖：增长系统/市场机会/战略定位/竞品分析/产品设计/商业模式/洞察提炼）
- 分析 <产品名>（模块：增长系统、商业模式、竞品分析） → 仅输出所选模块 + 洞察提炼
- 分析 <产品名>（模板：v1.0/v2.0/v4.0） → 先确定输出模板版本再生成
- 更新 <产品名> 的最新数据 → 增量更新已有分析

## High-level workflow

1. 采集数据（必须先做）：用 `scripts/collect_data.py` 组织公开信息与用户补充数据，写入 `81.93 竞品资料库/`。至少覆盖官网与About、条款/隐私、帮助中心/FAQ、定价/费用、融资/团队、口碑（App Store/Google Play/Product Hunt/G2/媒体评测/社交讨论）、竞品清单、市场规模线索（行业报告/市场规模/增速）。如在采集过程中发现有价值的数据源，先判断是否通用；通用则补充到 `config/analysis_config.yaml` 的 `data_sources`/`search_templates`/`source_url_templates`，非通用则补充到 `source_url_overrides`（按产品名）。
2. 检查知识库中是否已有分析文档与原始资料。
3. 确认分析模块（增长系统/市场机会/战略定位/竞品分析/产品设计/商业模式）与输出模板版本（v1.0/v2.0/v4.0）。用户未指定模板版本时先询问；未指定模块时默认全选；洞察提炼始终包含，并吸收战略设计动作。若选择 v4.0，输出需保持连续叙事与高信息密度，避免“标签式小标题 + 冒号”。
4. 生成分析：用 `scripts/generate_analysis.py` 基于 `config/gospel_framework.yaml`、`config/ai_expert_prompts.yaml` 与模板文件（`templatev1.0.md`/`templatev2.0.md`/`templatev4.0.md`）生成报告框架与输出；按所选模块与模板版本裁剪内容。市场机会模块必须给出 TAM/SAM/SOM 估算；无官方数据时用行业报告+合理假设并标注来源/假设。
5. 战略定位模块使用 `references/战略分析框架.md` 作为结构与判断标准。
6. 更新知识库：用 `scripts/update_knowledge_base.py` 更新分析模块库与模式库（81.94/81.90/81.91/81.92）。

## 叙事与转折要求（v4.0）

- 使用连续叙事与高信息密度表达，不使用“标签式小标题 + 冒号”。
- 所有转折/过渡语必须变体化：同一份报告内不得重复固定短语；跨报告也要避免复用同一组开头句式。优先改写语气、语序、动词。
- 禁用固定开头句式示例：“先把赛道拉开”“回到产品本体”“再看竞争格局”。必须改写为语义等价的变体。
- 必须包含竞品对比段落：至少选 2–4 个直接竞品，按定位、关键路径、增长机制、商业化与风险做对照，给出“为什么赢/为什么输”的判断。

## 版本管理规则

- 同一产品的不同版本报告必须分文件保存，不得覆盖旧文件。
- 默认文件命名：`81.XXX 产品名 产品分析_vX.Y.md`；如需日期或其它后缀，按用户要求调整。

## Core resources

- `config/analysis_config.yaml`：更新规则与质量阈值
- `config/gospel_framework.yaml`：分析维度与模块配置
- `config/ai_expert_prompts.yaml`：专家视角提示词
- `templatev1.0.md`：分析与对比模板（v1.0）
- `templatev2.0.md`：分析与对比模板（v2.0）
- `templatev4.0.md`：叙事式高密度模板（v4.0，连贯引导）

## References (load only when needed)

- `references/workflows.md`：完整工作流与阶段细节
- `references/examples.md`：提示词与输出示例
- `references/战略分析框架.md`：战略定位分析框架
- `references/竞品分析框架.md`：竞品分析模块

## Notes

- 知识库根目录：`80-89 项目·专题/81 AI产品研究`。如路径不同，更新 `scripts/utils.py` 的 `KNOWLEDGE_BASE_ROOT`。
- 主要输出位置：
  - `80-89 项目·专题/81 AI产品研究/81.XX [产品名].md`
  - `80-89 项目·专题/81 AI产品研究/81.93 竞品资料库/`
  - `80-89 项目·专题/81 AI产品研究/81.94 分析模块库/`
