---
name: init-team
description: >
  VibeKit项目架构分析工具：当用户需要创建开发环境、初始化项目、
  分析代码架构、检测循环依赖、评估代码质量时触发。
---

# VibeKit - Project Architecture Analyzer

## 触发场景

当以下情况发生时自动触发：
- 用户要求创建新的开发环境
- 用户要求初始化新项目
- 用户要求分析现有项目的架构
- 用户提到"循环依赖"、"上帝模块"、"架构违规"
- 用户要求代码质量评估或重构建议

## 核心能力

### 1. 开发环境创建
创建包含完整工具链的项目环境：
- VibeKit分析工具
- 项目模板和脚本
- 文档和最佳实践

### 2. 智能架构分析
- **依赖图构建**：自动生成模块依赖关系图
- **循环依赖检测**：使用Tarjan算法识别循环引用
- **上帝模块检测**：识别过度耦合的模块
- **架构违规检测**：检查分层架构合规性
- **复杂度分析**：圈复杂度和认知复杂度

### 3. 可视化报告
- SVG依赖关系图
- Markdown详细报告
- 架构健康评分
- 重构建议

### 4. 多技术栈支持
- ✅ Python 3.7+（完全支持）
- 🔄 JavaScript/TypeScript（规划中）
- 🔄 Java、Go（规划中）

## 工作流程

1. **创建环境**：python skills/init_team/create.py --target <path>
2. **初始化项目**：python project_team/skills/init_new_project.py <name>
3. **分析项目**：python project_team/skills/analyze_existing_project.py <path>
4. **查看报告**：在报告目录查看生成的SVG和Markdown

## 详细文档

- 使用指南：`skills/init_team/README.md`
- 架构文档：`skills/init_team/template/docs/ARCHITECTURE.md`
- 技能文档：`skills/init_team/template/docs/SKILLS.md`

## 约束

- 主要支持Python项目（其他语言规划中）
- 生成的环境位置：用户指定的target目录
- 分析报告默认输出到：`analysis_reports/`
