#!/usr/bin/env python3
"""
generate_test_template.py - 生成测试模板

功能:
- 基于实现文件生成测试模板
- 支持多种测试框架 (pytest, unittest, jest)
- 遵循 TDD 最佳实践

使用:
    python generate_test_template.py <impl_file> [framework]

示例:
    python generate_test_template.py src/auth/api/login.py pytest
    python generate_test_template.py src/user/service/user_service.py unittest
"""

import sys
from pathlib import Path


def generate_pytest_template(impl_file: Path) -> str:
    """生成 pytest 测试模板"""
    module_name = impl_file.stem

    template = f'''"""
测试模块: {module_name}

遵循 TDD 原则:
1. 先写测试 (Red)
2. 实现功能 (Green)
3. 重构优化 (Refactor)
"""

import pytest
from {module_name} import *


class Test{module_name.capitalize()}:
    """测试类: {module_name}"""

    def setup_method(self):
        """每个测试前执行"""
        pass

    def teardown_method(self):
        """每个测试后执行"""
        pass

    def test_example(self):
        """示例测试"""
        # Arrange (准备)
        pass

        # Act (执行)
        pass

        # Assert (断言)
        assert True, "待实现"
'''
    return template


def generate_unittest_template(impl_file: Path) -> str:
    """生成 unittest 测试模板"""
    module_name = impl_file.stem

    template = f'''"""
测试模块: {module_name}
"""

import unittest
from {module_name} import *


class Test{module_name.capitalize()}(unittest.TestCase):
    """测试类: {module_name}"""

    def setUp(self):
        """每个测试前执行"""
        pass

    def tearDown(self):
        """每个测试后执行"""
        pass

    def test_example(self):
        """示例测试"""
        self.assertTrue(True, "待实现")


if __name__ == "__main__":
    unittest.main()
'''
    return template


def generate_jest_template(impl_file: Path) -> str:
    """生成 jest 测试模板 (JavaScript/TypeScript)"""
    module_name = impl_file.stem

    template = f'''/**
 * 测试模块: {module_name}
 */

import {{}} from './{module_name}';

describe('{module_name}', () => {{
  beforeEach(() => {{
    // 每个测试前执行
  }});

  afterEach(() => {{
    // 每个测试后执行
  }});

  test('example test', () => {{
    // Arrange (准备)

    // Act (执行)

    // Assert (断言)
    expect(true).toBe(true);
  }});
}});
'''
    return template


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_test_template.py <impl_file> [framework]")
        print()
        print("Frameworks: pytest (default), unittest, jest")
        sys.exit(1)

    impl_file = Path(sys.argv[1])
    framework = sys.argv[2] if len(sys.argv) > 2 else "pytest"

    if not impl_file.exists():
        print(f"错误: 文件不存在: {impl_file}")
        sys.exit(1)

    # 生成测试文件路径
    if impl_file.suffix == ".py":
        test_file = impl_file.parent.parent.parent / "tests" / f"test_{impl_file.name}"
    elif impl_file.suffix in [".js", ".ts"]:
        test_file = impl_file.parent / f"{impl_file.stem}.test{impl_file.suffix}"
    else:
        print(f"错误: 不支持的文件类型: {impl_file.suffix}")
        sys.exit(1)

    # 生成模板
    if framework == "pytest":
        template = generate_pytest_template(impl_file)
    elif framework == "unittest":
        template = generate_unittest_template(impl_file)
    elif framework == "jest":
        template = generate_jest_template(impl_file)
    else:
        print(f"错误: 不支持的框架: {framework}")
        sys.exit(1)

    # 写入文件
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text(template)

    print(f"✓ 测试模板已生成: {test_file}")
    print()
    print("下一步: 填写测试用例，然后运行 TDD 流程")
    print(f"  python ../skills/run_tdd_cycle.py . task_id")


if __name__ == "__main__":
    main()
