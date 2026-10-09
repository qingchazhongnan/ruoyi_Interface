# -*- coding: utf-8 -*-
"""
一键运行入口：pytest 全量执行 + 自动生成 Allure 报告
============================================================
用法（项目根目录，激活 .venv 后）：
    python run.py

等价于手动两步：
    1) python -m pytest
    2) allure generate ./reports/allure-results -o ./reports/allure-report --clean
"""
import os
import sys

import pytest

if __name__ == "__main__":
    # 1) 跑全量用例（pytest.ini 已配好双报告 + 日志）
    code = pytest.main()

    # 2) 自动生成 Allure 静态报告（可在浏览器直接打开）
    ok = os.system(
        "allure generate ./reports/allure-results -o ./reports/allure-report --clean"
    )
    print("=" * 60)
    print("运行结果:", "全部通过" if code == 0 else f"有失败（exit={code}）")
    print("pytest-html 报告: reports\\report.html")
    print("Allure 报告:      reports\\allure-report\\index.html")
    print("运行日志:         logs\\run.log")
    print("=" * 60)

    # 把 pytest 的退出码透传给命令行（CI 里判断成功/失败靠它）
    raise SystemExit(code)
