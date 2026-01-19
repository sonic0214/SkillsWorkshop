#!/usr/bin/env python3
"""
Product Competitor Analysis - 工具函数库
Version: v1.0
Created: 2025-12-19

提供基础功能支持，包括文件操作、数据处理、配置加载等。
"""

import os
import re
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import glob as glob_module


# ==================== 路径配置 ====================

# 获取skill根目录
SKILL_ROOT = Path(__file__).parent.parent
KNOWLEDGE_BASE_ROOT = Path("/Users/admin/KnowledgeSystem/80-89 项目·专题/81 AI产品研究")

# 配置文件路径
CONFIG_DIR = SKILL_ROOT / "config"
GOSPEL_CONFIG = CONFIG_DIR / "gospel_framework.yaml"
ANALYSIS_CONFIG = CONFIG_DIR / "analysis_config.yaml"
EXPERT_PROMPTS_CONFIG = CONFIG_DIR / "ai_expert_prompts.yaml"

# 模板文件
TEMPLATE_FILE_MAP = {
    "分析模板": SKILL_ROOT / "templatev1.0.md",
    "分析模板 v2.0": SKILL_ROOT / "templatev2.0.md",
}
FRAMEWORK_FILE = SKILL_ROOT / "FRAMEWORK.md"

# 知识库路径
KB_MAIN_DOCS = KNOWLEDGE_BASE_ROOT
KB_RAW_MATERIALS = KNOWLEDGE_BASE_ROOT / "81.93 竞品资料库"
KB_ANALYSIS_MODULES = KNOWLEDGE_BASE_ROOT / "81.94 分析模块库"
KB_GROWTH_PATTERNS = KNOWLEDGE_BASE_ROOT / "81.90 增长模式库.md"
KB_BUSINESS_MODELS = KNOWLEDGE_BASE_ROOT / "81.91 商业模式总结.md"
KB_TECH_MOATS = KNOWLEDGE_BASE_ROOT / "81.92 技术壁垒分析.md"


# ==================== 文件操作 ====================

def file_exists(file_path: Union[str, Path]) -> bool:
    """检查文件是否存在"""
    return Path(file_path).exists()


def read_file(file_path: Union[str, Path], encoding: str = 'utf-8') -> str:
    """读取文件内容"""
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return f.read()
    except Exception as e:
        raise Exception(f"读取文件失败 {file_path}: {str(e)}")


def write_file(file_path: Union[str, Path], content: str, encoding: str = 'utf-8') -> None:
    """写入文件内容"""
    try:
        file_path = Path(file_path)
        # 确保目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
    except Exception as e:
        raise Exception(f"写入文件失败 {file_path}: {str(e)}")


def append_to_file(file_path: Union[str, Path], content: str, encoding: str = 'utf-8') -> None:
    """追加内容到文件末尾"""
    try:
        with open(file_path, 'a', encoding=encoding) as f:
            f.write(content)
    except Exception as e:
        raise Exception(f"追加文件失败 {file_path}: {str(e)}")


def save_file(file_path: Union[str, Path], content: Union[str, dict], encoding: str = 'utf-8') -> None:
    """
    保存文件（智能判断类型）
    - 如果content是dict且文件是.json，保存为JSON
    - 否则保存为文本
    """
    file_path = Path(file_path)

    if isinstance(content, dict) and file_path.suffix == '.json':
        save_json(file_path, content)
    else:
        write_file(file_path, content, encoding)


def save_json(file_path: Union[str, Path], data: dict, indent: int = 2) -> None:
    """保存JSON文件"""
    try:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=indent)
    except Exception as e:
        raise Exception(f"保存JSON失败 {file_path}: {str(e)}")


def load_json(file_path: Union[str, Path]) -> dict:
    """加载JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"加载JSON失败 {file_path}: {str(e)}")


# ==================== YAML配置加载 ====================

def load_yaml(file_path: Union[str, Path]) -> dict:
    """加载YAML配置文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise Exception(f"加载YAML失败 {file_path}: {str(e)}")


def load_gospel_config() -> dict:
    """加载GOSPEL框架配置"""
    return load_yaml(GOSPEL_CONFIG)


def load_analysis_config() -> dict:
    """加载分析配置"""
    return load_yaml(ANALYSIS_CONFIG)


def load_expert_prompts() -> dict:
    """加载专家Prompt配置"""
    return load_yaml(EXPERT_PROMPTS_CONFIG)


def load_yaml_config(filename: str) -> dict:
    """从config目录加载YAML配置"""
    return load_yaml(CONFIG_DIR / filename)


def load_markdown_file(file_path: Union[str, Path]) -> str:
    """加载Markdown文件"""
    return read_file(file_path)


# ==================== 模板加载 ====================

def load_template(template_name: str) -> str:
    """
    从模板文件加载指定模板

    Args:
        template_name: 模板名称，如 "分析模板"

    Returns:
        模板内容
    """
    if not template_name:
        raise ValueError("模板名称不能为空")

    template_file = TEMPLATE_FILE_MAP.get(template_name)
    if not template_file:
        candidate = SKILL_ROOT / template_name
        if candidate.exists():
            template_file = candidate

    if not template_file or not template_file.exists():
        raise ValueError(f"未找到模板: {template_name}")

    content = read_file(template_file).strip()
    if not content:
        raise ValueError(f"模板内容为空: {template_name}")

    # 移除可选的模板标题行
    lines = content.splitlines()
    if lines and lines[0].strip() == f"## {template_name}":
        content = "\n".join(lines[1:]).lstrip()

    # 若模板包含代码块，优先取第一个代码块内容
    fenced_match = re.search(r"```[^\n]*\n(.*?)\n```", content, re.DOTALL)
    if fenced_match:
        return fenced_match.group(1).strip()

    return content.strip()


def fill_template(template: str, variables: Dict[str, Any]) -> str:
    """
    填充模板变量

    Args:
        template: 模板内容
        variables: 变量字典，如 {'product_name': 'ChatGPT', 'date': '2025-12-19'}

    Returns:
        填充后的内容
    """
    result = template

    for key, value in variables.items():
        # 处理None值
        if value is None:
            value = ""

        # 转换为字符串
        if not isinstance(value, str):
            value = str(value)

        # 替换所有占位符格式: {key}, {{key}}, [key]
        patterns = [
            (f"{{{key}}}", value),
            (f"{{{{{key}}}}}", value),
            (f"[{key}]", value),
        ]

        for pattern, replacement in patterns:
            result = result.replace(pattern, replacement)

    return result


# ==================== 数据提取 ====================

def extract_number(file_path: str) -> int:
    """
    从文件路径中提取编号
    例如: "81.13 Base44.md" -> 13
    """
    match = re.search(r'81\.(\d+)', file_path)
    if match:
        return int(match.group(1))
    return 0


def extract_product_names(user_request: str) -> List[str]:
    """
    从用户请求中提取产品名称列表

    支持格式:
    - "对比 ChatGPT、Claude、Gemini"
    - "分析 Notion vs Obsidian"
    """
    products = []

    # 移除常见的触发词
    text = user_request
    for keyword in ['对比', '比较', '分析', 'vs', 'versus', '：', ':']:
        text = text.replace(keyword, ' ')

    # 按分隔符分割
    separators = ['、', '，', ',', '和', ' ']
    for sep in separators:
        if sep in text:
            parts = text.split(sep)
            products.extend([p.strip() for p in parts if p.strip()])
            break

    # 如果没有分隔符，可能是单个产品名或用空格分隔
    if not products:
        products = [p.strip() for p in text.split() if p.strip() and len(p.strip()) > 1]

    # 去重并过滤
    products = list(set(products))

    # 过滤掉过短的（可能是噪音）
    products = [p for p in products if len(p) >= 2]

    return products


def get_existing_files(pattern: str) -> List[Path]:
    """
    获取符合模式的现有文件

    Args:
        pattern: glob模式，如 "81.*.md"
    """
    search_path = KB_MAIN_DOCS / pattern
    return [Path(p) for p in glob_module.glob(str(search_path))]


def get_max_document_number() -> int:
    """
    获取当前知识库中最大的文档编号

    Returns:
        最大编号（如果没有文件则返回9）
    """
    existing_files = get_existing_files("81.*.md")

    if not existing_files:
        return 9

    numbers = [extract_number(str(f)) for f in existing_files]
    return max(numbers) if numbers else 9


def generate_unique_path(target_path: Union[str, Path]) -> Path:
    """
    生成唯一的文件路径（如果文件已存在，添加序号）

    Args:
        target_path: 目标路径

    Returns:
        唯一路径
    """
    target_path = Path(target_path)

    if not target_path.exists():
        return target_path

    # 文件已存在，生成新名称
    stem = target_path.stem
    suffix = target_path.suffix
    parent = target_path.parent

    counter = 1
    while True:
        new_path = parent / f"{stem}_{counter}{suffix}"
        if not new_path.exists():
            return new_path
        counter += 1


# ==================== 日期时间工具 ====================

def get_today() -> str:
    """获取今天的日期（格式: YYYY-MM-DD）"""
    return datetime.now().strftime("%Y-%m-%d")


def get_current_datetime() -> str:
    """获取当前日期时间（格式: YYYY-MM-DD HH:MM:SS）"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_date_string(format: str = "%Y-%m-%d") -> str:
    """
    获取格式化的日期字符串

    Args:
        format: 日期格式
    """
    return datetime.now().strftime(format)


# ==================== 数据验证 ====================

def calculate_completeness(data: dict, required_fields: List[str]) -> float:
    """
    计算数据完整度

    Args:
        data: 数据字典
        required_fields: 必需字段列表

    Returns:
        完整度百分比 (0-100)
    """
    if not required_fields:
        return 100.0

    filled_count = sum(1 for field in required_fields if data.get(field))
    return (filled_count / len(required_fields)) * 100


def validate_data_quality(data: dict, config: dict) -> Dict[str, Any]:
    """
    验证数据质量

    Args:
        data: 采集的数据
        config: 质量配置（包含critical_data和optional_data）

    Returns:
        {
            'completeness': float,  # 完整度百分比
            'quality_level': str,   # excellent/good/fair/poor
            'missing_critical': list,  # 缺失的关键数据
            'missing_optional': list,  # 缺失的可选数据
            'can_proceed': bool     # 是否可以继续分析
        }
    """
    critical_fields = config.get('critical_data', [])
    optional_fields = config.get('optional_data', [])
    all_fields = critical_fields + optional_fields

    # 计算完整度
    completeness = calculate_completeness(data, all_fields)

    # 检查缺失字段
    missing_critical = [f for f in critical_fields if not data.get(f)]
    missing_optional = [f for f in optional_fields if not data.get(f)]

    # 判断质量级别
    if completeness >= 80:
        quality_level = "excellent"
    elif completeness >= 60:
        quality_level = "good"
    elif completeness >= 40:
        quality_level = "fair"
    else:
        quality_level = "poor"

    # 判断是否可以继续（关键数据都有 + 完整度>=60%）
    can_proceed = len(missing_critical) == 0 and completeness >= 60

    return {
        'completeness': completeness,
        'quality_level': quality_level,
        'missing_critical': missing_critical,
        'missing_optional': missing_optional,
        'can_proceed': can_proceed
    }


# ==================== 文本处理 ====================

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """截断文本到指定长度"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def clean_filename(filename: str) -> str:
    """
    清理文件名，移除非法字符

    Args:
        filename: 原始文件名

    Returns:
        清理后的文件名
    """
    # 移除或替换非法字符
    illegal_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    cleaned = filename

    for char in illegal_chars:
        cleaned = cleaned.replace(char, '_')

    # 移除首尾空格
    cleaned = cleaned.strip()

    # 限制长度
    if len(cleaned) > 200:
        cleaned = cleaned[:200]

    return cleaned


def extract_domain(url: str) -> str:
    """
    从URL中提取域名

    Args:
        url: URL字符串

    Returns:
        域名
    """
    match = re.search(r'https?://([^/]+)', url)
    if match:
        return match.group(1)
    return url


# ==================== 路径管理 ====================

def ensure_directory_exists(directory: Union[str, Path]) -> Path:
    """
    确保目录存在（如果不存在则创建）

    Args:
        directory: 目录路径

    Returns:
        目录的Path对象
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def get_product_raw_data_dir(product_name: str) -> Path:
    """
    获取产品的原始资料目录

    Args:
        product_name: 产品名称

    Returns:
        目录路径
    """
    clean_name = clean_filename(product_name)
    return KB_RAW_MATERIALS / clean_name


def get_product_document_path(product_name: str, number: Optional[int] = None) -> Path:
    """
    获取产品分析文档路径

    Args:
        product_name: 产品名称
        number: 文档编号（如果为None，自动分配）

    Returns:
        文档路径
    """
    if number is None:
        number = get_max_document_number() + 1

    clean_name = clean_filename(product_name)
    filename = f"81.{number:02d} {clean_name} 产品分析.md"

    return KB_MAIN_DOCS / filename


# ==================== 模式识别辅助 ====================

def calculate_similarity(text1: str, text2: str) -> float:
    """
    计算两段文本的相似度（简单版本，基于词重叠）

    Args:
        text1: 文本1
        text2: 文本2

    Returns:
        相似度 (0-1)
    """
    # 简单的词袋模型
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    if not words1 or not words2:
        return 0.0

    # Jaccard相似度
    intersection = len(words1 & words2)
    union = len(words1 | words2)

    return intersection / union if union > 0 else 0.0


# ==================== 格式化输出 ====================

def format_percentage(value: float, decimals: int = 1) -> str:
    """格式化百分比"""
    return f"{value:.{decimals}f}%"


def format_currency(value: float, currency: str = "$") -> str:
    """格式化货币"""
    if value >= 1_000_000_000:
        return f"{currency}{value/1_000_000_000:.1f}B"
    elif value >= 1_000_000:
        return f"{currency}{value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{currency}{value/1_000:.1f}K"
    else:
        return f"{currency}{value:.0f}"


def format_number(value: int) -> str:
    """格式化大数字"""
    if value >= 1_000_000_000:
        return f"{value/1_000_000_000:.1f}B"
    elif value >= 1_000_000:
        return f"{value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value/1_000:.1f}K"
    else:
        return str(value)


# ==================== 主函数（测试用） ====================

if __name__ == "__main__":
    print("=== Product Competitor Analysis - Utils Test ===")
    print()

    # 测试配置加载
    print("测试1: 加载配置文件")
    try:
        gospel_config = load_gospel_config()
        print(f"✅ GOSPEL配置加载成功，包含 {len(gospel_config.get('dimensions', {}))} 个维度")

        analysis_config = load_analysis_config()
        print(f"✅ 分析配置加载成功")

        expert_prompts = load_expert_prompts()
        print(f"✅ 专家Prompts加载成功，包含 {len(expert_prompts.get('experts', {}))} 位专家")
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")

    print()

    # 测试路径管理
    print("测试2: 路径管理")
    try:
        max_num = get_max_document_number()
        print(f"✅ 当前最大文档编号: {max_num}")

        test_path = get_product_document_path("TestProduct")
        print(f"✅ 生成文档路径: {test_path}")

        raw_dir = get_product_raw_data_dir("TestProduct")
        print(f"✅ 原始资料目录: {raw_dir}")
    except Exception as e:
        print(f"❌ 路径管理测试失败: {e}")

    print()

    # 测试产品名提取
    print("测试3: 产品名提取")
    test_cases = [
        "对比 ChatGPT、Claude、Gemini",
        "分析 Notion vs Obsidian",
    ]

    for test in test_cases:
        products = extract_product_names(test)
        print(f"输入: {test}")
        print(f"提取: {products}")

    print()
    print("=== 测试完成 ===")
