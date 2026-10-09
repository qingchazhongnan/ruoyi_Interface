# -*- coding: utf-8 -*-
"""
角色管理 - Excel 数据驱动用例（与 yaml 驱动并存，演示"换载体不换代码"）
- 数据源   : data/role_cases.xlsx（openpyxl 读取）
- 读取器   : utils/excel_loader.py::read_excel()
- 断言逻辑 : 与 test_role.py 的 yaml 版完全一致
"""
import time

import allure
import pytest

from api.base_api import BaseApi
from api.role_api import RoleApi
from utils.excel_loader import read_excel
from utils.yaml_loader import render

_excel_cases = read_excel("role_cases.xlsx")
_excel_ids = [c["title"] for c in _excel_cases]
_ts = int(time.time())


@allure.feature("角色管理接口")
@allure.story("角色逆向用例（Excel 数据驱动）")
@pytest.mark.user
@pytest.mark.parametrize("case", _excel_cases, ids=_excel_ids)
class TestRoleExcel:
    @allure.severity(allure.severity_level.NORMAL)
    def test_role_negative_by_excel(self, role_api: RoleApi, case):
        data = render(case, ts=_ts)

        if data.get("action") == "delete":
            resp = role_api.delete_role(data["role_id"])
        else:
            # Excel 扁平列 -> 组装 payload（空单元格跳过；menuIds 字符串转列表）
            payload = {}
            for k in ("roleName", "roleKey", "roleSort", "status"):
                v = data.get(k)
                if v not in ("", None):
                    payload[k] = v
            if data.get("menuIds") not in ("", None):
                payload["menuIds"] = [int(data["menuIds"])]
            resp = role_api.add_role(**payload)

        body = BaseApi.json(resp)
        assert body.get("code") == data["expected_code"], f"code 不符: {body}"
        assert data["expected_msg"] in (body.get("msg") or ""), f"msg 不符: {body}"
