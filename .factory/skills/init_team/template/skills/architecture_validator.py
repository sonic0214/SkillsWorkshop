#!/usr/bin/env python3
"""
VibeKit - architecture_validator.py

架构违规检测器 - 检测跨层调用和反向依赖

功能：
- 读取 .vibekit.yaml 配置文件
- 映射模块到架构层
- 检测跨层调用（跳过中间层）
- 检测反向依赖（底层依赖上层）
- 生成违规报告

使用：
    validator = ArchitectureValidator('.vibekit.yaml')
    violations = validator.validate(dependency_graph, modules)
"""

import yaml
import re
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple


class ArchitectureConfig:
    """架构配置"""

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config = {}
        self.layers = []
        self.rules = []
        self.ignore = []

        if self.config_path.exists():
            self._load_config()

    def _load_config(self):
        """加载配置文件"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        arch = self.config.get('architecture', {})
        self.layers = arch.get('layers', [])
        self.rules = arch.get('rules', [])
        self.ignore = self.config.get('ignore', [])

        # 按 level 排序（从高到低）
        self.layers.sort(key=lambda x: x.get('level', 0), reverse=True)

    def is_configured(self) -> bool:
        """是否有配置文件"""
        return bool(self.layers)

    def get_layer_by_module(self, module_name: str, module_path: str) -> Optional[Dict]:
        """根据模块名和路径，找到对应的层"""
        for layer in self.layers:
            patterns = layer.get('patterns', [])

            for pattern in patterns:
                # 简单的模式匹配
                # 支持：auth/**, **/services/**, database
                if self._match_pattern(module_name, module_path, pattern):
                    return layer

        return None

    def _match_pattern(self, module_name: str, module_path: str, pattern: str) -> bool:
        """模式匹配"""
        # 完全匹配模块名
        if pattern == module_name:
            return True

        # 路径匹配
        if '**' in pattern:
            # auth/** 匹配 auth/service.py
            prefix = pattern.replace('/**', '')
            if module_path.startswith(prefix):
                return True

        # **/services/** 匹配任何包含 services 的路径
        if pattern.startswith('**/') and pattern.endswith('/**'):
            keyword = pattern.replace('**/', '').replace('/**', '')
            if keyword in module_path:
                return True

        # **/service.py 匹配任何以 service.py 结尾的文件
        if pattern.startswith('**/'):
            suffix = pattern.replace('**/', '')
            if module_path.endswith(suffix):
                return True

        return False


class ArchitectureValidator:
    """架构违规检测器"""

    def __init__(self, config_path: str):
        self.config = ArchitectureConfig(config_path)
        self.violations = []
        self.module_to_layer = {}

    def validate(self, dependency_graph: Dict[str, Set[str]], modules: List[Dict]) -> List[Dict]:
        """验证架构规则

        Args:
            dependency_graph: 依赖图 {module_name: set of dependencies}
            modules: 模块列表 [{name, path, type}]

        Returns:
            violations: 违规列表
        """
        if not self.config.is_configured():
            return []

        print("🏗️  验证架构规则...")

        # 1. 映射模块到层
        self.module_to_layer = self._map_modules_to_layers(modules)

        if not self.module_to_layer:
            print("   ⚠️  未能映射任何模块到架构层")
            return []

        print(f"   映射了 {len(self.module_to_layer)}/{len(modules)} 个模块到架构层")

        # 2. 检测跨层调用
        skip_layer_violations = self._detect_skip_layer(dependency_graph)

        # 3. 检测反向依赖
        reverse_dep_violations = self._detect_reverse_dependency(dependency_graph)

        self.violations = skip_layer_violations + reverse_dep_violations

        if self.violations:
            print(f"   ⚠️  发现 {len(self.violations)} 处架构违规！")
        else:
            print(f"   ✅ 未发现架构违规")

        return self.violations

    def _map_modules_to_layers(self, modules: List[Dict]) -> Dict[str, Dict]:
        """映射模块到层"""
        module_to_layer = {}

        for module in modules:
            module_name = module['name']
            module_path = module['path']

            layer = self.config.get_layer_by_module(module_name, module_path)

            if layer:
                module_to_layer[module_name] = {
                    'name': layer['name'],
                    'level': layer['level'],
                    'description': layer.get('description', '')
                }

        return module_to_layer

    def _detect_skip_layer(self, graph: Dict[str, Set[str]]) -> List[Dict]:
        """检测跨层调用

        示例：api (level 4) → database (level 1)
        跳过了 service (level 3) 和 repository (level 2)
        """
        violations = []

        for module, deps in graph.items():
            module_layer = self.module_to_layer.get(module)
            if not module_layer:
                continue

            for dep in deps:
                dep_layer = self.module_to_layer.get(dep)
                if not dep_layer:
                    continue

                # 计算层级差
                layer_diff = module_layer['level'] - dep_layer['level']

                # 如果跨越 > 1 层，就是跨层调用
                if layer_diff > 1:
                    skipped_layers = self._get_skipped_layers(
                        module_layer['level'],
                        dep_layer['level']
                    )

                    violations.append({
                        'type': 'skip_layer',
                        'severity': 'P0',
                        'from_module': module,
                        'from_layer': module_layer['name'],
                        'from_level': module_layer['level'],
                        'to_module': dep,
                        'to_layer': dep_layer['name'],
                        'to_level': dep_layer['level'],
                        'layer_diff': layer_diff,
                        'skipped_layers': skipped_layers
                    })

        return violations

    def _detect_reverse_dependency(self, graph: Dict[str, Set[str]]) -> List[Dict]:
        """检测反向依赖

        示例：database (level 1) → api (level 4)
        底层依赖了上层，违反分层原则
        """
        violations = []

        for module, deps in graph.items():
            module_layer = self.module_to_layer.get(module)
            if not module_layer:
                continue

            for dep in deps:
                dep_layer = self.module_to_layer.get(dep)
                if not dep_layer:
                    continue

                # 如果依赖的层级更高，就是反向依赖
                if dep_layer['level'] > module_layer['level']:
                    violations.append({
                        'type': 'reverse_dependency',
                        'severity': 'P0',
                        'from_module': module,
                        'from_layer': module_layer['name'],
                        'from_level': module_layer['level'],
                        'to_module': dep,
                        'to_layer': dep_layer['name'],
                        'to_level': dep_layer['level'],
                        'direction': f"{module_layer['name']} (L{module_layer['level']}) → {dep_layer['name']} (L{dep_layer['level']})"
                    })

        return violations

    def _get_skipped_layers(self, from_level: int, to_level: int) -> List[str]:
        """获取跳过的层"""
        skipped = []

        for layer in self.config.layers:
            level = layer['level']
            if to_level < level < from_level:
                skipped.append(layer['name'])

        return skipped

    def get_layer_mapping_summary(self) -> Dict:
        """获取层映射摘要（用于报告）"""
        summary = {}

        for module, layer_info in self.module_to_layer.items():
            layer_name = layer_info['name']
            if layer_name not in summary:
                summary[layer_name] = []
            summary[layer_name].append(module)

        return summary


def create_default_config(project_path: str):
    """创建默认的 .vibekit.yaml 配置文件"""
    config_path = Path(project_path) / '.vibekit.yaml'

    if config_path.exists():
        print(f"   配置文件已存在：{config_path}")
        return str(config_path)

    default_config = """# VibeKit 架构配置文件
# 用于检测架构违规：跨层调用、反向依赖等

architecture:
  type: layered  # 分层架构

  # 定义架构层（从上到下）
  layers:
    # API 层 - 路由、控制器
    - name: api
      level: 4  # 最上层
      description: "API 层 - 路由和控制器"
      patterns:
        - "api"
        - "api/**"
        - "**/routes/**"
        - "**/controllers/**"

    # 服务层 - 业务逻辑
    - name: service
      level: 3
      description: "业务逻辑层"
      patterns:
        - "service"
        - "service/**"
        - "**/services/**"

    # 数据访问层 - Repository/Model
    - name: repository
      level: 2
      description: "数据访问层"
      patterns:
        - "repository"
        - "repository/**"
        - "**/repositories/**"
        - "**/models/**"
        - "user"  # 示例：user 模块属于 repository 层
        - "order"
        - "payment"

    # 数据库层 - 连接、查询
    - name: database
      level: 1  # 最底层
      description: "数据库层"
      patterns:
        - "database"
        - "database/**"
        - "**/db/**"
        - "**/connection.py"

  # 架构规则
  rules:
    # 只能依赖同层或下层
    - type: layer_dependency
      description: "上层可以依赖下层，下层不能依赖上层"

    # 禁止跨层调用
    - type: no_skip_layer
      description: "不能跨层调用（如 API 直接访问 DB）"
      allow_skip: false  # 严格模式

# 忽略的目录/模块
ignore:
  - tests
  - test
  - migrations
  - __pycache__
  - .git
  - venv
  - env

# 说明：
# 1. level 数字越大，层级越高
# 2. patterns 支持：
#    - 完全匹配：api, database
#    - 目录匹配：api/**, database/**
#    - 包含匹配：**/services/**, **/models/**
#    - 文件匹配：**/connection.py
# 3. 架构违规检测：
#    - 跨层调用：api → database (跳过 service, repository)
#    - 反向依赖：database → api (底层依赖上层)
"""

    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(default_config)

    print(f"   ✅ 创建默认配置：{config_path}")
    return str(config_path)


if __name__ == "__main__":
    # 测试
    import sys

    if len(sys.argv) < 2:
        print("用法：python architecture_validator.py <项目路径>")
        sys.exit(1)

    project_path = sys.argv[1]

    # 创建默认配置
    config_path = create_default_config(project_path)

    print(f"\n配置文件已创建：{config_path}")
    print("\n请根据您的项目架构修改配置文件，然后运行：")
    print(f"  python analyze_existing_project.py {project_path}")
