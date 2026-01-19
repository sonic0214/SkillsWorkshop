#!/usr/bin/env python3
"""
Product Competitor Analysis - 数据收集脚本
Version: v1.0
Created: 2025-12-19

提供数据收集、保存和管理功能。
配合Claude的WebSearch/WebFetch工具使用。
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# 导入utils函数
from utils import (
    load_analysis_config,
    get_product_raw_data_dir,
    ensure_directory_exists,
    save_json,
    load_json,
    write_file,
    file_exists,
    validate_data_quality,
    get_today,
    clean_filename,
    extract_domain,
)
from urllib.parse import quote_plus


# ==================== 数据收集类 ====================

class DataCollector:
    """
    数据收集器类

    负责管理产品数据的收集、保存和验证
    """

    def __init__(self, product_name: str):
        """
        初始化数据收集器

        Args:
            product_name: 产品名称
        """
        self.product_name = product_name
        self.raw_data_dir = get_product_raw_data_dir(product_name)
        self.config = load_analysis_config()

        # 确保目录存在
        ensure_directory_exists(self.raw_data_dir)
        ensure_directory_exists(self.raw_data_dir / "user_provided")

        # 数据存储
        self.collected_data = {
            'product_name': product_name,
            'collection_date': get_today(),
            'basic_info': {},
            'funding_info': {},
            'user_data': {},
            'business_model': {},
            'user_reviews': {},
            'competitors': {},
            'sources': []
        }

    def add_basic_info(self, info: Dict[str, Any]) -> None:
        """
        添加基础信息

        Args:
            info: 包含官网URL、产品描述、上线时间、团队信息等
        """
        self.collected_data['basic_info'].update(info)

    def add_funding_info(self, info: Dict[str, Any]) -> None:
        """
        添加融资信息

        Args:
            info: 包含融资轮次、金额、投资方、估值等
        """
        self.collected_data['funding_info'].update(info)

    def add_user_data(self, data: Dict[str, Any]) -> None:
        """
        添加用户数据

        Args:
            data: 包含MAU/DAU、增长趋势、用户分布等
        """
        self.collected_data['user_data'].update(data)

    def add_business_model(self, model: Dict[str, Any]) -> None:
        """
        添加商业模式信息

        Args:
            model: 包含定价信息、付费方案、价格锚点等
        """
        self.collected_data['business_model'].update(model)

    def add_user_reviews(self, reviews: Dict[str, Any]) -> None:
        """
        添加用户评价

        Args:
            reviews: 包含Product Hunt、Reddit、Twitter、App Store评分等
        """
        self.collected_data['user_reviews'].update(reviews)

    def add_competitors(self, competitors: List[str]) -> None:
        """
        添加竞品信息

        Args:
            competitors: 竞品列表
        """
        self.collected_data['competitors'] = competitors

    def add_source(self, source: str, source_type: str = "web") -> None:
        """
        添加数据来源

        Args:
            source: 来源URL或描述
            source_type: 来源类型 (web/user_provided/api)
        """
        self.collected_data['sources'].append({
            'source': source,
            'type': source_type,
            'timestamp': datetime.now().isoformat()
        })

    def calculate_completeness(self) -> float:
        """
        计算数据完整度

        Returns:
            完整度百分比 (0-100)
        """
        data_config = self.config.get('data_collection', {}).get('quality_check', {})

        critical_fields = data_config.get('critical_data', [])
        optional_fields = data_config.get('optional_data', [])

        # 映射字段到实际数据
        field_mapping = {
            '官网URL': lambda: self.collected_data['basic_info'].get('official_url'),
            '产品描述': lambda: self.collected_data['basic_info'].get('description'),
            '商业模式类型': lambda: self.collected_data['business_model'].get('model_type'),
            '用户规模': lambda: self.collected_data['user_data'].get('mau') or self.collected_data['user_data'].get('dau'),
            '融资信息': lambda: bool(self.collected_data['funding_info']),
            '留存率': lambda: self.collected_data['user_data'].get('retention'),
            '转化率': lambda: self.collected_data['business_model'].get('conversion_rate'),
        }

        # 检查字段完整度
        all_fields = critical_fields + optional_fields
        filled_count = sum(1 for field in all_fields if field in field_mapping and field_mapping[field]())

        return (filled_count / len(all_fields) * 100) if all_fields else 0

    def validate(self) -> Dict[str, Any]:
        """
        验证数据质量

        Returns:
            验证结果字典
        """
        data_config = self.config.get('data_collection', {}).get('quality_check', {})

        return validate_data_quality(self.collected_data, data_config)

    def save(self) -> Dict[str, Path]:
        """
        保存收集的数据

        Returns:
            保存的文件路径字典
        """
        date_str = get_today()
        saved_files = {}

        # 1. 保存原始JSON数据
        json_path = self.raw_data_dir / f"raw_data_{date_str}.json"
        save_json(json_path, self.collected_data)
        saved_files['raw_data'] = json_path

        # 2. 保存README
        readme_content = self._generate_readme()
        readme_path = self.raw_data_dir / "README.md"
        write_file(readme_path, readme_content)
        saved_files['readme'] = readme_path

        # 3. 如果有单独的内容，保存为独立文件
        if self.collected_data['basic_info'].get('official_website_content'):
            website_path = self.raw_data_dir / "official_website.md"
            write_file(website_path, self.collected_data['basic_info']['official_website_content'])
            saved_files['website'] = website_path

        if self.collected_data['business_model'].get('pricing_page_content'):
            pricing_path = self.raw_data_dir / "pricing_page.md"
            write_file(pricing_path, self.collected_data['business_model']['pricing_page_content'])
            saved_files['pricing'] = pricing_path

        if self.collected_data['user_reviews'].get('reviews_text'):
            reviews_path = self.raw_data_dir / "user_reviews.md"
            write_file(reviews_path, self.collected_data['user_reviews']['reviews_text'])
            saved_files['reviews'] = reviews_path

        return saved_files

    def _generate_readme(self) -> str:
        """
        生成README内容

        Returns:
            README的markdown内容
        """
        completeness = self.calculate_completeness()
        validation = self.validate()

        readme = f"""# {self.product_name} - 原始资料库

> **采集时间**: {self.collected_data['collection_date']}
> **数据完整度**: {completeness:.1f}% ({validation['quality_level']})
> **数据来源数**: {len(self.collected_data['sources'])}

## 数据概览

### 基础信息
- 官网: {self.collected_data['basic_info'].get('official_url', '未采集')}
- 描述: {self.collected_data['basic_info'].get('description', '未采集')[:100]}...
- 上线时间: {self.collected_data['basic_info'].get('launch_date', '未采集')}
- 团队: {self.collected_data['basic_info'].get('team', '未采集')}

### 融资信息
- 融资轮次: {self.collected_data['funding_info'].get('round', '未采集')}
- 融资金额: {self.collected_data['funding_info'].get('amount', '未采集')}
- 投资方: {self.collected_data['funding_info'].get('investors', '未采集')}

### 用户数据
- MAU: {self.collected_data['user_data'].get('mau', '未采集')}
- DAU: {self.collected_data['user_data'].get('dau', '未采集')}
- 增长率: {self.collected_data['user_data'].get('growth_rate', '未采集')}

### 商业模式
- 模式类型: {self.collected_data['business_model'].get('model_type', '未采集')}
- 定价: {self.collected_data['business_model'].get('pricing', '未采集')}

## 文件说明

- `raw_data_{self.collected_data['collection_date']}.json` - 原始JSON数据
- `official_website.md` - 官网内容快照（如果采集）
- `pricing_page.md` - 定价页面快照（如果采集）
- `user_reviews.md` - 用户评价汇总（如果采集）
- `user_provided/` - 用户手动提供的资料

## 数据质量

### 完整度评估
- 总体完整度: {completeness:.1f}%
- 质量级别: {validation['quality_level']}
- 是否可继续分析: {'是' if validation['can_proceed'] else '否'}

### 缺失数据
"""

        if validation['missing_critical']:
            readme += "\n**缺失关键数据**:\n"
            for field in validation['missing_critical']:
                readme += f"- {field}\n"

        if validation['missing_optional']:
            readme += "\n**缺失可选数据**:\n"
            for field in validation['missing_optional']:
                readme += f"- {field}\n"

        readme += "\n## 数据来源\n\n"
        for i, source in enumerate(self.collected_data['sources'], 1):
            readme += f"{i}. [{source['type']}] {source['source']}\n"

        readme += f"\n## 更新记录\n\n- {self.collected_data['collection_date']}: 初始采集\n"

        return readme

    @classmethod
    def load_existing(cls, product_name: str, date: Optional[str] = None) -> Optional['DataCollector']:
        """
        加载已存在的数据收集器

        Args:
            product_name: 产品名称
            date: 数据日期（如果为None，加载最新）

        Returns:
            DataCollector实例，如果不存在则返回None
        """
        raw_data_dir = get_product_raw_data_dir(product_name)

        if not raw_data_dir.exists():
            return None

        # 查找数据文件
        if date:
            json_file = raw_data_dir / f"raw_data_{date}.json"
        else:
            # 查找最新的数据文件
            json_files = list(raw_data_dir.glob("raw_data_*.json"))
            if not json_files:
                return None
            json_file = sorted(json_files, reverse=True)[0]

        if not json_file.exists():
            return None

        # 加载数据
        collector = cls(product_name)
        collector.collected_data = load_json(json_file)

        return collector


# ==================== 数据收集辅助函数 ====================

def get_search_queries(product_name: str) -> List[Dict[str, str]]:
    """
    生成数据收集的搜索查询列表

    Args:
        product_name: 产品名称

    Returns:
        搜索查询列表 [{'purpose': 'xxx', 'query': 'xxx'}, ...]
    """
    config = load_analysis_config()
    data_collection = config.get('data_collection', {})
    templates = data_collection.get('search_templates', {})
    overrides = data_collection.get('source_url_overrides', {}).get(product_name, {})

    queries = []

    # 基于模板生成查询
    template_mapping = {
        'official_website': '官网',
        'about': '关于/公司信息',
        'pricing': '定价',
        'fees': '费用',
        'commission': '佣金',
        'spread': '点差',
        'app_store': 'App Store',
        'google_play': 'Google Play',
        'funding': '融资',
        'team': '团队',
        'users': '用户数据',
        'reviews': '用户评价',
        'product_hunt': 'Product Hunt',
        'g2': 'G2口碑',
        'capterra': 'Capterra口碑',
        'trustpilot': 'Trustpilot口碑',
        'competitors': '竞品',
        'alternatives': '替代方案',
        'regulatory': '合规/监管',
        'terms': '条款',
        'privacy': '隐私',
        'help_center': '帮助中心',
        'press': '新闻稿/公告',
        'blog': '官方博客',
        'news': '新闻',
        'reddit': 'Reddit讨论',
        'twitter': 'Twitter提及',
        'youtube': '视频评测',
        'market_size': '市场规模',
        'tam_sam_som': 'TAM/SAM/SOM',
        'industry_report': '行业报告',
        'market_growth': '市场增速',
        'marketsandmarkets': 'MarketsandMarkets 报告',
        'mordor': 'Mordor Intelligence 报告',
        'fortune_business_insights': 'Fortune Business Insights 报告',
        'giiresearch': 'GII Research 报告',
        'market_us': 'market.us 报告',
        'prnewswire': 'PRNewswire 新闻稿',
        'business_wire': 'Business Wire 新闻稿',
        'nytimes': 'NYTimes 新闻',
        'a16z': 'A16Z 投资/观点',
        'sequoia': 'Sequoia 投资/观点',
        'semrush': 'SEMrush 流量数据',
        'google_news': 'Google News',
        'hacker_news': 'Hacker News',
        'tool_reviews': '工具评测（Substack）',
        'competitor_comparison_blog': '竞品对比博客',
    }

    for key, purpose in template_mapping.items():
        if key in overrides:
            # 有直连URL时，跳过搜索查询
            continue
        if key in templates:
            query = templates[key].replace('{product_name}', product_name)
            queries.append({
                'purpose': purpose,
                'query': query
            })

    return queries


def get_direct_sources(product_name: str) -> List[Dict[str, str]]:
    """
    获取直连数据源（优先级高于搜索）

    Args:
        product_name: 产品名称

    Returns:
        直连数据源列表 [{'purpose': 'xxx', 'url': 'xxx'}, ...]
    """
    config = load_analysis_config()
    data_collection = config.get('data_collection', {})
    overrides = data_collection.get('source_url_overrides', {}).get(product_name, {})
    templates = data_collection.get('source_url_templates', {})

    purpose_mapping = {
        'official_website': '官网',
        'about': '关于/公司信息',
        'pricing': '定价',
        'fees': '费用',
        'commission': '佣金',
        'spread': '点差',
        'app_store': 'App Store',
        'google_play': 'Google Play',
        'funding': '融资',
        'team': '团队',
        'users': '用户数据',
        'reviews': '用户评价',
        'product_hunt': 'Product Hunt',
        'g2': 'G2口碑',
        'capterra': 'Capterra口碑',
        'trustpilot': 'Trustpilot口碑',
        'competitors': '竞品',
        'alternatives': '替代方案',
        'regulatory': '合规/监管',
        'terms': '条款',
        'privacy': '隐私',
        'help_center': '帮助中心',
        'press': '新闻稿/公告',
        'blog': '官方博客',
        'news': '新闻',
        'reddit': 'Reddit讨论',
        'twitter': 'Twitter提及',
        'youtube': '视频评测',
        'market_size': '市场规模',
        'tam_sam_som': 'TAM/SAM/SOM',
        'industry_report': '行业报告',
        'market_growth': '市场增速',
        'business_wire': 'Business Wire 新闻稿',
        'nytimes': 'NYTimes 新闻',
        'a16z': 'A16Z 投资/观点',
        'sequoia': 'Sequoia 投资/观点',
        'google_news': 'Google News',
        'hacker_news': 'Hacker News',
        'semrush': 'SEMrush 流量数据',
    }

    direct_sources = []
    seen_urls = set()

    def add_source(key: str, url: str) -> None:
        if not url or url in seen_urls:
            return
        seen_urls.add(url)
        direct_sources.append({
            'purpose': purpose_mapping.get(key, key),
            'url': url,
        })

    for key, url in overrides.items():
        add_source(key, url)

    # 使用模板生成直连URL（仅填充可用占位符）
    if templates:
        domain = None
        for key in ('official_website', 'official_url', 'website', 'home'):
            if key in overrides:
                domain = extract_domain(overrides[key])
                break
        if not domain and '.' in product_name and ' ' not in product_name:
            domain = product_name.lower()

        product_name_encoded = quote_plus(product_name)
        for key, template in templates.items():
            if key in overrides:
                continue
            if '{product_name}' in template:
                add_source(key, template.format(product_name=product_name_encoded))
            elif '{domain}' in template and domain:
                add_source(key, template.format(domain=domain))

    return direct_sources


def create_data_collection_plan(product_name: str) -> Dict[str, Any]:
    """
    创建数据收集计划

    Args:
        product_name: 产品名称

    Returns:
        收集计划字典
    """
    return {
        'product_name': product_name,
        'direct_sources': get_direct_sources(product_name),
        'search_queries': get_search_queries(product_name),
        'data_to_collect': {
            'basic_info': ['官网URL', '产品描述', '上线时间', '团队信息'],
            'official_info': ['About/公司信息', '条款/隐私', '帮助中心/FAQ', '合规/牌照'],
            'funding_info': ['融资轮次', '融资金额', '投资方', '估值'],
            'user_data': ['MAU/DAU/WAU', '增长趋势', '用户分布'],
            'business_model': ['定价页面', '付费方案', '价格锚点'],
            'user_reviews': ['Product Hunt评分', 'Reddit讨论', 'Twitter提及', 'App Store评分'],
            'reputation': ['G2/Capterra/Trustpilot评价', '媒体评测'],
            'competitors': ['主要竞品列表', '对比文章'],
            'market_data': ['TAM/SAM/SOM估算', '行业规模与增速', '市场报告来源']
        },
        'estimated_time': '5-10分钟',
        'automation_level': '90%'
    }


def save_user_provided_data(product_name: str, content: str, filename: str, content_type: str = "markdown") -> Path:
    """
    保存用户提供的数据

    Args:
        product_name: 产品名称
        content: 内容
        filename: 文件名
        content_type: 内容类型

    Returns:
        保存的文件路径
    """
    raw_data_dir = get_product_raw_data_dir(product_name)
    user_provided_dir = raw_data_dir / "user_provided"
    ensure_directory_exists(user_provided_dir)

    # 清理文件名
    clean_name = clean_filename(filename)

    # 添加扩展名
    if content_type == "markdown" and not clean_name.endswith('.md'):
        clean_name += '.md'
    elif content_type == "json" and not clean_name.endswith('.json'):
        clean_name += '.json'

    file_path = user_provided_dir / clean_name
    write_file(file_path, content)

    return file_path


# ==================== CLI接口 ====================

def main():
    """CLI主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='产品数据收集工具')
    parser.add_argument('product', help='产品名称')
    parser.add_argument('--plan', action='store_true', help='显示数据收集计划')
    parser.add_argument('--load', action='store_true', help='加载已有数据')
    parser.add_argument('--validate', action='store_true', help='验证数据质量')

    args = parser.parse_args()

    if args.plan:
        # 显示收集计划
        plan = create_data_collection_plan(args.product)
        print(f"\n=== {args.product} 数据收集计划 ===\n")
        print(f"预计时间: {plan['estimated_time']}")
        print(f"自动化程度: {plan['automation_level']}")
        if plan.get('direct_sources'):
            print("\n直连数据源（优先使用）:")
            for s in plan['direct_sources']:
                print(f"  - {s['purpose']}: {s['url']}")
        print("\n搜索查询:")
        for q in plan['search_queries']:
            print(f"  - {q['purpose']}: {q['query']}")
        print("\n需要收集的数据:")
        for category, items in plan['data_to_collect'].items():
            print(f"  {category}:")
            for item in items:
                print(f"    - {item}")

    elif args.load:
        # 加载已有数据
        collector = DataCollector.load_existing(args.product)
        if collector:
            print(f"\n✅ 成功加载 {args.product} 的数据")
            print(f"采集日期: {collector.collected_data['collection_date']}")
            print(f"数据完整度: {collector.calculate_completeness():.1f}%")
        else:
            print(f"\n❌ 未找到 {args.product} 的数据")

    elif args.validate:
        # 验证数据
        collector = DataCollector.load_existing(args.product)
        if collector:
            validation = collector.validate()
            print(f"\n=== {args.product} 数据质量验证 ===\n")
            print(f"完整度: {validation['completeness']:.1f}%")
            print(f"质量级别: {validation['quality_level']}")
            print(f"可继续分析: {'是' if validation['can_proceed'] else '否'}")

            if validation['missing_critical']:
                print("\n缺失关键数据:")
                for field in validation['missing_critical']:
                    print(f"  - {field}")

            if validation['missing_optional']:
                print("\n缺失可选数据:")
                for field in validation['missing_optional']:
                    print(f"  - {field}")
        else:
            print(f"\n❌ 未找到 {args.product} 的数据")

    else:
        # 创建新的收集器
        collector = DataCollector(args.product)
        print(f"\n✅ 已为 {args.product} 创建数据收集器")
        print(f"数据目录: {collector.raw_data_dir}")
        print("\n使用 --plan 查看收集计划")
        print("使用 --load 加载已有数据")
        print("使用 --validate 验证数据质量")


if __name__ == "__main__":
    main()
