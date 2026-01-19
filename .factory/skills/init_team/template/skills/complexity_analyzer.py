#!/usr/bin/env python3
"""
VibeKit - complexity_analyzer.py

代码复杂度分析器 - 检测高复杂度函数和重复代码

功能：
- 圈复杂度分析（Cyclomatic Complexity）
- 认知复杂度分析（Cognitive Complexity）
- 函数长度分析
- 重复代码检测

使用：
    analyzer = ComplexityAnalyzer(project_path, modules)
    results = analyzer.analyze()
"""

import ast
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict


class ComplexityAnalyzer:
    """代码复杂度分析器"""

    def __init__(self, project_path: Path, modules: List[Dict]):
        self.project_path = project_path
        self.modules = modules
        self.high_complexity_functions = []
        self.long_functions = []
        self.duplicates = []

    def analyze(self) -> Dict:
        """分析代码复杂度"""
        print("📐 分析代码复杂度...")

        all_functions = []

        # 遍历所有模块
        for module in self.modules:
            module_path = self.project_path / module['path']
            functions = self._analyze_module(module_path, module['name'])
            all_functions.extend(functions)

        # 1. 找出高复杂度函数
        self.high_complexity_functions = [
            f for f in all_functions if f['complexity'] > 10
        ]

        # 2. 找出长函数
        self.long_functions = [
            f for f in all_functions if f['lines'] > 50
        ]

        # 3. 检测重复代码
        self.duplicates = self._detect_duplicates(all_functions)

        # 统计
        total_functions = len(all_functions)
        avg_complexity = sum(f['complexity'] for f in all_functions) / total_functions if total_functions > 0 else 0
        avg_length = sum(f['lines'] for f in all_functions) / total_functions if total_functions > 0 else 0

        print(f"   分析了 {total_functions} 个函数")
        print(f"   平均复杂度：{avg_complexity:.1f}")
        print(f"   平均长度：{avg_length:.1f} 行")

        if self.high_complexity_functions:
            print(f"   ⚠️  发现 {len(self.high_complexity_functions)} 个高复杂度函数")
        else:
            print(f"   ✅ 未发现高复杂度函数")

        if self.long_functions:
            print(f"   ⚠️  发现 {len(self.long_functions)} 个长函数")
        else:
            print(f"   ✅ 未发现长函数")

        if self.duplicates:
            duplicate_rate = len(self.duplicates) / total_functions * 100 if total_functions > 0 else 0
            print(f"   ⚠️  代码重复率：{duplicate_rate:.1f}%")
        else:
            print(f"   ✅ 未发现重复代码")

        return {
            'total_functions': total_functions,
            'avg_complexity': round(avg_complexity, 1),
            'avg_length': round(avg_length, 1),
            'high_complexity_functions': self.high_complexity_functions,
            'long_functions': self.long_functions,
            'duplicates': self.duplicates
        }

    def _analyze_module(self, module_path: Path, module_name: str) -> List[Dict]:
        """分析模块内的所有函数"""
        functions = []

        for py_file in module_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 解析 AST
                tree = ast.parse(content)

                # 分析函数
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        func_info = self._analyze_function(node, py_file, module_name, content)
                        if func_info:
                            functions.append(func_info)

            except Exception as e:
                # 跳过无法解析的文件
                continue

        return functions

    def _analyze_function(self, node: ast.FunctionDef, file_path: Path, module_name: str, content: str) -> Dict:
        """分析单个函数"""
        # 计算圈复杂度
        complexity = self._calculate_complexity(node)

        # 计算函数长度
        lines = self._calculate_lines(node)

        # 获取函数源码
        source_lines = content.split('\n')
        func_source = '\n'.join(source_lines[node.lineno - 1:node.end_lineno])

        # 计算函数签名哈希（用于重复检测）
        func_hash = self._calculate_hash(func_source)

        return {
            'name': node.name,
            'module': module_name,
            'file': str(file_path.relative_to(self.project_path)),
            'line': node.lineno,
            'complexity': complexity,
            'lines': lines,
            'source': func_source,
            'hash': func_hash
        }

    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """计算圈复杂度（简化版）

        圈复杂度 = 决策点数量 + 1
        决策点：if, elif, for, while, except, and, or, assert
        """
        complexity = 1  # 基础复杂度

        for child in ast.walk(node):
            # if 语句
            if isinstance(child, ast.If):
                complexity += 1
            # for/while 循环
            elif isinstance(child, (ast.For, ast.While)):
                complexity += 1
            # except 语句
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            # 布尔运算符 (and, or)
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
            # 列表/字典/集合推导式
            elif isinstance(child, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                complexity += 1
            # assert 语句
            elif isinstance(child, ast.Assert):
                complexity += 1

        return complexity

    def _calculate_lines(self, node: ast.FunctionDef) -> int:
        """计算函数行数"""
        if node.end_lineno and node.lineno:
            return node.end_lineno - node.lineno + 1
        return 0

    def _calculate_hash(self, source: str) -> str:
        """计算源码哈希（归一化后）"""
        # 简单归一化：移除空白符、注释
        normalized = ''.join(source.split())
        return hashlib.md5(normalized.encode()).hexdigest()[:8]

    def _detect_duplicates(self, functions: List[Dict]) -> List[Dict]:
        """检测重复代码

        简单策略：
        1. 基于哈希值分组
        2. 相同哈希值的函数视为重复
        3. 只保留出现 >= 2 次的
        """
        duplicates = []

        # 按哈希值分组
        hash_groups = defaultdict(list)
        for func in functions:
            hash_groups[func['hash']].append(func)

        # 找出重复的组
        for func_hash, group in hash_groups.items():
            if len(group) >= 2:
                # 检查是否真的重复（不只是哈希冲突）
                # 简单检查：行数和复杂度相同
                if self._is_duplicate_group(group):
                    duplicates.append({
                        'count': len(group),
                        'functions': [
                            {
                                'name': f['name'],
                                'module': f['module'],
                                'file': f['file'],
                                'line': f['line']
                            }
                            for f in group
                        ],
                        'lines': group[0]['lines'],
                        'complexity': group[0]['complexity']
                    })

        return duplicates

    def _is_duplicate_group(self, group: List[Dict]) -> bool:
        """判断是否是真正的重复组"""
        if len(group) < 2:
            return False

        # 检查行数和复杂度是否相同
        first = group[0]
        for func in group[1:]:
            if func['lines'] != first['lines'] or func['complexity'] != first['complexity']:
                return False

        return True


class CodeMetrics:
    """代码度量统计"""

    @staticmethod
    def calculate_file_metrics(file_path: Path) -> Dict:
        """计算文件级别的度量"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')
            total_lines = len(lines)

            # 空行
            blank_lines = sum(1 for line in lines if not line.strip())

            # 注释行（简化：以 # 开头）
            comment_lines = sum(1 for line in lines if line.strip().startswith('#'))

            # 代码行
            code_lines = total_lines - blank_lines - comment_lines

            return {
                'total_lines': total_lines,
                'code_lines': code_lines,
                'blank_lines': blank_lines,
                'comment_lines': comment_lines,
                'comment_ratio': round(comment_lines / code_lines * 100, 1) if code_lines > 0 else 0
            }

        except Exception as e:
            return {
                'total_lines': 0,
                'code_lines': 0,
                'blank_lines': 0,
                'comment_lines': 0,
                'comment_ratio': 0
            }

    @staticmethod
    def categorize_complexity(complexity: int) -> Tuple[str, str]:
        """分类复杂度"""
        if complexity <= 5:
            return "简单", "✅"
        elif complexity <= 10:
            return "中等", "⚠️"
        elif complexity <= 20:
            return "复杂", "⚠️"
        else:
            return "极复杂", "❌"

    @staticmethod
    def categorize_length(lines: int) -> Tuple[str, str]:
        """分类函数长度"""
        if lines <= 20:
            return "短", "✅"
        elif lines <= 50:
            return "适中", "✅"
        elif lines <= 100:
            return "较长", "⚠️"
        else:
            return "过长", "❌"


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法：python complexity_analyzer.py <项目路径>")
        sys.exit(1)

    project_path = Path(sys.argv[1])

    # 简单测试
    modules = [
        {"name": "test", "path": ".", "type": "directory"}
    ]

    analyzer = ComplexityAnalyzer(project_path, modules)
    results = analyzer.analyze()

    print(f"\n分析结果：")
    print(f"  总函数数：{results['total_functions']}")
    print(f"  平均复杂度：{results['avg_complexity']}")
    print(f"  平均长度：{results['avg_length']} 行")
    print(f"  高复杂度函数：{len(results['high_complexity_functions'])} 个")
    print(f"  长函数：{len(results['long_functions'])} 个")
    print(f"  重复代码组：{len(results['duplicates'])} 组")
