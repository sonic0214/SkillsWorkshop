#!/usr/bin/env python3
"""
项目复杂度评估器

基于需求文档评估项目复杂度，推荐合适的流程模式。

复杂度维度：
1. 功能数量（用户故事数量）
2. 技术栈复杂度（前后端分离、数据库、第三方集成）
3. 数据模型复杂度（实体数量、关系复杂度）
4. 预期用户规模
5. 团队规模
6. 时间压力

输出：
- simple: 快速模式（Fast Track） - 得分 < 0.3
- standard: 标准模式（Standard） - 得分 0.3-0.7
- complex: 严格模式（Rigorous） - 得分 > 0.7

作者：MyBrain Architect Agent
日期：2025-12-08
版本：1.0.0
"""

import re
import sys
from pathlib import Path
from typing import Dict, Tuple


class ComplexityAssessor:
    """项目复杂度评估器"""

    def __init__(self, requirements_file: str = None):
        self.requirements_file = Path(requirements_file) if requirements_file else None
        self.requirements_text = ""
        self.metrics = {}
        self.complexity_score = 0.0
        self.recommended_mode = "standard"

    def load_requirements(self):
        """加载需求文档"""
        if self.requirements_file and self.requirements_file.exists():
            with open(self.requirements_file, 'r', encoding='utf-8') as f:
                self.requirements_text = f.read()
        else:
            # 交互式输入
            print("未提供需求文件，进入交互式评估模式\n")
            self.requirements_text = ""

    def assess_feature_complexity(self) -> float:
        """
        评估功能复杂度（基于用户故事数量）

        Returns:
            0.0-1.0 的得分
        """
        # 方法1：从文档中识别用户故事数量
        user_story_count = 0

        # 识别 "作为...我想要..." 模式
        user_story_patterns = [
            r'作为.*?我想要.*?以便',
            r'As a.*?I want.*?so that',
            r'User Story \d+',
            r'Story \d+:',
        ]

        for pattern in user_story_patterns:
            matches = re.findall(pattern, self.requirements_text, re.IGNORECASE)
            user_story_count += len(matches)

        # 方法2：如果文档中没有明确的用户故事，通过关键词估算功能数量
        if user_story_count == 0:
            feature_keywords = [
                '登录', '注册', '创建', '编辑', '删除', '查询', '搜索',
                '上传', '下载', '分享', '评论', '点赞', '支付', '通知',
                'login', 'register', 'create', 'edit', 'delete', 'search',
                'upload', 'download', 'share', 'comment', 'like', 'payment'
            ]
            for keyword in feature_keywords:
                if keyword in self.requirements_text.lower():
                    user_story_count += 1

        self.metrics['user_story_count'] = user_story_count

        # 评分规则
        if user_story_count < 5:
            return 0.2
        elif user_story_count < 15:
            return 0.5
        else:
            return 0.9

    def assess_tech_stack_complexity(self) -> float:
        """
        评估技术栈复杂度

        Returns:
            0.0-1.0 的得分
        """
        complexity = 0.0

        # 前后端分离 +0.2
        if any(kw in self.requirements_text.lower() for kw in ['前后端分离', 'spa', 'rest api', 'graphql']):
            complexity += 0.2
            self.metrics['frontend_backend_separation'] = True

        # 数据库 +0.1
        if any(kw in self.requirements_text.lower() for kw in ['数据库', 'database', 'postgresql', 'mysql', 'mongodb']):
            complexity += 0.1
            self.metrics['has_database'] = True

        # 第三方集成 +0.1 per integration
        integrations = re.findall(r'(?:集成|接入|调用).*?(?:API|接口|服务)', self.requirements_text)
        integration_count = min(len(integrations), 5)  # 最多计5个
        complexity += integration_count * 0.1
        self.metrics['integration_count'] = integration_count

        # 微服务架构 +0.3
        if any(kw in self.requirements_text.lower() for kw in ['微服务', 'microservice', 'kubernetes', 'k8s']):
            complexity += 0.3
            self.metrics['is_microservice'] = True

        # 实时功能 +0.2
        if any(kw in self.requirements_text.lower() for kw in ['实时', 'websocket', '推送', 'real-time']):
            complexity += 0.2
            self.metrics['has_realtime'] = True

        return min(complexity, 1.0)

    def assess_data_complexity(self) -> float:
        """
        评估数据模型复杂度

        Returns:
            0.0-1.0 的得分
        """
        # 识别实体/表数量
        entity_keywords = ['用户', '订单', '商品', '文章', '评论', '分类',
                          'user', 'order', 'product', 'article', 'comment', 'category']

        entity_count = 0
        for keyword in entity_keywords:
            if keyword in self.requirements_text.lower():
                entity_count += 1

        self.metrics['entity_count'] = entity_count

        # 评分规则
        if entity_count < 3:
            return 0.2
        elif entity_count < 8:
            return 0.5
        else:
            return 0.9

    def assess_scale_requirements(self) -> float:
        """
        评估规模要求（用户量、并发）

        Returns:
            0.0-1.0 的得分
        """
        # 识别用户规模
        user_scale_patterns = [
            (r'(\d+)\s*(?:万|w)\s*用户', 10000),
            (r'(\d+)k?\s*users?', 1),
            (r'(\d+)\s*并发', 1),
            (r'(\d+)\s*concurrent', 1),
        ]

        max_users = 0
        for pattern, multiplier in user_scale_patterns:
            matches = re.findall(pattern, self.requirements_text.lower())
            for match in matches:
                users = int(match) * multiplier
                max_users = max(max_users, users)

        self.metrics['expected_users'] = max_users

        # 评分规则
        if max_users == 0 or max_users < 1000:
            return 0.1
        elif max_users < 10000:
            return 0.5
        else:
            return 0.9

    def assess_interactive_factors(self) -> Dict[str, float]:
        """
        交互式评估额外因素

        Returns:
            因素字典
        """
        factors = {}

        print("\n=== 额外因素评估 ===\n")

        # 团队规模
        team_size = input("团队规模（人数，直接回车默认1）: ").strip()
        team_size = int(team_size) if team_size else 1

        if team_size == 1:
            factors['team_size_factor'] = -0.1  # 单人项目降低复杂度
        elif team_size <= 2:
            factors['team_size_factor'] = 0.0
        else:
            factors['team_size_factor'] = 0.2   # 多人协作增加复杂度

        # 时间压力
        deadline = input("开发周期（周数，直接回车默认4）: ").strip()
        deadline = int(deadline) if deadline else 4

        if deadline < 2:
            factors['time_pressure_factor'] = -0.2  # 时间紧迫，降低流程复杂度
        elif deadline < 4:
            factors['time_pressure_factor'] = -0.1
        else:
            factors['time_pressure_factor'] = 0.0

        # 关键业务
        is_critical = input("是否关键业务系统？(y/n，直接回车默认n): ").strip().lower()
        if is_critical == 'y':
            factors['critical_factor'] = 0.3  # 关键业务增加质量要求
        else:
            factors['critical_factor'] = 0.0

        # MVP 还是生产
        is_mvp = input("是否 MVP/原型？(y/n，直接回车默认n): ").strip().lower()
        if is_mvp == 'y':
            factors['mvp_factor'] = -0.3  # MVP 降低流程复杂度
        else:
            factors['mvp_factor'] = 0.0

        return factors

    def calculate_complexity_score(self, interactive: bool = True) -> float:
        """
        计算综合复杂度得分

        Args:
            interactive: 是否交互式输入额外因素

        Returns:
            0.0-1.0 的得分
        """
        # 基础得分（权重分配）
        feature_score = self.assess_feature_complexity() * 0.3
        tech_score = self.assess_tech_stack_complexity() * 0.3
        data_score = self.assess_data_complexity() * 0.2
        scale_score = self.assess_scale_requirements() * 0.2

        base_score = feature_score + tech_score + data_score + scale_score

        # 交互式因素
        if interactive and not self.requirements_file:
            factors = self.assess_interactive_factors()
            adjustment = sum(factors.values())
            self.metrics['interactive_factors'] = factors
        else:
            adjustment = 0.0

        final_score = max(0.0, min(1.0, base_score + adjustment))

        return final_score

    def recommend_mode(self) -> str:
        """
        推荐流程模式

        Returns:
            'fast_track', 'standard', 或 'rigorous'
        """
        if self.complexity_score < 0.3:
            return 'fast_track'
        elif self.complexity_score < 0.7:
            return 'standard'
        else:
            return 'rigorous'

    def generate_report(self) -> str:
        """生成评估报告"""
        report = []
        report.append("\n" + "=" * 60)
        report.append("项目复杂度评估报告")
        report.append("=" * 60)
        report.append("")

        report.append(f"📊 综合复杂度得分: {self.complexity_score:.2f} / 1.00")
        report.append("")

        report.append("📋 详细指标:")
        report.append(f"  - 用户故事数量: {self.metrics.get('user_story_count', 0)}")
        report.append(f"  - 实体数量: {self.metrics.get('entity_count', 0)}")
        report.append(f"  - 第三方集成: {self.metrics.get('integration_count', 0)}")
        report.append(f"  - 预期用户规模: {self.metrics.get('expected_users', '未知')}")

        if 'interactive_factors' in self.metrics:
            report.append("")
            report.append("🎯 额外因素:")
            for factor, value in self.metrics['interactive_factors'].items():
                report.append(f"  - {factor}: {value:+.1f}")

        report.append("")
        report.append("=" * 60)
        report.append(f"🎯 推荐模式: {self.recommended_mode.upper()}")
        report.append("=" * 60)
        report.append("")

        # 模式说明
        mode_descriptions = {
            'fast_track': """
快速模式 (Fast Track)
- 适合: MVP、原型验证、个人小项目
- 特点: 最小文档、TDD 可选、无强制测试覆盖率
- 开发周期: 短（约 1-2 周）
            """,
            'standard': """
标准模式 (Standard)
- 适合: 常规业务系统、中小型项目
- 特点: 强制 TDD、80% 覆盖率、渐进式设计
- 开发周期: 中等（约 4-8 周）
            """,
            'rigorous': """
严格模式 (Rigorous)
- 适合: 关键业务、生产环境、大型项目
- 特点: 90% 覆盖率、强制审查、完整文档
- 开发周期: 长（约 8-16 周）
            """
        }

        report.append(mode_descriptions[self.recommended_mode].strip())
        report.append("")

        return "\n".join(report)

    def assess(self, interactive: bool = True) -> Tuple[str, float, Dict]:
        """
        执行完整评估

        Args:
            interactive: 是否交互式

        Returns:
            (推荐模式, 复杂度得分, 指标详情)
        """
        self.load_requirements()
        self.complexity_score = self.calculate_complexity_score(interactive)
        self.recommended_mode = self.recommend_mode()

        return self.recommended_mode, self.complexity_score, self.metrics


def main():
    """CLI 入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="项目复杂度评估器"
    )
    parser.add_argument(
        "--requirements",
        "-r",
        help="需求文档路径（可选，不提供则交互式评估）"
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="非交互模式（仅基于文档评估）"
    )

    args = parser.parse_args()

    assessor = ComplexityAssessor(args.requirements)
    mode, score, metrics = assessor.assess(interactive=not args.non_interactive)

    # 输出报告
    print(assessor.generate_report())

    # 返回推荐的 SOP 文件名
    sop_file = f"sop_{mode}.yaml"
    print(f"💡 建议使用 SOP: {sop_file}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
