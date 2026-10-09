# -*- coding: utf-8 -*-
"""
字典类型管理接口用例
- 正向全链路：增→查→改→删→验证无残留
- 逆向数据驱动：缺必填 / 重复 / 删除不存在
"""
import time

import allure
import pytest

from api.base_api import BaseApi
from api.dict_api import DictApi
from utils.yaml_loader import get_cases, render

_neg_cases = get_cases("dict_data.yaml", "negative_cases")
_neg_ids = [c["title"] for c in _neg_cases]
_ts = int(time.time())


@allure.feature("字典类型管理接口")
@pytest.mark.user
class TestDict:
    @allure.story("字典类型增删改查全链路")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_dict_full_flow(self, dict_api: DictApi, cleanup_items):
        dict_name = f"dict_{_ts}"
        dict_type = f"dict_type_{_ts}"

        # 1) 新增
        resp = dict_api.add_dict_type(dictName=dict_name, dictType=dict_type, status="0")
        assert BaseApi.is_success(resp), f"新增失败: {BaseApi.json(resp)}"
        dict_id = dict_api.find_dict_id(dict_name)
        assert dict_id is not None, "新增后查询不到 dictId"
        cleanup_items.append((None, dict_api.delete_dict_type, dict_id))

        # 2) 修改
        resp = dict_api.update_dict_type(dict_id, dictName=f"{dict_name}_改",
                                         dictType=dict_type, status="0")
        assert BaseApi.is_success(resp), f"修改失败: {BaseApi.json(resp)}"
        assert dict_api.find_dict_id(f"{dict_name}_改") is not None, "修改后查不到新名字"

        # 3) 删除 + 验证
        resp = dict_api.delete_dict_type(dict_id)
        assert BaseApi.is_success(resp), f"删除失败: {BaseApi.json(resp)}"
        assert dict_api.assert_dict_gone(f"{dict_name}_改"), "删除后仍能查到"

    @allure.story("字典类型逆向用例（yaml 数据驱动）")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("case", _neg_cases, ids=_neg_ids)
    def test_dict_negative(self, dict_api: DictApi, case):
        data = render(case, ts=_ts)
        if data.get("action") == "delete":
            resp = dict_api.delete_dict_type(data["dict_id"])
        else:
            payload = {k: v for k, v in data["payload"].items() if v not in (None, "")}
            resp = dict_api.add_dict_type(**payload)
        body = BaseApi.json(resp)
        assert body.get("code") == data["expected_code"], f"code 不符: {body}"
        assert data["expected_msg"] in (body.get("msg") or ""), f"msg 不符: {body}"
