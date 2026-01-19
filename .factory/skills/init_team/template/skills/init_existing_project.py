#!/usr/bin/env python3
"""
VibeKit - init_existing_project.py

功能: 存量项目架构分析初始化
- 分析现有项目结构
- 生成项目初始化架构梳理文档
- 创建开发环境配置
- 集成 VibeKit 分析能力

使用:
    python project_team/skills/init_existing_project.py /path/to/existing/project

触发条件:
    - Agent 检测到存量项目（有现有代码）
    - 询问用户是否进行架构分析
    - 用户确认后执行此脚本

输出:
    - 项目架构梳理文档
    - VibeKit 分析报告
    - 开发环境配置建议
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# 导入 VibeKit 分析工具
try:
    from analyze_existing_project import ProjectAnalyzer
    from architecture_validator import ArchitectureValidator, create_default_config
    from complexity_analyzer import ComplexityAnalyzer
    HAS_ANALYZERS = True
except ImportError as e:
    HAS_ANALYZERS = False
    print(f"⚠️  导入分析工具失败: {e}")
    print("将生成基础架构梳理文档")


class ExistingProjectAnalyzer:
    """存量项目架构分析器"""

    def __init__(self, project_path: str):
        self.project_path = Path(project_path).resolve()
        self.project_name = self.project_path.name
        self.analysis_result = {}

    def detect_project_type(self) -> Dict:
        """检测项目类型和技术栈"""
        print("🔍 检测项目类型和技术栈...")

        project_info = {
            "name": self.project_name,
            "path": str(self.project_path),
            "size_mb": 0,
            "file_count": 0,
            "languages": {},
            "frameworks": [],
            "build_tools": [],
            "test_frameworks": [],
            "package_managers": []
        }

        # 统计文件大小和数量
        total_size = 0
        file_count = 0
        language_files = {}

        # 文件类型到语言的映射
        language_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".jsx": "React/JavaScript",
            ".tsx": "React/TypeScript",
            ".java": "Java",
            ".go": "Go",
            ".rs": "Rust",
            ".cpp": "C++",
            ".c": "C",
            ".cs": "C#",
            ".php": "PHP",
            ".rb": "Ruby",
            ".swift": "Swift",
            ".kt": "Kotlin"
        }

        # 检测框架和工具
        for item in self.project_path.rglob("*"):
            if item.is_file():
                file_count += 1
                total_size += item.stat().st_size

                # 语言检测
                suffix = item.suffix.lower()
                if suffix in language_map:
                    lang = language_map[suffix]
                    language_files[lang] = language_files.get(lang, 0) + 1

                # 框架检测
                if item.name in ["package.json", "requirements.txt", "Pipfile", "yarn.lock", "pom.xml", "build.gradle"]:
                    if item.name == "package.json":
                        try:
                            content = item.read_text()
                            if "react" in content:
                                project_info["frameworks"].append("React")
                            if "vue" in content:
                                project_info["frameworks"].append("Vue.js")
                            if "angular" in content:
                                project_info["frameworks"].append("Angular")
                            if "express" in content:
                                project_info["frameworks"].append("Express.js")
                            if "next" in content:
                                project_info["frameworks"].append("Next.js")
                            project_info["package_managers"].append("npm/yarn")
                        except:
                            pass
                    elif item.name == "requirements.txt":
                        project_info["frameworks"].extend(["Django", "Flask", "FastAPI"])  # 可能的框架
                        project_info["package_managers"].append("pip")
                    elif item.name == "Pipfile":
                        project_info["package_managers"].append("pipenv")
                    elif item.name == "yarn.lock":
                        project_info["package_managers"].append("yarn")
                    elif item.name in ["pom.xml"]:
                        project_info["package_managers"].append("Maven")
                        project_info["frameworks"].append("Java/Spring")
                    elif item.name == "build.gradle":
                        project_info["package_managers"].append("Gradle")
                        project_info["frameworks"].append("Java/Spring")

                # 测试框架检测
                if "test" in item.name.lower() or item.name.startswith("test_"):
                    if item.suffix == ".py":
                        project_info["test_frameworks"].append("pytest/unittest")
                    elif item.suffix in [".js", ".ts"]:
                        if "jest" in str(item).lower():
                            project_info["test_frameworks"].append("Jest")
                        elif "mocha" in str(item).lower():
                            project_info["test_frameworks"].append("Mocha")

                # 构建工具检测
                if item.name in ["Makefile", "webpack.config.js", "rollup.config.js", "vite.config.js"]:
                    if item.name == "Makefile":
                        project_info["build_tools"].append("Make")
                    elif "webpack" in item.name:
                        project_info["build_tools"].append("Webpack")
                    elif "rollup" in item.name:
                        project_info["build_tools"].append("Rollup")
                    elif "vite" in item.name:
                        project_info["build_tools"].append("Vite")

        project_info["size_mb"] = round(total_size / (1024 * 1024), 2)
        project_info["file_count"] = file_count
        project_info["languages"] = language_files

        # 去重
        for key in ["frameworks", "build_tools", "test_frameworks", "package_managers"]:
            project_info[key] = list(set(project_info[key]))

        print(f"   项目大小: {project_info['size_mb']} MB")
        print(f"   文件数量: {project_info['file_count']}")
        print(f"   主要语言: {max(language_files.items(), key=lambda x: x[1])[0] if language_files else 'Unknown'}")

        return project_info

    def analyze_project_structure(self) -> Dict:
        """分析项目结构"""
        print("🏗️  分析项目结构...")

        structure = {
            "directories": [],
            "key_files": [],
            "patterns": []
        }

        # 获取主要目录
        dirs = []
        for item in self.project_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                dirs.append({
                    "name": item.name,
                    "file_count": len(list(item.rglob("*"))),
                    "purpose": self._guess_directory_purpose(item.name)
                })

        structure["directories"] = sorted(dirs, key=lambda x: x["file_count"], reverse=True)[:10]

        # 获取关键文件
        key_files = []
        for item in self.project_path.rglob("*"):
            if item.is_file():
                if self._is_key_file(item.name):
                    key_files.append({
                        "name": item.name,
                        "path": str(item.relative_to(self.project_path)),
                        "purpose": self._guess_file_purpose(item.name)
                    })

        structure["key_files"] = key_files[:20]

        # 检测架构模式
        structure["patterns"] = self._detect_architecture_patterns()

        return structure

    def _guess_directory_purpose(self, dir_name: str) -> str:
        """猜测目录用途"""
        dir_name_lower = dir_name.lower()

        purpose_map = {
            "src": "源代码",
            "source": "源代码",
            "lib": "库文件",
            "app": "应用代码",
            "test": "测试代码",
            "tests": "测试代码",
            "spec": "测试代码",
            "specs": "测试代码",
            "docs": "文档",
            "doc": "文档",
            "documentation": "文档",
            "build": "构建输出",
            "dist": "分发文件",
            "out": "输出文件",
            "config": "配置文件",
            "conf": "配置文件",
            "scripts": "脚本文件",
            "tools": "工具文件",
            "utils": "工具函数",
            "vendor": "第三方库",
            "node_modules": "Node.js 依赖",
            "__pycache__": "Python 缓存",
            "assets": "资源文件",
            "static": "静态资源",
            "public": "公共资源",
            "styles": "样式文件",
            "css": "样式文件",
            "stylesheets": "样式文件"
        }

        return purpose_map.get(dir_name_lower, "其他")

    def _is_key_file(self, filename: str) -> bool:
        """判断是否为关键文件"""
        key_file_patterns = [
            "package.json", "requirements.txt", "Pipfile", "poetry.lock",
            "pom.xml", "build.gradle", "Cargo.toml", "go.mod",
            "README.md", "README.txt", "CHANGELOG.md",
            "LICENSE", "LICENSE.txt", "COPYRIGHT",
            "Dockerfile", "docker-compose.yml", "docker-compose.yaml",
            ".gitignore", ".gitattributes", ".env.example",
            "Makefile", "CMakeLists.txt", "build.gradle.kts",
            "tsconfig.json", "jsconfig.json", "babel.config.js",
            "webpack.config.js", "rollup.config.js", "vite.config.js",
            ".eslintrc.js", ".eslintrc.json", "prettier.config.js",
            "pytest.ini", "tox.ini", "jest.config.js",
            "setup.py", "setup.cfg", "pyproject.toml"
        ]

        return filename in key_file_patterns

    def _guess_file_purpose(self, filename: str) -> str:
        """猜测文件用途"""
        if filename in ["package.json", "requirements.txt", "Pipfile", "poetry.lock"]:
            return "依赖管理"
        elif filename in ["pom.xml", "build.gradle", "Cargo.toml", "go.mod"]:
            return "项目构建"
        elif filename.startswith("README"):
            return "项目说明"
        elif filename in ["LICENSE", "LICENSE.txt", "COPYRIGHT"]:
            return "许可证"
        elif filename in ["Dockerfile", "docker-compose.yml", "docker-compose.yaml"]:
            return "容器化"
        elif filename.startswith(".git"):
            return "Git 配置"
        elif filename in ["Makefile", "CMakeLists.txt"]:
            return "构建脚本"
        elif filename.endswith((".config.js", ".config.json", ".config.ts")):
            return "工具配置"
        elif filename in [".eslintrc.js", ".eslintrc.json", "prettier.config.js"]:
            return "代码规范"
        elif filename in ["pytest.ini", "tox.ini", "jest.config.js"]:
            return "测试配置"
        elif filename in ["setup.py", "setup.cfg", "pyproject.toml"]:
            return "Python 打包"
        else:
            return "配置文件"

    def _detect_architecture_patterns(self) -> List[str]:
        """检测架构模式"""
        patterns = []

        # 检测目录结构模式
        has_src = (self.project_path / "src").exists()
        has_lib = (self.project_path / "lib").exists()
        has_app = (self.project_path / "app").exists()

        if has_src:
            patterns.append("标准 src/ 布局")
        if has_lib:
            patterns.append("库模块布局")
        if has_app:
            patterns.append("应用模块布局")

        # 检测分层架构
        layers = ["controller", "service", "repository", "model", "view"]
        found_layers = []
        for layer in layers:
            for item in self.project_path.rglob("*"):
                if item.is_dir() and layer in item.name.lower():
                    found_layers.append(layer)
                    break

        if found_layers:
            patterns.append(f"分层架构 (发现: {', '.join(found_layers)})")

        # 检测 MVC 模式
        mvc_components = []
        if any("model" in d.name.lower() for d in self.project_path.rglob("*") if d.is_dir()):
            mvc_components.append("Model")
        if any("view" in d.name.lower() for d in self.project_path.rglob("*") if d.is_dir()):
            mvc_components.append("View")
        if any("controller" in d.name.lower() for d in self.project_path.rglob("*") if d.is_dir()):
            mvc_components.append("Controller")

        if len(mvc_components) >= 2:
            patterns.append(f"MVC 模式 ({', '.join(mvc_components)})")

        # 检测微服务特征
        if (self.project_path / "docker").exists() or (self.project_path / "k8s").exists():
            patterns.append("容器化/微服务架构")

        if not patterns:
            patterns.append("未识别特定的架构模式")

        return patterns

    def run_vibekit_analysis(self) -> Optional[Dict]:
        """运行 VibeKit 深度分析"""
        if not HAS_ANALYZERS:
            print("⚠️  VibeKit 分析工具不可用，跳过深度分析")
            return None

        print("🔬 运行 VibeKit 深度分析...")

        try:
            # 运行基础的项目分析
            analyzer = ProjectAnalyzer(str(self.project_path))
            result = analyzer.analyze()

            print(f"   发现 {len(result['modules'])} 个模块")
            print(f"   依赖关系: {len(result['dependency_graph'])} 条")

            if result['circular_dependencies']:
                print(f"   ⚠️  循环依赖: {len(result['circular_dependencies'])} 处")

            if result['god_modules']:
                print(f"   ⚠️  上帝模块: {len(result['god_modules'])} 个")

            return result

        except Exception as e:
            print(f"❌ VibeKit 分析失败: {e}")
            return None

    def generate_init_document(self, project_info: Dict, structure: Dict, vibekit_result: Optional[Dict]) -> str:
        """生成项目初始化架构梳理文档"""

        doc_content = f"""# 项目架构梳理报告

## 📋 项目概览

**项目名称**: {project_info['name']}
**项目路径**: {project_info['path']}
**分析时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**项目大小**: {project_info['size_mb']} MB
**文件数量**: {project_info['file_count']}

## 🛠️ 技术栈

### 编程语言
"""

        # 添加语言统计
        for lang, count in sorted(project_info['languages'].items(), key=lambda x: x[1], reverse=True):
            doc_content += f"- **{lang}**: {count} 个文件\n"

        # 框架和工具
        doc_content += f"""
### 框架和库
{self._format_list(project_info['frameworks'])}

### 构建工具
{self._format_list(project_info['build_tools'])}

### 测试框架
{self._format_list(project_info['test_frameworks'])}

### 包管理器
{self._format_list(project_info['package_managers'])}

## 🏗️ 项目结构

### 主要目录
| 目录名称 | 文件数量 | 用途 |
|---------|---------|------|
"""

        for dir_info in structure['directories'][:10]:
            doc_content += f"| {dir_info['name']} | {dir_info['file_count']} | {dir_info['purpose']} |\n"

        # 关键文件
        doc_content += f"""
### 关键配置文件
| 文件名 | 路径 | 用途 |
|-------|------|------|
"""

        for file_info in structure['key_files'][:15]:
            doc_content += f"| {file_info['name']} | `{file_info['path']}` | {file_info['purpose']} |\n"

        # 架构模式
        doc_content += f"""
## 🎯 架构模式

检测到的架构模式：
"""

        for pattern in structure['patterns']:
            doc_content += f"- {pattern}\n"

        # VibeKit 分析结果
        if vibekit_result:
            doc_content += f"""
## 📊 VibeKit 深度分析

### 模块统计
- **总模块数**: {len(vibekit_result.get('modules', []))}
- **依赖关系数**: {len(vibekit_result.get('dependency_graph', {}))}
- **最大依赖深度**: {vibekit_result.get('max_dependency_depth', 0)}

### 架构质量问题
"""

            # 循环依赖
            circular_deps = vibekit_result.get('circular_dependencies', [])
            if circular_deps:
                doc_content += f"""
#### ⚠️ 循环依赖 ({len(circular_deps)} 处)
发现循环依赖，建议重构：
"""
                for i, dep in enumerate(circular_deps[:5], 1):
                    doc_content += f"{i}. {' → '.join(dep)}\n"
                if len(circular_deps) > 5:
                    doc_content += f"... 还有 {len(circular_deps) - 5} 处\n"

            # 上帝模块
            god_modules = vibekit_result.get('god_modules', [])
            if god_modules:
                doc_content += f"""
#### ⚠️ 上帝模块 ({len(god_modules)} 个)
被过多模块依赖的组件：
"""
                for module in god_modules[:5]:
                    doc_content += f"- **{module['name']}**: 被 {module['fan_in']} 个模块依赖\n"

            # 复杂度分析
            if 'complexity' in vibekit_result:
                complexity = vibekit_result['complexity']
                doc_content += f"""
#### 代码复杂度
- **总函数数**: {complexity.get('total_functions', 0)}
- **平均复杂度**: {complexity.get('avg_complexity', 0)}
- **平均函数长度**: {complexity.get('avg_length', 0)} 行
- **高复杂度函数**: {len(complexity.get('high_complexity_functions', []))} 个
- **长函数**: {len(complexity.get('long_functions', []))} 个
"""

        # 开发环境建议
        doc_content += f"""
## 🚀 开发环境配置建议

### 1. 推荐工具链
"""

        if "Python" in project_info['languages']:
            doc_content += """- **IDE**: PyCharm / VS Code
- **环境管理**: pyenv + virtualenv / conda
- **代码格式化**: black + isort
- **代码检查**: flake8 / pylint
- **测试**: pytest
"""

        if any(lang in project_info['languages'] for lang in ["JavaScript", "TypeScript"]):
            doc_content += """- **IDE**: VS Code / WebStorm
- **包管理器**: npm / yarn / pnpm
- **代码格式化**: Prettier
- **代码检查**: ESLint
- **测试**: Jest / Vitest
"""

        # 添加 VibeKit 集成建议
        doc_content += f"""
### 2. VibeKit 集成
建议将项目接入 VibeKit 进行持续的架构质量监控：

```bash
# 1. 复制 VibeKit 到项目
cp -r /path/to/MyBrain/skills/init_team/template/skills ./vibekit

# 2. 定期运行分析
python vibekit/analyze_existing_project.py .

# 3. 查看报告
open ./.vibekit/analysis_report.md
```

### 3. 项目结构优化建议

"""

        # 根据分析结果给出建议
        if vibekit_result and vibekit_result.get('circular_dependencies'):
            doc_content += """- **优先级1**: 解决循环依赖问题
  - 识别循环依赖的根本原因
  - 考虑使用依赖注入或事件驱动架构
  - 将相关模块合并或重新设计

"""

        if structure['directories'] and not any(d['name'] in ['src', 'lib', 'app'] for d in structure['directories']):
            doc_content += """- **优先级2**: 规范化目录结构
  - 创建 src/ 目录存放源代码
  - 创建 tests/ 目录存放测试代码
  - 创建 docs/ 目录存放文档

"""

        if not project_info['test_frameworks']:
            doc_content += """- **优先级3**: 添加测试框架
  - 根据语言选择合适的测试框架
  - 配置持续集成
  - 设置测试覆盖率目标

"""

        doc_content += f"""
### 4. 下一步行动
1. [ ] 根据建议重构代码结构
2. [ ] 集成 VibeKit 进行定期检查
3. [ ] 建立代码规范和 Review 流程
4. [ ] 完善文档和测试覆盖率

---
*报告由 VibeKit 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        return doc_content

    def _format_list(self, items: List[str]) -> str:
        """格式化列表"""
        if not items:
            return "- 无"
        return "\n".join(f"- {item}" for item in items)

    def create_vibekit_config(self):
        """创建 VibeKit 配置文件"""
        config_content = """# VibeKit 项目配置文件

# 项目信息
project:
  name: """ + self.project_name + """
  type: existing_project

# 分析配置
analysis:
  # 忽略的目录
  ignore:
    - node_modules
    - __pycache__
    - .git
    - .vscode
    - .idea
    - dist
    - build
    - target
    - vendor
    - .venv
    - venv
    - env

  # 分析深度
  depth:
    max_modules: 200
    max_dependency_depth: 10

  # 质量阈值
  thresholds:
    circular_dependency_severity: "error"
    god_module_threshold: 0.3  # 30%
    max_function_complexity: 10
    max_function_length: 50

# 输出配置
output:
  formats: ["markdown", "json"]
  include_visualization: true
  include_complexity: true
"""

        vibekit_dir = self.project_path / ".vibekit"
        vibekit_dir.mkdir(exist_ok=True)

        config_file = vibekit_dir / "vibekit.yaml"
        config_file.write_text(config_content, encoding='utf-8')

        return config_file

    def analyze(self) -> Dict:
        """执行完整分析流程"""
        print("=" * 60)
        print(f"🚀 VibeKit 存量项目架构分析")
        print("=" * 60)
        print(f"📁 项目路径: {self.project_path}")
        print()

        # 1. 基础项目信息
        project_info = self.detect_project_type()

        # 2. 项目结构分析
        structure = self.analyze_project_structure()

        # 3. VibeKit 深度分析
        vibekit_result = self.run_vibekit_analysis()

        # 4. 生成初始化文档
        print("📄 生成架构梳理文档...")
        doc_content = self.generate_init_document(project_info, structure, vibekit_result)

        # 保存文档
        doc_file = self.project_path / "PROJECT_ARCHITECTURE_ANALYSIS.md"
        doc_file.write_text(doc_content, encoding='utf-8')
        print(f"   ✓ 文档已保存: {doc_file}")

        # 5. 创建 VibeKit 配置
        print("⚙️  创建 VibeKit 配置...")
        config_file = self.create_vibekit_config()
        print(f"   ✓ 配置已保存: {config_file}")

        # 6. 如果有 VibeKit 分析结果，也保存
        if vibekit_result:
            vibekit_dir = self.project_path / ".vibekit"
            vibekit_dir.mkdir(exist_ok=True)

            # 保存分析数据
            data_file = vibekit_dir / "analysis_data.json"
            data_file.write_text(json.dumps(vibekit_result, indent=2, ensure_ascii=False), encoding='utf-8')
            print(f"   ✓ 分析数据已保存: {data_file}")

        # 保存综合结果
        self.analysis_result = {
            "project_info": project_info,
            "structure": structure,
            "vibekit_result": vibekit_result,
            "documents": {
                "architecture_analysis": str(doc_file),
                "vibekit_config": str(config_file)
            }
        }

        print()
        print("=" * 60)
        print("✅ 存量项目架构分析完成！")
        print("=" * 60)
        print()
        print(f"📄 架构梳理文档: {doc_file}")
        print(f"⚙️  VibeKit 配置: {config_file}")
        if vibekit_result:
            print(f"📊 分析数据: {data_file}")
        print()
        print("📋 主要发现:")
        if project_info['languages']:
            main_lang = max(project_info['languages'].items(), key=lambda x: x[1])[0]
            print(f"  • 主要语言: {main_lang}")
        if structure['patterns']:
            print(f"  • 架构模式: {', '.join(structure['patterns'])}")
        if vibekit_result:
            if vibekit_result.get('circular_dependencies'):
                print(f"  • ⚠️  发现 {len(vibekit_result['circular_dependencies'])} 处循环依赖")
            if vibekit_result.get('god_modules'):
                print(f"  • ⚠️  发现 {len(vibekit_result['god_modules'])} 个上帝模块")
        print()
        print("🚀 下一步:")
        print(f"  1. 查看 {doc_file}")
        print(f"  2. 根据建议优化项目结构")
        print(f"  3. 集成 VibeKit 进行持续监控")
        print()

        return self.analysis_result


def main():
    if len(sys.argv) < 2:
        print("VibeKit - init_existing_project.py")
        print()
        print("用法: python init_existing_project.py /path/to/existing/project")
        print()
        print("功能:")
        print("  - 分析存量项目结构和技术栈")
        print("  - 检测架构模式和潜在问题")
        print("  - 生成项目初始化架构梳理文档")
        print("  - 创建 VibeKit 配置文件")
        print()
        print("示例:")
        print("  python project_team/skills/init_existing_project.py ~/my-project")
        print("  python project_team/skills/init_existing_project.py .")
        sys.exit(1)

    project_path = sys.argv[1]

    # 验证路径存在
    if not Path(project_path).exists():
        print(f"❌ 项目路径不存在: {project_path}")
        sys.exit(1)

    # 执行分析
    analyzer = ExistingProjectAnalyzer(project_path)
    result = analyzer.analyze()

    # 退出代码
    if result.get('vibekit_result', {}).get('circular_dependencies') or \
       result.get('vibekit_result', {}).get('god_modules'):
        print("⚠️  项目存在架构问题，建议查看详细报告")
        sys.exit(1)  # 有问题，退出码为 1
    else:
        print("✅ 项目架构健康")
        sys.exit(0)  # 健康，退出码为 0


if __name__ == "__main__":
    main()