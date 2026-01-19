#!/usr/bin/env python3
"""
Product Competitor Analysis - 分析生成脚本
Version: v1.0
Created: 2025-12-19

基于GOSPEL框架生成产品分析报告。
采用统一分析流程，可按模块选择输出内容。
"""

from pathlib import Path
from typing import Dict, List, Optional, Any

# 导入utils和collect_data
from utils import (
    load_gospel_config,
    load_expert_prompts,
    load_template,
    fill_template,
    get_today,
    get_product_document_path,
    write_file,
)
from collect_data import DataCollector


# ==================== 分析生成器类 ====================

class AnalysisGenerator:
    """
    分析生成器

    基于GOSPEL框架生成结构化的产品分析
    """

    MODULE_MAP = {
        "增长系统": "G",
        "市场机会": "O",
        "战略定位": "S",
        "竞品分析": "C",
        "产品设计": "P",
        "商业模式": "E",
        "洞察提炼": "L",
        "G": "G",
        "O": "O",
        "S": "S",
        "C": "C",
        "P": "P",
        "E": "E",
        "L": "L",
    }
    TEMPLATE_ALIASES = {
        "1": "分析模板",
        "v1": "分析模板",
        "v1.0": "分析模板",
        "templatev1.0": "分析模板",
        "templatev1.0.md": "分析模板",
        "2": "分析模板 v2.0",
        "v2": "分析模板 v2.0",
        "v2.0": "分析模板 v2.0",
        "templatev2.0": "分析模板 v2.0",
        "templatev2.0.md": "分析模板 v2.0",
    }
    DEFAULT_TEMPLATE_VERSION = "v1.0"

    def __init__(
        self,
        product_name: str,
        modules: Optional[List[str]] = None,
        template_version: Optional[str] = None,
    ):
        """
        初始化分析生成器

        Args:
            product_name: 产品名称
            modules: 模块列表（增长系统/市场机会/战略定位/产品设计/商业模式）
            template_version: 模板版本（v1.0/v2.0 或 模板名称）
        """
        self.product_name = product_name

        # 加载配置
        self.gospel_config = load_gospel_config()
        self.expert_prompts = load_expert_prompts()

        # 获取分析配置
        self.mode_config = self.gospel_config['analysis_modes']['standard']
        self.modules = self._normalize_modules(modules)

        # 分析结果存储
        self.analysis_results = {
            'product_name': product_name,
            'analysis_date': get_today(),
            'modules': self.modules,
            'dimensions': {}
        }

        self.template_version = template_version or self.DEFAULT_TEMPLATE_VERSION
        self.template_name = self._resolve_template_name(self.template_version)

        # 加载数据
        self.data_collector = DataCollector.load_existing(product_name)

    def _resolve_template_name(self, template_version: str) -> str:
        """
        将模板版本映射到模板名称
        """
        version = (template_version or "").strip()
        if not version:
            version = self.DEFAULT_TEMPLATE_VERSION

        normalized = version.lower()
        return self.TEMPLATE_ALIASES.get(normalized, version)

    def get_template(self) -> str:
        """
        获取模板内容（优先加载模板文件，不存在则回退内置模板）
        """
        try:
            return load_template(self.template_name)
        except ValueError:
            return self._get_builtin_template()

    def get_required_dimensions(self) -> List[str]:
        """
        获取需要分析的维度

        Returns:
            维度代码列表，如 ['G', 'O', 'S', 'P', 'E', 'L']
        """
        dimensions = list(self.modules)
        if "L" not in dimensions:
            dimensions.append("L")
        return dimensions

    def _normalize_modules(self, modules: Optional[List[str]]) -> List[str]:
        """
        规范化模块输入，返回维度代码列表
        """
        if not modules:
            default_dims = [dim for dim in self.mode_config['dimensions'] if dim != "L"]
            return default_dims

        normalized = []
        for module in modules:
            key = module.strip()
            if not key:
                continue
            mapped = self.MODULE_MAP.get(key)
            if not mapped:
                mapped = self.MODULE_MAP.get(key.upper())
            if not mapped:
                raise ValueError(f"未知模块: {module}")
            normalized.append(mapped)

        # 去重保序
        seen = set()
        ordered = []
        for dim in normalized:
            if dim not in seen:
                seen.add(dim)
                ordered.append(dim)

        return ordered

    def _format_modules_label(self, dimensions: List[str]) -> str:
        """
        输出模块名称标签
        """
        labels = []
        for dim in dimensions:
            config = self.get_dimension_config(dim)
            labels.append(config['name_cn'])
        return " / ".join(labels)

    def get_dimension_config(self, dimension: str) -> Dict[str, Any]:
        """
        获取指定维度的配置

        Args:
            dimension: 维度代码 (G/O/S/P/E/L)

        Returns:
            维度配置字典
        """
        return self.gospel_config['dimensions'][dimension]

    def create_dimension_framework(self, dimension: str) -> Dict[str, Any]:
        """
        创建维度分析框架

        Args:
            dimension: 维度代码

        Returns:
            维度分析框架（包含所有需要分析的子维度和数据点）
        """
        config = self.get_dimension_config(dimension)

        framework = {
            'dimension': dimension,
            'name': config['name'],
            'name_cn': config['name_cn'],
            'sub_dimensions': {},
            'data_sources': config.get('data_sources', {}),
            'analysis_points': []
        }

        # 提取子维度
        for sub_dim in config.get('sub_dimensions', []):
            for key, value in sub_dim.items():
                framework['sub_dimensions'][key] = value

        return framework

    def generate_analysis_framework(self) -> Dict[str, Any]:
        """
        生成完整的分析框架

        Returns:
            包含所有维度框架的字典
        """
        required_dims = self.get_required_dimensions()
        framework = {}

        for dim in required_dims:
            framework[dim] = self.create_dimension_framework(dim)

        return framework

    def add_dimension_analysis(self, dimension: str, analysis: Dict[str, Any]) -> None:
        """
        添加维度分析结果

        Args:
            dimension: 维度代码
            analysis: 分析结果字典
        """
        self.analysis_results['dimensions'][dimension] = analysis

    def get_expert_prompt(self, expert_name: str, context: Dict[str, Any]) -> str:
        """
        获取专家分析Prompt

        Args:
            expert_name: 专家代号 (yujun/liangning/andrew_chen/zengming/lishangyou)
            context: 分析上下文（包含已完成的维度分析）

        Returns:
            完整的专家prompt
        """
        if expert_name not in self.expert_prompts['experts']:
            raise ValueError(f"未知专家: {expert_name}")

        expert = self.expert_prompts['experts'][expert_name]

        # 构建上下文字符串
        context_str = f"""
## 产品信息：
- 产品名称：{self.product_name}
- 分析日期：{get_today()}

## 已完成的分析：
"""

        # 添加各维度分析摘要
        for dim, result in context.items():
            if isinstance(result, dict):
                context_str += f"\n### {dim}:\n"
                context_str += self._format_analysis_summary(result)

        # 组合prompt
        full_prompt = f"""{expert['prompt']}

{context_str}

请基于上述框架对{self.product_name}进行分析。
"""

        return full_prompt

    def _format_analysis_summary(self, analysis: Dict[str, Any], indent: int = 0) -> str:
        """
        格式化分析摘要

        Args:
            analysis: 分析字典
            indent: 缩进级别

        Returns:
            格式化的字符串
        """
        result = ""
        indent_str = "  " * indent

        for key, value in analysis.items():
            if isinstance(value, dict):
                result += f"{indent_str}- {key}:\n"
                result += self._format_analysis_summary(value, indent + 1)
            elif isinstance(value, list):
                result += f"{indent_str}- {key}:\n"
                for item in value:
                    result += f"{indent_str}  - {item}\n"
            else:
                result += f"{indent_str}- {key}: {value}\n"

        return result

    def generate_expert_insights_prompts(self) -> Dict[str, str]:
        """
        生成所有专家的分析prompts

        Returns:
            {expert_name: prompt} 字典
        """
        # 准备上下文（当前已完成的分析）
        context = self.analysis_results['dimensions']

        # 专家召集顺序（从配置获取）
        expert_order = ['yujun', 'liangning', 'andrew_chen', 'zengming', 'lishangyou']

        prompts = {}
        for expert_name in expert_order:
            prompts[expert_name] = self.get_expert_prompt(expert_name, context)

        return prompts

    def create_analysis_document(self, expert_insights: Optional[Dict[str, str]] = None) -> str:
        """
        创建分析文档

        Args:
            expert_insights: 专家洞察字典（可选）

        Returns:
            完整的Markdown文档
        """
        # 选择模板
        template = self.get_template()

        # 准备变量
        variables = {
            'product_name': self.product_name,
            'analysis_date': get_today(),
            'analysis_modules': self._format_modules_label(self.get_required_dimensions()),
        }

        # 添加各维度分析
        for dim, analysis in self.analysis_results['dimensions'].items():
            dim_config = self.get_dimension_config(dim)
            variables[f'{dim}_name'] = dim_config['name_cn']
            variables[f'{dim}_content'] = self._format_dimension_content(analysis)

        # 补齐未提供的模块占位
        for dim in self.mode_config['dimensions']:
            dim_config = self.get_dimension_config(dim)
            variables.setdefault(f'{dim}_name', dim_config['name_cn'])
            variables.setdefault(f'{dim}_content', "")

        # 添加专家洞察（如提供）
        if expert_insights:
            for expert_name, insight in expert_insights.items():
                expert = self.expert_prompts['experts'][expert_name]
                variables[f'{expert_name}_name'] = expert['name']
                variables[f'{expert_name}_content'] = insight
        else:
            for expert_name, expert in self.expert_prompts.get('experts', {}).items():
                variables.setdefault(f'{expert_name}_name', expert.get('name', expert_name))
                variables.setdefault(f'{expert_name}_content', "")

        # 填充模板
        document = fill_template(template, variables)

        return document

    def _format_dimension_content(self, analysis: Dict[str, Any]) -> str:
        """
        格式化维度内容为Markdown

        Args:
            analysis: 维度分析字典

        Returns:
            Markdown格式的内容
        """
        content = ""

        for key, value in analysis.items():
            if isinstance(value, dict):
                content += f"\n### {key}\n\n"
                content += self._format_analysis_summary(value)
            elif isinstance(value, list):
                content += f"\n### {key}\n\n"
                for item in value:
                    content += f"- {item}\n"
            else:
                content += f"\n**{key}**: {value}\n\n"

        return content

    def _get_builtin_template(self) -> str:
        """
        获取内置模板（如果外部模板不可用）

        Returns:
            模板字符串
        """
        return """# {product_name} 产品分析

> **分析日期**: {analysis_date}
> **分析模块**: {analysis_modules}

## 一句话总结

[待填充]

## Part G: {G_name}

{G_content}

## Part O: {O_name}

{O_content}

## Part S: {S_name}

{S_content}

## Part C: {C_name}

{C_content}

## Part P: {P_name}

{P_content}

## Part E: {E_name}

{E_content}

## Part L: {L_name}

### 俞军视角: {yujun_name}

{yujun_content}

### 梁宁视角: {liangning_name}

{liangning_content}

### Andrew Chen视角: {andrew_chen_name}

{andrew_chen_content}

### 曾鸣视角: {zengming_name}

{zengming_content}

### 李善友视角: {lishangyou_name}

{lishangyou_content}

### 综合洞察

[待填充]

## 可复用模式识别

[待填充]

## 数据来源

[待填充]
"""

    def save_analysis(self, document_content: str, document_number: Optional[int] = None) -> Path:
        """
        保存分析文档

        Args:
            document_content: 文档内容
            document_number: 文档编号（可选）

        Returns:
            保存的文件路径
        """
        file_path = get_product_document_path(self.product_name, document_number)
        write_file(file_path, document_content)

        return file_path


# ==================== 分析辅助函数 ====================

def create_analysis_framework(product_name: str, modules: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    创建分析框架

    Args:
        product_name: 产品名称
        modules: 模块列表（可选）

    Returns:
        分析框架
    """
    generator = AnalysisGenerator(product_name, modules=modules)
    return generator.generate_analysis_framework()


def get_all_expert_prompts(product_name: str, current_analysis: Dict[str, Any]) -> Dict[str, str]:
    """
    获取所有专家的分析prompts

    Args:
        product_name: 产品名称
        current_analysis: 当前已完成的分析

    Returns:
        {expert_name: prompt} 字典
    """
    generator = AnalysisGenerator(product_name)
    generator.analysis_results['dimensions'] = current_analysis

    return generator.generate_expert_insights_prompts()


def generate_analysis_report(
    product_name: str,
    dimension_analyses: Dict[str, Any],
    expert_insights: Optional[Dict[str, str]] = None,
    document_number: Optional[int] = None,
    modules: Optional[List[str]] = None,
    template_version: Optional[str] = None,
) -> Path:
    """
    生成完整的分析报告

    Args:
        product_name: 产品名称
        dimension_analyses: 各维度的分析结果
        expert_insights: 专家洞察（可选）
        document_number: 文档编号
        modules: 模块列表（可选）
        template_version: 模板版本（可选）

    Returns:
        保存的文件路径
    """
    generator = AnalysisGenerator(product_name, modules=modules, template_version=template_version)

    # 添加维度分析
    for dim, analysis in dimension_analyses.items():
        generator.add_dimension_analysis(dim, analysis)

    # 创建文档
    document = generator.create_analysis_document(expert_insights)

    # 保存文档
    file_path = generator.save_analysis(document, document_number)

    return file_path


# ==================== CLI接口 ====================

def main():
    """CLI主函数"""
    import argparse
    import json

    parser = argparse.ArgumentParser(description='产品分析生成工具')
    parser.add_argument('product', help='产品名称')
    parser.add_argument('--modules', help='分析模块，逗号分隔（增长系统,市场机会,战略定位,竞品分析,产品设计,商业模式）')
    parser.add_argument('--framework', action='store_true', help='显示分析框架')
    parser.add_argument('--prompts', action='store_true', help='生成专家prompts')
    parser.add_argument('--template', '--show-template', dest='show_template', action='store_true', help='显示文档模板')
    parser.add_argument('--template-version', help='模板版本（v1.0/v2.0 或 模板名称）')

    args = parser.parse_args()
    modules = []
    if args.modules:
        import re
        modules = [m.strip() for m in re.split(r'[，,、]', args.modules) if m.strip()]

    if args.framework:
        # 显示分析框架
        framework = create_analysis_framework(args.product, modules=modules or None)
        print(f"\n=== {args.product} 分析框架 ===\n")
        print(json.dumps(framework, ensure_ascii=False, indent=2))

    elif args.prompts:
        # 生成专家prompts
        generator = AnalysisGenerator(args.product, modules=modules or None, template_version=args.template_version)
        prompts = generator.generate_expert_insights_prompts()

        print(f"\n=== {args.product} 专家分析Prompts ===\n")
        for expert_name, prompt in prompts.items():
            expert = generator.expert_prompts['experts'][expert_name]
            print(f"\n## {expert['name']} ({expert_name})\n")
            print(prompt)
            print("\n" + "="*80 + "\n")

    elif args.show_template:
        # 显示文档模板
        generator = AnalysisGenerator(args.product, modules=modules or None, template_version=args.template_version)
        template = generator.get_template()

        print(f"\n=== {args.product} 文档模板 ===\n")
        print(template)

    else:
        # 创建分析生成器
        generator = AnalysisGenerator(args.product, modules=modules or None, template_version=args.template_version)
        print(f"\n✅ 已为 {args.product} 创建分析生成器")
        print(f"分析模块: {generator._format_modules_label(generator.get_required_dimensions())}")
        print(f"需要分析的维度: {generator.get_required_dimensions()}")
        print(f"模板版本: {generator.template_version}（{generator.template_name}）")
        print("\n使用 --framework 查看分析框架")
        print("使用 --prompts 生成专家prompts")
        print("使用 --template-version 选择模板版本")
        print("使用 --show-template 查看文档模板")


if __name__ == "__main__":
    main()
