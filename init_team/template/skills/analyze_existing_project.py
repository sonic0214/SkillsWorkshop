#!/usr/bin/env python3
"""
VibeKit - analyze_existing_project.py v0.2

分析存量项目的依赖关系，检测循环依赖、上帝模块和架构违规

功能：
- 扫描项目结构，识别技术栈
- 构建模块级依赖图
- 检测循环依赖（使用 Tarjan 算法）
- 检测上帝模块（被过多模块依赖）
- 检测架构违规（跨层调用、反向依赖）[v0.2 新增]
- 生成依赖图可视化（SVG）
- 生成 Markdown 分析报告

使用：
    python analyze_existing_project.py /path/to/project

输出：
    /path/to/project/.vibekit/
        ├── analysis_report.md      # 分析报告
        ├── dependency_graph.svg    # 依赖图
        ├── dependency_data.json    # 原始数据
        └── .vibekit.yaml           # 架构配置（首次运行时生成）
"""

import os
import sys
import ast
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime
from collections import defaultdict, deque

# v0.2: 导入架构验证器
try:
    from architecture_validator import ArchitectureValidator, create_default_config
    HAS_ARCH_VALIDATOR = True
except ImportError:
    HAS_ARCH_VALIDATOR = False
    print("⚠️  未找到 architecture_validator.py，跳过架构验证")

# v0.3: 导入复杂度分析器
try:
    from complexity_analyzer import ComplexityAnalyzer, CodeMetrics
    HAS_COMPLEXITY_ANALYZER = True
except ImportError:
    HAS_COMPLEXITY_ANALYZER = False
    print("⚠️  未找到 complexity_analyzer.py，跳过复杂度分析")


class ProjectScanner:
    """项目扫描器 - 识别技术栈和模块结构"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.tech_stack = []
        self.modules = []

    def scan(self) -> Dict:
        """扫描项目"""
        print(f"🔍 扫描项目：{self.project_path}")

        # 检测技术栈
        self.tech_stack = self._detect_tech_stack()
        print(f"   技术栈：{', '.join(self.tech_stack)}")

        # 发现模块
        self.modules = self._discover_modules()
        print(f"   发现 {len(self.modules)} 个模块")

        return {
            "project_path": str(self.project_path),
            "tech_stack": self.tech_stack,
            "modules": self.modules,
            "scan_time": datetime.now().isoformat()
        }

    def _detect_tech_stack(self) -> List[str]:
        """检测技术栈"""
        tech_stack = []

        # 检测 Python
        if (self.project_path / "requirements.txt").exists() or \
           (self.project_path / "setup.py").exists() or \
           (self.project_path / "pyproject.toml").exists():
            tech_stack.append("Python")

        # 检测 JavaScript/TypeScript
        if (self.project_path / "package.json").exists():
            tech_stack.append("JavaScript/TypeScript")

        # 检测 Go
        if (self.project_path / "go.mod").exists():
            tech_stack.append("Go")

        return tech_stack or ["Unknown"]

    def _discover_modules(self) -> List[Dict]:
        """发现模块（目录结构）"""
        modules = []

        # 常见的代码目录
        code_dirs = ["src", "app", "lib", "pkg", ""]

        for code_dir in code_dirs:
            search_path = self.project_path / code_dir
            if not search_path.exists():
                continue

            # 找所有包含 __init__.py 的目录（Python）或包含代码文件的目录
            for item in search_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    # 检查是否是模块
                    has_init = (item / "__init__.py").exists()
                    has_py_files = len(list(item.glob("*.py"))) > 0

                    if has_init or has_py_files:
                        modules.append({
                            "name": item.name,
                            "path": str(item.relative_to(self.project_path)),
                            "type": "package" if has_init else "directory"
                        })

        return modules


class DependencyAnalyzer:
    """依赖分析器 - 构建依赖图"""

    def __init__(self, project_path: Path, modules: List[Dict]):
        self.project_path = project_path
        self.modules = {m["name"]: m for m in modules}
        self.graph = defaultdict(set)  # module -> set of dependencies

    def analyze(self) -> Dict[str, Set[str]]:
        """分析依赖关系"""
        print("🔗 分析依赖关系...")

        for module_name, module_info in self.modules.items():
            module_path = self.project_path / module_info["path"]
            deps = self._extract_module_dependencies(module_path, module_name)
            self.graph[module_name] = deps

        print(f"   发现 {self._count_edges()} 条依赖关系")
        return dict(self.graph)

    def _extract_module_dependencies(self, module_path: Path, module_name: str) -> Set[str]:
        """提取模块的依赖"""
        dependencies = set()

        # 遍历模块内所有 Python 文件
        for py_file in module_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 解析 import 语句
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    # from X import Y
                    if isinstance(node, ast.ImportFrom):
                        if node.module:
                            dep_module = node.module.split('.')[0]
                            if dep_module in self.modules and dep_module != module_name:
                                dependencies.add(dep_module)

                    # import X
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            dep_module = alias.name.split('.')[0]
                            if dep_module in self.modules and dep_module != module_name:
                                dependencies.add(dep_module)

            except Exception as e:
                # 跳过无法解析的文件
                continue

        return dependencies

    def _count_edges(self) -> int:
        """计算依赖关系总数"""
        return sum(len(deps) for deps in self.graph.values())


class CycleDetector:
    """循环依赖检测器 - 使用 Tarjan 算法"""

    def __init__(self, graph: Dict[str, Set[str]]):
        self.graph = graph
        self.cycles = []

    def detect(self) -> List[Dict]:
        """检测循环依赖"""
        print("🔄 检测循环依赖...")

        # 使用 Tarjan 算法找强连通分量
        sccs = self._tarjan_scc()

        # 过滤出循环依赖（大小 > 1 的强连通分量）
        for scc in sccs:
            if len(scc) > 1:
                cycle_path = self._find_cycle_path(scc)
                self.cycles.append({
                    "modules": sorted(scc),
                    "path": cycle_path,
                    "severity": "P0",
                    "size": len(scc)
                })

        if self.cycles:
            print(f"   ⚠️  发现 {len(self.cycles)} 处循环依赖！")
        else:
            print(f"   ✅ 未发现循环依赖")

        return self.cycles

    def _tarjan_scc(self) -> List[Set[str]]:
        """Tarjan 强连通分量算法"""
        index_counter = [0]
        stack = []
        lowlink = {}
        index = {}
        on_stack = set()
        sccs = []

        def strongconnect(node):
            index[node] = index_counter[0]
            lowlink[node] = index_counter[0]
            index_counter[0] += 1
            stack.append(node)
            on_stack.add(node)

            # 遍历邻居
            for neighbor in self.graph.get(node, []):
                if neighbor not in index:
                    strongconnect(neighbor)
                    lowlink[node] = min(lowlink[node], lowlink[neighbor])
                elif neighbor in on_stack:
                    lowlink[node] = min(lowlink[node], index[neighbor])

            # 如果是 SCC 的根
            if lowlink[node] == index[node]:
                scc = set()
                while True:
                    w = stack.pop()
                    on_stack.remove(w)
                    scc.add(w)
                    if w == node:
                        break
                sccs.append(scc)

        for node in self.graph:
            if node not in index:
                strongconnect(node)

        return sccs

    def _find_cycle_path(self, scc: Set[str]) -> List[str]:
        """找出循环路径（用于展示）"""
        # 简单实现：从 SCC 中任意节点开始，BFS 找回自己
        start = list(scc)[0]
        queue = deque([(start, [start])])
        visited = {start}

        while queue:
            node, path = queue.popleft()

            for neighbor in self.graph.get(node, []):
                if neighbor in scc:
                    if neighbor == start and len(path) > 1:
                        return path + [start]
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, path + [neighbor]))

        return list(scc)  # fallback


class GodModuleDetector:
    """上帝模块检测器 - 检测被过多模块依赖的模块"""

    def __init__(self, graph: Dict[str, Set[str]]):
        self.graph = graph
        self.god_modules = []

    def detect(self, threshold: float = 0.3) -> List[Dict]:
        """检测上帝模块

        Args:
            threshold: 阈值，被 > threshold 比例的模块依赖 = 上帝模块
        """
        print("👑 检测上帝模块...")

        # 计算每个模块的入度（被多少模块依赖）
        in_degrees = defaultdict(int)
        for deps in self.graph.values():
            for dep in deps:
                in_degrees[dep] += 1

        # 阈值
        total_modules = len(self.graph)
        threshold_count = total_modules * threshold

        # 找出上帝模块
        for module, in_degree in in_degrees.items():
            if in_degree > threshold_count:
                dependents = [m for m, deps in self.graph.items() if module in deps]
                self.god_modules.append({
                    "name": module,
                    "dependents_count": in_degree,
                    "dependents": sorted(dependents),
                    "dependency_rate": round(in_degree / total_modules * 100, 1),
                    "severity": "P1"
                })

        if self.god_modules:
            print(f"   ⚠️  发现 {len(self.god_modules)} 个上帝模块")
        else:
            print(f"   ✅ 未发现上帝模块")

        return self.god_modules


class DependencyVisualizer:
    """依赖图可视化"""

    def __init__(self, graph: Dict[str, Set[str]], cycles: List[Dict], god_modules: List[Dict]):
        self.graph = graph
        self.cycles = cycles
        self.god_modules = god_modules

    def visualize(self, output_path: str):
        """生成 SVG 依赖图"""
        try:
            from graphviz import Digraph
        except ImportError:
            print("   ⚠️  未安装 graphviz，跳过可视化")
            print("   安装：pip install graphviz")
            return

        print("📊 生成依赖图...")

        dot = Digraph(comment='Dependency Graph')
        dot.attr(rankdir='LR')

        # 获取循环依赖中的边
        cycle_edges = set()
        for cycle in self.cycles:
            path = cycle["path"]
            for i in range(len(path) - 1):
                cycle_edges.add((path[i], path[i + 1]))

        # 上帝模块集合
        god_module_names = {gm["name"] for gm in self.god_modules}

        # 添加节点
        for module in self.graph.keys():
            if module in god_module_names:
                dot.node(module, module, color='orange', style='filled', fillcolor='lightyellow')
            else:
                dot.node(module, module)

        # 添加边
        for module, deps in self.graph.items():
            for dep in deps:
                if (module, dep) in cycle_edges:
                    # 循环依赖用红色
                    dot.edge(module, dep, color='red', penwidth='2.0')
                else:
                    # 正常依赖用蓝色
                    dot.edge(module, dep, color='blue')

        # 渲染
        try:
            dot.render(output_path, format='svg', cleanup=True)
            print(f"   ✅ 依赖图已保存：{output_path}.svg")
        except Exception as e:
            print(f"   ⚠️  生成依赖图失败：{e}")


class ReportGenerator:
    """报告生成器"""

    def __init__(self, project_info: Dict, graph: Dict, cycles: List, god_modules: List, arch_violations: List = None, complexity_results: Dict = None):
        self.project_info = project_info
        self.graph = graph
        self.cycles = cycles
        self.god_modules = god_modules
        self.arch_violations = arch_violations or []
        self.complexity_results = complexity_results or {}

    def generate(self) -> str:
        """生成 Markdown 报告"""
        print("📝 生成分析报告...")

        # 根据功能确定版本
        if self.complexity_results:
            version = "v0.3"
        elif self.arch_violations:
            version = "v0.2"
        else:
            version = "v0.1"

        # 复杂度概览
        complexity_overview = ""
        if self.complexity_results:
            high_complexity_count = len(self.complexity_results.get('high_complexity_functions', []))
            long_functions_count = len(self.complexity_results.get('long_functions', []))
            duplicates_count = len(self.complexity_results.get('duplicates', []))
            complexity_overview = f"""- **高复杂度函数**：{high_complexity_count} 个 {'⚠️' if high_complexity_count > 0 else '✅'}
- **长函数**：{long_functions_count} 个 {'⚠️' if long_functions_count > 0 else '✅'}
- **重复代码组**：{duplicates_count} 组 {'⚠️' if duplicates_count > 0 else '✅'}"""

        report = f"""# 项目依赖分析报告 {version}

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
项目路径：`{self.project_info['project_path']}`
技术栈：{', '.join(self.project_info['tech_stack'])}

---

## 📊 总体情况

- **总模块数**：{len(self.graph)}
- **依赖关系数**：{self._count_edges()}
- **循环依赖**：{len(self.cycles)} 处 {'⚠️' if self.cycles else '✅'}
- **上帝模块**：{len(self.god_modules)} 个 {'⚠️' if self.god_modules else '✅'}
- **架构违规**：{len(self.arch_violations)} 处 {'⚠️' if self.arch_violations else '✅'}
{complexity_overview}

---

{self._format_arch_violations_section()}

---

{self._format_cycles_section()}

---

{self._format_god_modules_section()}

---

{self._format_complexity_section()}

---

## 📊 依赖图可视化

![Dependency Graph](./dependency_graph.svg)

**图例**：
- 🔴 红色边：循环依赖
- 🔵 蓝色边：正常依赖
- 🟠 橙色节点：上帝模块

---

{self._format_refactor_suggestions()}

---

## 🔧 下一步

运行以下命令开始重构：

```bash
# 使用 VibeKit 重构工具（即将支持）
python skills/refactor_to_vibekit.py {self.project_info['project_path']}
```

---

*报告由 VibeKit v0.1 生成*
"""
        return report

    def _count_edges(self) -> int:
        """计算依赖关系总数"""
        return sum(len(deps) for deps in self.graph.values())

    def _format_arch_violations_section(self) -> str:
        """格式化架构违规部分（v0.2 新增）"""
        if not self.arch_violations:
            return """## ✅ 架构违规检测

未发现架构违规，架构规范良好！

_提示：如需启用架构检测，请在项目根目录创建 `.vibekit.yaml` 配置文件_"""

        # 按类型分组
        skip_layer_violations = [v for v in self.arch_violations if v['type'] == 'skip_layer']
        reverse_dep_violations = [v for v in self.arch_violations if v['type'] == 'reverse_dependency']

        section = f"## 🚨 架构违规 (P0 - 必须修复)\n\n"
        section += f"发现 **{len(self.arch_violations)}** 处架构违规：\n\n"

        # 跨层调用
        if skip_layer_violations:
            section += f"### 1. 跨层调用 ({len(skip_layer_violations)} 处)\n\n"
            section += "_上层模块跳过中间层，直接依赖底层模块_\n\n"

            for i, v in enumerate(skip_layer_violations, 1):
                section += f"#### {i}. `{v['from_module']}` ({v['from_layer']}) → `{v['to_module']}` ({v['to_layer']})\n\n"
                section += f"**跳过的层**：{', '.join(v['skipped_layers'])}\n\n"
                section += f"**问题**：\n"
                section += f"- {v['from_layer']} 层跳过 {len(v['skipped_layers'])} 个中间层，直接访问 {v['to_layer']} 层\n"
                section += f"- 违反分层架构原则，增加耦合度\n"
                section += f"- 业务逻辑可能散落在多处\n\n"
                section += f"**建议**：\n"
                section += f"1. 通过中间层访问（{v['from_layer']} → {' → '.join(v['skipped_layers'])} → {v['to_layer']}）\n"
                section += f"2. 将逻辑移到合适的层\n"
                section += f"3. 使用依赖注入解耦\n\n"
                section += f"**重构难度**：⭐⭐⭐ (3/5)  \n"
                section += f"**预估时间**：4 小时\n\n"

        # 反向依赖
        if reverse_dep_violations:
            section += f"### 2. 反向依赖 ({len(reverse_dep_violations)} 处)\n\n"
            section += "_底层模块依赖上层模块，违反依赖倒置原则_\n\n"

            for i, v in enumerate(reverse_dep_violations, 1):
                section += f"#### {i}. `{v['from_module']}` ({v['from_layer']}) → `{v['to_module']}` ({v['to_layer']})\n\n"
                section += f"**依赖方向**：{v['direction']}\n\n"
                section += f"**问题**：\n"
                section += f"- 底层 {v['from_layer']} 依赖了上层 {v['to_layer']}\n"
                section += f"- 违反依赖倒置原则（DIP）\n"
                section += f"- 可能形成循环依赖\n"
                section += f"- 底层模块无法独立复用\n\n"
                section += f"**建议**：\n"
                section += f"1. 使用依赖注入（DI）\n"
                section += f"2. 定义接口/抽象类，反转依赖\n"
                section += f"3. 使用事件驱动模式解耦\n\n"
                section += f"**重构难度**：⭐⭐⭐⭐ (4/5)  \n"
                section += f"**预估时间**：6 小时\n\n"

        return section

    def _format_cycles_section(self) -> str:
        """格式化循环依赖部分"""
        if not self.cycles:
            return """## ✅ 循环依赖检测

未发现循环依赖，项目结构良好！"""

        section = f"## 🚨 循环依赖 (P0 - 必须修复)\n\n发现 **{len(self.cycles)}** 处循环依赖：\n"

        for i, cycle in enumerate(self.cycles, 1):
            modules = cycle["modules"]
            path = cycle["path"]

            section += f"\n### {i}. {' ↔ '.join(modules)}\n\n"
            section += f"**依赖路径**：\n```\n{' → '.join(path)}\n```\n\n"
            section += "**影响**：\n"
            section += "- ❌ 无法独立测试任何一个模块\n"
            section += "- ❌ 修改一处可能影响多处\n"
            section += "- ❌ 无法独立部署\n\n"
            section += "**建议**：\n"
            section += "1. 提取共享类型到独立模块\n"
            section += "2. 使用依赖注入，而非直接导入\n"
            section += "3. 考虑引入事件驱动模式解耦\n\n"
            section += f"**重构难度**：⭐⭐⭐ (3/5)  \n"
            section += f"**预估时间**：{len(modules) * 4} 小时\n"

        return section

    def _format_god_modules_section(self) -> str:
        """格式化上帝模块部分"""
        if not self.god_modules:
            return """## ✅ 上帝模块检测

未发现上帝模块，模块职责划分清晰！"""

        section = f"## ⚠️ 上帝模块 (P1 - 应该优化)\n\n发现 **{len(self.god_modules)}** 个上帝模块：\n"

        for i, gm in enumerate(self.god_modules, 1):
            section += f"\n### {i}. `{gm['name']}`\n\n"
            section += f"**被依赖次数**：{gm['dependents_count']}/{len(self.graph)} 模块 "
            section += f"(依赖率 {gm['dependency_rate']}%)\n\n"
            section += "**依赖者**：\n"
            for dep in gm['dependents'][:5]:
                section += f"- `{dep}`\n"
            if len(gm['dependents']) > 5:
                section += f"- ... 还有 {len(gm['dependents']) - 5} 个\n"
            section += "\n**问题**：\n"
            section += f"- 被过多模块依赖，任何修改都可能影响 {gm['dependents_count']} 个模块\n"
            section += "- 是系统的脆弱点和瓶颈\n\n"
            section += "**建议**：\n"
            section += "1. 拆分为领域特定的子模块\n"
            section += "2. 将通用函数移到标准库或第三方库\n"
            section += "3. 使用接口隔离，减少直接依赖\n\n"
            section += f"**重构难度**：⭐⭐⭐⭐ (4/5)  \n"
            section += f"**预估时间**：{gm['dependents_count'] * 2} 小时\n"

        return section

    def _format_complexity_section(self) -> str:
        """格式化代码复杂度部分（v0.3 新增）"""
        if not self.complexity_results:
            return ""

        total_functions = self.complexity_results.get('total_functions', 0)
        avg_complexity = self.complexity_results.get('avg_complexity', 0)
        avg_length = self.complexity_results.get('avg_length', 0)
        high_complexity_functions = self.complexity_results.get('high_complexity_functions', [])
        long_functions = self.complexity_results.get('long_functions', [])
        duplicates = self.complexity_results.get('duplicates', [])

        # 如果没有任何问题，返回简洁版本
        if not high_complexity_functions and not long_functions and not duplicates:
            return f"""## ✅ 代码质量检测

**总体情况**：
- 分析了 {total_functions} 个函数
- 平均复杂度：{avg_complexity}（良好）
- 平均长度：{avg_length} 行（良好）
- 未发现高复杂度函数
- 未发现过长函数
- 未发现重复代码

代码质量良好，继续保持！"""

        section = f"## 📐 代码质量分析 (v0.3 新增)\n\n"
        section += f"**总体情况**：\n"
        section += f"- 分析了 **{total_functions}** 个函数\n"
        section += f"- 平均复杂度：**{avg_complexity}**\n"
        section += f"- 平均长度：**{avg_length}** 行\n\n"

        # 1. 高复杂度函数
        if high_complexity_functions:
            section += f"### 1. 高复杂度函数 ({len(high_complexity_functions)} 个) ⚠️\n\n"
            section += "_圈复杂度 > 10 的函数，建议拆分_\n\n"

            # 按复杂度排序，显示前 10 个
            sorted_funcs = sorted(high_complexity_functions, key=lambda x: x['complexity'], reverse=True)
            for i, func in enumerate(sorted_funcs[:10], 1):
                category, emoji = CodeMetrics.categorize_complexity(func['complexity'])
                section += f"#### {i}. `{func['name']}` - {func['module']}\n\n"
                section += f"- **位置**：{func['file']}:{func['line']}\n"
                section += f"- **复杂度**：{func['complexity']} {emoji} ({category})\n"
                section += f"- **长度**：{func['lines']} 行\n\n"
                section += "**建议**：\n"
                section += "- 拆分为多个小函数\n"
                section += "- 提取条件判断到独立函数\n"
                section += "- 使用策略模式简化分支逻辑\n\n"

            if len(sorted_funcs) > 10:
                section += f"_... 还有 {len(sorted_funcs) - 10} 个高复杂度函数_\n\n"

        # 2. 长函数
        if long_functions:
            section += f"### 2. 长函数 ({len(long_functions)} 个) ⚠️\n\n"
            section += "_行数 > 50 的函数，建议重构_\n\n"

            # 按长度排序，显示前 10 个
            sorted_funcs = sorted(long_functions, key=lambda x: x['lines'], reverse=True)
            for i, func in enumerate(sorted_funcs[:10], 1):
                category, emoji = CodeMetrics.categorize_length(func['lines'])
                section += f"#### {i}. `{func['name']}` - {func['module']}\n\n"
                section += f"- **位置**：{func['file']}:{func['line']}\n"
                section += f"- **长度**：{func['lines']} 行 {emoji} ({category})\n"
                section += f"- **复杂度**：{func['complexity']}\n\n"
                section += "**建议**：\n"
                section += "- 按职责拆分函数\n"
                section += "- 提取重复代码段\n"
                section += "- 简化嵌套结构\n\n"

            if len(sorted_funcs) > 10:
                section += f"_... 还有 {len(sorted_funcs) - 10} 个长函数_\n\n"

        # 3. 重复代码
        if duplicates:
            section += f"### 3. 重复代码 ({len(duplicates)} 组) ⚠️\n\n"
            section += "_发现结构相似的代码，建议提取复用_\n\n"

            for i, dup in enumerate(duplicates[:5], 1):
                section += f"#### {i}. 重复组 ({dup['count']} 处)\n\n"
                section += f"**相似函数**：\n"
                for func in dup['functions']:
                    section += f"- `{func['name']}` ({func['module']}) - {func['file']}:{func['line']}\n"
                section += f"\n**代码特征**：\n"
                section += f"- 长度：{dup['lines']} 行\n"
                section += f"- 复杂度：{dup['complexity']}\n\n"
                section += "**建议**：\n"
                section += "- 提取为公共函数\n"
                section += "- 考虑使用模板方法模式\n"
                section += "- 移到工具类或基类\n\n"

            if len(duplicates) > 5:
                section += f"_... 还有 {len(duplicates) - 5} 组重复代码_\n\n"

        return section

    def _format_refactor_suggestions(self) -> str:
        """格式化重构建议"""
        if not self.cycles and not self.god_modules:
            return """## 🎉 恭喜！

项目架构健康，暂无需重构。

建议：
- 保持当前的模块划分
- 定期运行分析，监控依赖变化
"""

        section = "## 💡 重构建议\n\n"
        section += "基于以上分析，建议按以下顺序重构：\n\n"

        total_hours = 0

        if self.cycles:
            cycle_hours = sum(len(c["modules"]) * 4 for c in self.cycles)
            total_hours += cycle_hours
            section += f"### Phase 1：消除循环依赖（{cycle_hours // 8 + 1} 天）\n\n"
            section += "**优先级**：P0（必须做）\n\n"
            for i, cycle in enumerate(self.cycles, 1):
                modules = ' ↔ '.join(cycle["modules"])
                hours = len(cycle["modules"]) * 4
                section += f"{i}. **{modules}**（{hours}h）\n"
            section += "\n"

        if self.god_modules:
            gm_hours = sum(gm["dependents_count"] * 2 for gm in self.god_modules)
            total_hours += gm_hours
            section += f"### Phase 2：拆解上帝模块（{gm_hours // 8 + 1} 天）\n\n"
            section += "**优先级**：P1（应该做）\n\n"
            for i, gm in enumerate(self.god_modules, 1):
                hours = gm["dependents_count"] * 2
                section += f"{i}. **`{gm['name']}`**（{hours}h）\n"
            section += "\n"

        section += f"### Phase 3：验证（0.5 天）\n\n"
        section += "1. 运行所有测试，确保功能不变\n"
        section += "2. 重新运行分析，确认问题已解决\n"
        section += "3. 提交重构代码\n\n"

        section += f"---\n\n**总预估时间**：{total_hours} 小时（约 {total_hours // 8 + 1} 个工作日）\n"

        return section


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法：python analyze_existing_project.py <项目路径>")
        sys.exit(1)

    project_path = sys.argv[1]

    if not os.path.exists(project_path):
        print(f"❌ 项目路径不存在：{project_path}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  VibeKit - 项目依赖分析 v0.2")
    print(f"{'='*60}\n")

    # 1. 扫描项目
    scanner = ProjectScanner(project_path)
    project_info = scanner.scan()

    if not project_info["modules"]:
        print("\n⚠️  未发现任何模块，请确认项目结构")
        sys.exit(1)

    print()

    # 2. 分析依赖
    analyzer = DependencyAnalyzer(Path(project_path), project_info["modules"])
    graph = analyzer.analyze()

    print()

    # 3. 检测循环依赖
    cycle_detector = CycleDetector(graph)
    cycles = cycle_detector.detect()

    print()

    # 4. 检测上帝模块
    god_detector = GodModuleDetector(graph)
    god_modules = god_detector.detect(threshold=0.3)

    print()

    # 5. 检测架构违规（v0.2 新增）
    arch_violations = []
    if HAS_ARCH_VALIDATOR:
        config_file = Path(project_path) / ".vibekit.yaml"

        # 如果没有配置文件，提示创建
        if not config_file.exists():
            print("💡 提示：创建 .vibekit.yaml 可启用架构违规检测")
            print(f"   运行：python architecture_validator.py {project_path}")
            print()
        else:
            # 运行架构验证
            arch_validator = ArchitectureValidator(str(config_file))
            arch_violations = arch_validator.validate(graph, project_info["modules"])
            print()

    # 6. 分析代码复杂度（v0.3 新增）
    complexity_results = {}
    if HAS_COMPLEXITY_ANALYZER:
        complexity_analyzer = ComplexityAnalyzer(Path(project_path), project_info["modules"])
        complexity_results = complexity_analyzer.analyze()
        print()

    # 7. 生成输出目录
    output_dir = Path(project_path) / ".vibekit"
    output_dir.mkdir(exist_ok=True)

    # 8. 保存原始数据
    data_file = output_dir / "dependency_data.json"
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump({
            "project_info": project_info,
            "graph": {k: list(v) for k, v in graph.items()},
            "cycles": cycles,
            "god_modules": god_modules,
            "arch_violations": arch_violations,  # v0.2
            "complexity": complexity_results  # v0.3
        }, f, indent=2, ensure_ascii=False)

    # 9. 生成可视化
    visualizer = DependencyVisualizer(graph, cycles, god_modules)
    visualizer.visualize(str(output_dir / "dependency_graph"))

    print()

    # 10. 生成报告
    reporter = ReportGenerator(project_info, graph, cycles, god_modules, arch_violations, complexity_results)  # v0.3
    report = reporter.generate()

    report_file = output_dir / "analysis_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"   ✅ 报告已保存：{report_file}")

    print(f"\n{'='*60}")
    print(f"  ✅ 分析完成！")
    print(f"{'='*60}\n")
    print(f"查看报告：{report_file}")
    print(f"查看依赖图：{output_dir / 'dependency_graph.svg'}")

    # 返回状态码
    if cycles:
        print(f"\n⚠️  发现 {len(cycles)} 处循环依赖（P0 问题）")
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
