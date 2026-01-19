# VibeKit - 智能项目架构分析工具

VibeKit 是一个强大的项目架构分析工具，专门用于检测代码质量问题、循环依赖和架构违规。提供智能化的依赖分析和可视化报告。

## 🎯 核心功能

### 智能分析引擎
- **依赖图构建**：自动构建模块级依赖关系图
- **循环依赖检测**：使用 Tarjan 算法识别所有循环引用
- **上帝模块检测**：识别被过度依赖的模块
- **架构违规检测**：检查分层架构的合规性

### 可视化报告
- **SVG 依赖图**：直观展示模块依赖关系
- **Markdown 报告**：详细的问题分析和重构建议
- **架构健康评分**：量化项目的架构质量

### 多技术栈支持
- ✅ Python 3.7+（完全支持）
- 🔄 JavaScript/TypeScript（v0.2 规划）
- 🔄 Java（v0.3 规划）
- 🔄 Go（v0.4 规划）

## 🚀 快速开始

### 场景 1：创建完整开发环境

```bash
# 创建包含 VibeKit 的开发环境
python skills/init_team/create.py --target ~/my-dev-env

cd ~/my-dev-env
# 现在你有了 project_team/ 目录，包含完整的 VibeKit 工具集
```

### 场景 2：初始化新项目（推荐）

```bash
cd ~/my-dev-env

# 创建新项目（Agent 会自动调用）
python project_team/skills/init_new_project.py my-awesome-project

cd my-awesome-project
# 项目结构已完整创建，包含 src/, tests/, docs/ 等
```

### 场景 3：分析存量项目

```bash
# 分析现有项目（Agent 会询问后调用）
python project_team/skills/init_existing_project.py /path/to/existing/project

# 查看生成的架构梳理报告
cat /path/to/existing/project/PROJECT_ARCHITECTURE_ANALYSIS.md
```

### 场景 4：手动深度分析

```bash
# 手动运行 VibeKit 深度分析
cd skills/init_team/template/skills
python analyze_existing_project.py /path/to/your/project

# 查看报告
cat /path/to/your/project/.vibekit/analysis_report.md
open /path/to/your/project/.vibekit/dependency_graph.svg
```

### 快速验证功能

```bash
# 创建测试项目
python create_test_project.py ./test_project

# 运行分析
./test_analyze.sh

# 查看结果
open test_project/.vibekit/dependency_graph.svg
```

## 📊 版本规划

### v0.1 - 核心功能（已完成）
- ✅ 项目扫描和依赖图构建
- ✅ 循环依赖检测（Tarjan 算法）
- ✅ 上帝模块检测
- ✅ SVG 可视化
- ✅ Markdown 报告生成
- ✅ 测试工具集

### v0.2 - 架构验证（开发中）
- 🔄 分层架构违规检测
- 🔄 跨层调用检测
- 🔄 反向依赖检测
- 🔄 配置文件支持（.vibekit.yaml）
- 🔄 自定义架构规则

### v0.3 - 复杂度分析（规划中）
- 🔄 圈复杂度分析
- 🔄 认知复杂度分析
- 🔄 代码质量评分
- 🔄 热点代码识别

### v1.0 - 企业级功能（规划中）
- 🔄 多语言支持
- 🔄 CI/CD 集成
- 🔄 趋势分析
- 🔄 团队协作功能

## 🏗️ 架构设计

### 核心组件

```
VibeKit/
├── analyze_existing_project.py    # 主分析引擎
├── architecture_validator.py      # 架构验证器
├── complexity_analyzer.py         # 复杂度分析器
├── create_test_project.py         # 测试项目生成器
└── test_analyze.sh                # 一键测试脚本
```

### 分析流程

1. **项目扫描** → 识别技术栈和模块结构
2. **依赖分析** → 构建模块级依赖图
3. **问题检测** → 应用算法检测架构问题
4. **报告生成** → 生成可视化和文本报告

### 算法基础

- **Tarjan 强连通分量**：O(V+E) 循环依赖检测
- **图论算法**：依赖路径分析
- **分层架构理论**：架构违规检测
- **复杂度度量**：代码质量评估

## 📈 应用场景

### 日常开发
- **代码 Review**：提交前检查架构影响
- **重构规划**：识别需要重构的模块
- **技术债务管理**：持续监控架构健康

### 团队协作
- **架构规范**：统一团队的架构标准
- **知识传递**：可视化帮助理解项目结构
- **质量保证**：自动化架构合规检查

### 管理决策
- **技术评估**：评估项目的技术状况
- **资源规划**：基于复杂度评估开发成本
- **风险控制**：识别潜在的架构风险

## 📚 详细文档

- [V01_DELIVERY.md](V01_DELIVERY.md) - v0.1 完整交付文档
- [ANALYZE_README.md](template/skills/ANALYZE_README.md) - 详细使用指南
- [QUICKSTART.md](template/skills/QUICKSTART.md) - 5 分钟快速上手

## 🤝 贡献指南

### 开发环境

```bash
# 安装依赖
pip install graphviz

# 运行测试
cd template/skills
./test_analyze.sh

# 添加新功能
# 1. 创建功能分支
# 2. 编写测试用例
# 3. 实现功能
# 4. 更新文档
```

### 提交规范

- `feat:` 新功能
- `fix:` 问题修复
- `docs:` 文档更新
- `test:` 测试相关
- `refactor:` 代码重构

## 📞 支持与反馈

**问题反馈**：
- 提供项目类型和规模
- 附上错误信息和复现步骤
- 建议期望的解决方案

**功能建议**：
- 描述使用场景和需求
- 说明预期的功能和效果
- 提供相关的最佳实践参考

---

*VibeKit - 让代码架构更清晰，让开发更高效*

*基于 session_012 战略设计，服务于 AI Agent 主线的简历增值工具*
