#!/usr/bin/env python3
"""
Product Competitor Analysis - 知识库更新脚本
Version: v1.0
Created: 2025-12-19

负责更新知识库的各个部分:
- 分析模块库 (81.94)
- 模式库 (81.90/81.91/81.92)
- 索引文件
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any

# 导入utils
from utils import (
    read_file,
    write_file,
    file_exists,
    ensure_directory_exists,
    get_today,
    KB_GROWTH_PATTERNS,
    KB_BUSINESS_MODELS,
    KB_TECH_MOATS,
    KB_ANALYSIS_MODULES,
)


# ==================== 模式库更新 ====================

class PatternLibraryUpdater:
    """模式库更新器"""

    def __init__(self, library_type: str):
        """
        初始化模式库更新器

        Args:
            library_type: 库类型 (growth/business/tech)
        """
        self.library_type = library_type

        # 确定文件路径
        if library_type == 'growth':
            self.file_path = KB_GROWTH_PATTERNS
        elif library_type == 'business':
            self.file_path = KB_BUSINESS_MODELS
        elif library_type == 'tech':
            self.file_path = KB_TECH_MOATS
        else:
            raise ValueError(f"未知的库类型: {library_type}")

        # 确保文件存在
        if not file_exists(self.file_path):
            self._create_initial_file()

        self.content = read_file(self.file_path)

    def _create_initial_file(self) -> None:
        """创建初始模式库文件"""
        if self.library_type == 'growth':
            title = "81.90 增长模式库"
            description = "记录各产品的增长模式、增长飞轮、AARRR策略等可复用模式"
        elif self.library_type == 'business':
            title = "81.91 商业模式总结"
            description = "记录各产品的商业模式、定价策略、变现路径等"
        else:  # tech
            title = "81.92 技术壁垒分析"
            description = "记录各产品的技术护城河、核心竞争力等"

        initial_content = f"""# {title}

> **说明**: {description}
> **更新时间**: {get_today()}
> **模式数量**: 0

## 模式列表

---

## 更新记录

- {get_today()}: 初始化文档
"""
        write_file(self.file_path, initial_content)

    def add_pattern(self, pattern_data: Dict[str, Any]) -> bool:
        """
        添加新模式

        Args:
            pattern_data: 模式数据，包含:
                - name: 模式名称
                - description: 模式描述
                - source_product: 来源产品
                - example: 示例
                - applicability: 适用场景

        Returns:
            是否成功添加（如果已存在则返回False）
        """
        # 检查模式是否已存在
        if self._pattern_exists(pattern_data['name']):
            return False

        # 构建模式条目
        pattern_entry = self._format_pattern_entry(pattern_data)

        # 插入到模式列表
        self._insert_pattern(pattern_entry)

        # 更新模式数量
        self._update_pattern_count()

        # 添加更新记录
        self._add_update_log(f"新增模式: {pattern_data['name']} (来自 {pattern_data['source_product']})")

        # 保存
        write_file(self.file_path, self.content)

        return True

    def _pattern_exists(self, pattern_name: str) -> bool:
        """检查模式是否已存在"""
        pattern = rf'###?\s+{re.escape(pattern_name)}'
        return bool(re.search(pattern, self.content))

    def _format_pattern_entry(self, data: Dict[str, Any]) -> str:
        """格式化模式条目"""
        entry = f"""
### {data['name']}

**来源产品**: [[{data['source_product']}]]

**模式描述**:
{data.get('description', '')}

**示例**:
{data.get('example', '')}

**适用场景**:
{data.get('applicability', '')}

**关键要素**:
{data.get('key_elements', '')}

---
"""
        return entry

    def _insert_pattern(self, pattern_entry: str) -> None:
        """插入模式到文档"""
        # 查找模式列表部分的结束位置
        pattern = r'(## 模式列表\n\n)(.*?)(---\n\n## 更新记录)'
        match = re.search(pattern, self.content, re.DOTALL)

        if match:
            # 插入到模式列表部分
            insert_pos = match.end(1) + len(match.group(2))
            self.content = self.content[:insert_pos] + pattern_entry + self.content[insert_pos:]
        else:
            # 如果找不到标准结构，追加到文件末尾
            self.content += "\n" + pattern_entry

    def _update_pattern_count(self) -> None:
        """更新模式数量"""
        # 统计模式数量（查找 ### 标题）
        count = len(re.findall(r'^### ', self.content, re.MULTILINE))

        # 更新元数据
        self.content = re.sub(
            r'(>\s*\*\*模式数量\*\*:\s*)\d+',
            rf'\g<1>{count}',
            self.content
        )

        # 更新更新时间
        self.content = re.sub(
            r'(>\s*\*\*更新时间\*\*:\s*)\d{4}-\d{2}-\d{2}',
            rf'\g<1>{get_today()}',
            self.content
        )

    def _add_update_log(self, message: str) -> None:
        """添加更新记录"""
        log_pattern = r'(## 更新记录\n\n)'
        match = re.search(log_pattern, self.content)

        if match:
            log_entry = f"- {get_today()}: {message}\n"
            insert_pos = match.end()
            self.content = self.content[:insert_pos] + log_entry + self.content[insert_pos:]


# ==================== 分析模块库更新 ====================

class AnalysisModuleUpdater:
    """分析模块库更新器"""

    def __init__(self):
        """初始化分析模块库更新器"""
        self.base_dir = KB_ANALYSIS_MODULES
        ensure_directory_exists(self.base_dir)

        # 确保各个维度目录存在
        self.dimensions = ['增长飞轮', 'Aha Moment', '商业化策略', '数据飞轮', '用户价值', '产品定位']
        for dim in self.dimensions:
            ensure_directory_exists(self.base_dir / dim)

    def save_module(self, dimension: str, product_name: str, content: str) -> Path:
        """
        保存分析模块

        Args:
            dimension: 维度名称（如"增长飞轮"）
            product_name: 产品名称
            content: 模块内容

        Returns:
            保存的文件路径
        """
        if dimension not in self.dimensions:
            raise ValueError(f"未知维度: {dimension}，支持的维度: {self.dimensions}")

        # 构建文件名
        filename = f"{product_name}_{dimension}.md"
        file_path = self.base_dir / dimension / filename

        # 添加元数据
        full_content = f"""# {product_name} - {dimension}分析

> **提取时间**: {get_today()}
> **来源**: [[{product_name} 产品分析]]

---

{content}

---

*此模块已保存到分析模块库，可在其他分析中引用*
"""

        # 保存文件
        write_file(file_path, full_content)

        return file_path


# ==================== 辅助函数 ====================
def add_growth_pattern(pattern_data: Dict[str, Any]) -> bool:
    """
    添加增长模式

    Args:
        pattern_data: 模式数据

    Returns:
        是否成功添加
    """
    updater = PatternLibraryUpdater('growth')
    success = updater.add_pattern(pattern_data)

    if success:
        print(f"✅ 已添加增长模式: {pattern_data['name']}")
    else:
        print(f"⚠️ 增长模式已存在: {pattern_data['name']}")

    return success


def add_business_model(model_data: Dict[str, Any]) -> bool:
    """
    添加商业模式

    Args:
        model_data: 模式数据

    Returns:
        是否成功添加
    """
    updater = PatternLibraryUpdater('business')
    success = updater.add_pattern(model_data)

    if success:
        print(f"✅ 已添加商业模式: {model_data['name']}")
    else:
        print(f"⚠️ 商业模式已存在: {model_data['name']}")

    return success


def add_tech_moat(moat_data: Dict[str, Any]) -> bool:
    """
    添加技术壁垒

    Args:
        moat_data: 模式数据

    Returns:
        是否成功添加
    """
    updater = PatternLibraryUpdater('tech')
    success = updater.add_pattern(moat_data)

    if success:
        print(f"✅ 已添加技术壁垒: {moat_data['name']}")
    else:
        print(f"⚠️ 技术壁垒已存在: {moat_data['name']}")

    return success


def save_analysis_module(dimension: str, product_name: str, content: str) -> Path:
    """
    保存分析模块

    Args:
        dimension: 维度名称
        product_name: 产品名称
        content: 模块内容

    Returns:
        保存的文件路径
    """
    updater = AnalysisModuleUpdater()
    file_path = updater.save_module(dimension, product_name, content)
    print(f"✅ 已保存分析模块: {file_path.name}")

    return file_path


# ==================== CLI接口 ====================

def main():
    """CLI主函数"""
    import argparse
    import json

    parser = argparse.ArgumentParser(description='知识库更新工具')

    subparsers = parser.add_subparsers(dest='command', help='子命令')

    # 模式库更新命令
    pattern_parser = subparsers.add_parser('pattern', help='添加模式')
    pattern_parser.add_argument('--type', required=True, choices=['growth', 'business', 'tech'], help='模式类型')
    pattern_parser.add_argument('--data', required=True, help='模式数据（JSON格式）')

    # 分析模块保存命令
    module_parser = subparsers.add_parser('module', help='保存分析模块')
    module_parser.add_argument('--dimension', required=True, help='维度名称')
    module_parser.add_argument('--product', required=True, help='产品名称')
    module_parser.add_argument('--content', required=True, help='模块内容')

    args = parser.parse_args()

    if args.command == 'pattern':
        # 添加模式
        data = json.loads(args.data)

        if args.type == 'growth':
            add_growth_pattern(data)
        elif args.type == 'business':
            add_business_model(data)
        elif args.type == 'tech':
            add_tech_moat(data)

    elif args.command == 'module':
        # 保存分析模块
        save_analysis_module(args.dimension, args.product, args.content)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
