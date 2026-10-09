# -*- coding: utf-8 -*-
"""
角色管理接口用例
- TestRole.test_role_full_flow : 正向全链路（增→查→改→删→验证无残留）
- TestRole.test_role_negative  : 逆向数据驱动（yaml，缺必填/重复/删除不存在）
"""
import time

import allure
import pytest

from api.base_api import BaseApi
from api.role_api import RoleApi
from utils.yaml_loader import get_cases, render

_neg_cases = get_cases("role_data.yaml", "negative_cases")
_neg_ids = [c["title"] for c in _neg_cases]
_ts = int(time.time())


@allure.feature("角色管理接口")
@pytest.mark.user
class TestRole:
    @allure.story("角色增删改查全链路")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_role_full_flow(self, role_api: RoleApi, cleanup_items):
        role_name = f"role_{_ts}"
        role_key = f"role_key_{_ts}"

        # 1) 新增
        resp = role_api.add_role(roleName=role_name, roleKey=role_key,
                                 roleSort=6, status="0", menuIds=[1])
        assert BaseApi.is_success(resp), f"新增失败: {BaseApi.json(resp)}"
        role_id = role_api.find_role_id(role_name)
        assert role_id is not None, "新增后查询不到 roleId"
        cleanup_items.append((None, role_api.delete_role, role_id))  # 兜底按 id 删

        # 2) 修改（改名后再查确认）
        resp = role_api.update_role(role_id, roleName=f"{role_name}_改",
                                    roleKey=role_key, roleSort=6, status="0", menuIds=[1])
        assert BaseApi.is_success(resp), f"修改失败: {BaseApi.json(resp)}"
        assert role_api.find_role_id(f"{role_name}_改") is not None, "修改后查不到新名字"

        # 3) 删除 + 验证无残留
        resp = role_api.delete_role(role_id)
        assert BaseApi.is_success(resp), f"删除失败: {BaseApi.json(resp)}"
        assert role_api.assert_role_gone(f"{role_name}_改"), "删除后仍能查到"

    @allure.story("角色逆向用例（yaml 数据驱动）")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("case", _neg_cases, ids=_neg_ids)
    def test_role_negative(self, role_api: RoleApi, case):
        data = render(case, ts=_ts)
        if data.get("action") == "delete":
            resp = role_api.delete_role(data["role_id"])
        else:
            payload = {k: v for k, v in data["payload"].items() if v not in (None, "")}
            resp = role_api.add_role(**payload)
        body = BaseApi.json(resp)
        assert body.get("code") == data["expected_code"], f"code 不符: {body}"
        assert data["expected_msg"] in (body.get("msg") or ""), f"msg 不符: {body}"
