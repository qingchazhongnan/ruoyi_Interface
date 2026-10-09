# -*- coding: utf-8 -*-
"""
Excel 数据驱动演示用例（与 yaml 驱动并存对比，面试可讲"换载体不换代码"）
- 数据源   : data/user_cases.xlsx（openpyxl 读取）
- 读取器   : utils/excel_loader.py 的 read_excel()
- 其余逻辑 : 与 test_user.py 的 yaml 驱动版完全一致（双断言 + {ts} 唯一 + 后置清理）
"""
import time

import allure
import pytest

from api.base_api import BaseApi
from api.user_api import UserApi
from utils.excel_loader import read_excel
from utils.yaml_loader import render

_excel_cases = read_excel("user_cases.xlsx")
_excel_ids = [c["title"] for c in _excel_cases]
_ts = int(time.time())  # 本次运行时间戳，保证账号唯一


@allure.feature("用户管理接口")
@allure.story("新增用户（Excel 数据驱动）")
@pytest.mark.user
@pytest.mark.parametrize("case", _excel_cases, ids=_excel_ids)
class TestAddUserExcel:
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_user_by_excel(self, user_api: UserApi, cleanup_users, case):
        # 渲染 {ts} 占位符：Excel 里的 userName: excel_{ts} -> excel_<时间戳>
        data = render(case, ts=_ts)
        fields = {k: v for k, v in data.items()
                  if k not in ("title", "expected_code", "expected_msg", "cleanup")}

        # 需要清理的账号先登记（重复用户名用例不登记，避免误删内置账号）
        if data.get("cleanup", True):
            cleanup_users.append(data["userName"])

        resp = user_api.add_user(**fields)
        body = BaseApi.json(resp)
        assert body.get("code") == data["expected_code"], f"code 不符: {body}"
        assert data["expected_msg"] in (body.get("msg") or ""), f"msg 不符: {body}"

        # 新增成功则再查一次，确认真的落了库
        if data.get("expected_code") == 200:
            assert user_api.find_user_id(data["userName"]) is not None, "新增成功但查询不到"
