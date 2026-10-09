# -*- coding: utf-8 -*-
"""
部门管理接口用例（注意：部门列表返回 data 字段，见 api/dept_api.py）
- 正向全链路：增→查→改→删→验证无残留
- 逆向数据驱动：缺必填 / 删除不存在
"""
import time

import allure
import pytest

from api.base_api import BaseApi
from api.dept_api import DeptApi
from utils.yaml_loader import get_cases, render

_neg_cases = get_cases("dept_data.yaml", "negative_cases")
_neg_ids = [c["title"] for c in _neg_cases]
_ts = int(time.time())


@allure.feature("部门管理接口")
@pytest.mark.user
class TestDept:
    @allure.story("部门增删改查全链路")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_dept_full_flow(self, dept_api: DeptApi, cleanup_items):
        dept_name = f"dept_{_ts}"

        # 1) 新增
        resp = dept_api.add_dept(parentId=103, deptName=dept_name, orderNum=9, status="0")
        assert BaseApi.is_success(resp), f"新增失败: {BaseApi.json(resp)}"
        dept_id = dept_api.find_dept_id(dept_name)
        assert dept_id is not None, "新增后查询不到 deptId"
        cleanup_items.append((None, dept_api.delete_dept, dept_id))

        # 2) 修改
        resp = dept_api.update_dept(dept_id, parentId=103, deptName=f"{dept_name}_改",
                                    orderNum=9, status="0")
        assert BaseApi.is_success(resp), f"修改失败: {BaseApi.json(resp)}"
        assert dept_api.find_dept_id(f"{dept_name}_改") is not None, "修改后查不到新名字"

        # 3) 删除 + 验证
        resp = dept_api.delete_dept(dept_id)
        assert BaseApi.is_success(resp), f"删除失败: {BaseApi.json(resp)}"
        assert dept_api.assert_dept_gone(f"{dept_name}_改"), "删除后仍能查到"

    @allure.story("部门逆向用例（yaml 数据驱动）")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("case", _neg_cases, ids=_neg_ids)
    def test_dept_negative(self, dept_api: DeptApi, case):
        data = render(case, ts=_ts)
        if data.get("action") == "delete":
            resp = dept_api.delete_dept(data["dept_id"])
        else:
            payload = {k: v for k, v in data["payload"].items() if v not in (None, "")}
            resp = dept_api.add_dept(**payload)
        body = BaseApi.json(resp)
        assert body.get("code") == data["expected_code"], f"code 不符: {body}"
        assert data["expected_msg"] in (body.get("msg") or ""), f"msg 不符: {body}"
