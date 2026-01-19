# analyze_existing_project.py v0.1

分析存量项目的依赖关系，检测架构问题。

## 功能

✅ **v0.1 已实现**：
- 项目结构扫描（识别 Python 模块）
- 模块级依赖图构建
- 循环依赖检测（Tarjan 算法）
- 上帝模块检测（被过多模块依赖）
- 依赖图可视化（SVG）
- Markdown 分析报告生成

🚧 **后续版本计划**：
- v0.2：架构违规检测（跨层调用）
- v0.3：复杂度分析 + 重复代码检测
- v0.4：内聚/耦合指标计算
- v1.0：完整重构建议 + 自动化重构工具

## 安装依赖

```bash
# 核心依赖（必需）
pip install graphviz

# 系统依赖（可视化必需）
# macOS
brew install graphviz

# Ubuntu/Debian
sudo apt-get install graphviz

# Windows
# 下载安装：https://graphviz.org/download/
```

## 使用方法

### 基本用法

```bash
# 分析项目
python skills/analyze_existing_project.py /path/to/your/project

# 输出：
# 🔍 扫描项目...
#    技术栈：Python
#    发现 8 个模块
#
# 🔗 分析依赖关系...
#    发现 23 条依赖关系
#
# 🔄 检测循环依赖...
#    ⚠️  发现 2 处循环依赖！
#
# 👑 检测上帝模块...
#    ⚠️  发现 1 个上帝模块
#
# 📊 生成依赖图...
#    ✅ 依赖图已保存：.vibekit/dependency_graph.svg
#
# 📝 生成分析报告...
#    ✅ 报告已保存：.vibekit/analysis_report.md
#
# ============================================================
#   ✅ 分析完成！
# ============================================================
```

### 输出文件

分析完成后，会在项目目录下生成 `.vibekit/` 文件夹：

```
your-project/
├── .vibekit/
│   ├── analysis_report.md      # 📄 分析报告（主要阅读这个）
│   ├── dependency_graph.svg    # 📊 依赖图可视化
│   └── dependency_data.json    # 🗂️  原始数据（供工具使用）
└── ...
```

### 示例报告

```markdown
# 项目依赖分析报告 v0.1

生成时间：2025-12-08 16:00:00
项目路径：`~/my-project`
技术栈：Python

---

## 📊 总体情况

- **总模块数**：8
- **依赖关系数**：23
- **循环依赖**：2 处 ⚠️
- **上帝模块**：1 个 ⚠️

---

## 🚨 循环依赖 (P0 - 必须修复)

### 1. auth ↔ user ↔ permission

**依赖路径**：
```
auth → user → permission → auth
```

**影响**：
- ❌ 无法独立测试任何一个模块
- ❌ 修改一处可能影响多处
- ❌ 无法独立部署

**建议**：
1. 提取共享类型到独立模块
2. 使用依赖注入，而非直接导入
3. 考虑引入事件驱动模式解耦

---

## ⚠️ 上帝模块 (P1 - 应该优化)

### 1. `utils`

**被依赖次数**：6/8 模块 (依赖率 75%)

**问题**：
- 被过多模块依赖，任何修改都可能影响 6 个模块
- 是系统的脆弱点和瓶颈

**建议**：
1. 拆分为领域特定的子模块
2. 将通用函数移到标准库或第三方库

---

## 💡 重构建议

### Phase 1：消除循环依赖（1 天）
1. **auth ↔ user ↔ permission**（12h）

### Phase 2：拆解上帝模块（2 天）
1. **`utils`**（12h）

**总预估时间**：24 小时（约 3 个工作日）
```

## 支持的项目类型

### ✅ 已支持

- **Python 项目**
  - 自动识别：`requirements.txt`, `setup.py`, `pyproject.toml`
  - 解析：`import` 和 `from...import` 语句
  - 模块发现：包含 `__init__.py` 或 `.py` 文件的目录

### 🚧 计划支持

- **JavaScript/TypeScript**（v0.2）
- **Go**（v0.3）
- **Java**（v0.4）

## 技术原理

### 循环依赖检测

使用 **Tarjan 强连通分量算法**：
- 时间复杂度：O(V + E)
- 空间复杂度：O(V)
- 能找出所有循环依赖

### 上帝模块检测

计算每个模块的**入度**（被多少模块依赖）：
- 阈值：被 > 30% 的模块依赖 = 上帝模块
- 可配置阈值

### 依赖图可视化

使用 **Graphviz**：
- 🔴 红色边：循环依赖
- 🔵 蓝色边：正常依赖
- 🟠 橙色节点：上帝模块

## 常见问题

### Q1: 为什么没发现我的模块？

**可能原因**：
1. 模块不在默认搜索目录（`src/`, `app/`, `lib/`, 根目录）
2. Python 包缺少 `__init__.py`（非 namespace package）
3. 模块名以 `.` 开头（被忽略）

**解决方案**：
- 检查项目结构
- 确保关键目录有 `__init__.py`

### Q2: graphviz 安装失败？

**解决方案**：
```bash
# macOS
brew install graphviz
pip install graphviz

# Ubuntu
sudo apt-get install graphviz
pip install graphviz

# Windows
# 1. 下载安装包：https://graphviz.org/download/
# 2. 添加到 PATH
# 3. pip install graphviz
```

### Q3: 如何忽略某些模块？

当前版本不支持，v0.2 将增加配置文件：

```yaml
# .vibekit.yaml
ignore:
  - tests
  - migrations
  - __pycache__
```

### Q4: 分析很慢怎么办？

**优化建议**：
- 当前版本适合中小项目（< 100 模块）
- 大项目请等待 v0.3（增量分析）

## 开发计划

### v0.2 - 架构违规检测

预计：1-2 周后

功能：
- [ ] 检测跨层调用（Controller → DB）
- [ ] 检测反向依赖（底层依赖上层）
- [ ] 自定义架构规则

### v0.3 - 代码质量分析

预计：3-4 周后

功能：
- [ ] 圈复杂度分析
- [ ] 重复代码检测
- [ ] 认知复杂度分析
- [ ] 技术债估算

### v0.4 - 内聚/耦合指标

预计：5-6 周后

功能：
- [ ] LCOM4（类内聚度）
- [ ] CBO（类耦合度）
- [ ] TCC（紧密类内聚）

### v1.0 - 完整版

预计：2-3 个月后

功能：
- [ ] 完整分析报告
- [ ] 自动化重构建议
- [ ] 配置文件支持
- [ ] 多语言支持（JS/TS/Go）
- [ ] CI/CD 集成

## 贡献

欢迎贡献代码和反馈！

**报告 Bug**：
- 说明项目类型和规模
- 附上错误信息
- 提供最小复现案例

**功能建议**：
- 描述使用场景
- 说明预期效果

## License

MIT License

---

*VibeKit - 让 Vibe Coding 可持续*
