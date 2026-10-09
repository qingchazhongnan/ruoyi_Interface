# -*- coding: utf-8 -*-
"""
岗位管理接口用例
- 正向全链路：增→查→改→删→验证无残留
- 逆向数据驱动：缺必填 / 重复 / 删除不存在
"""
import time

import allure
import pytest

from api.base_api import BaseApi
from api.post_api import PostApi
from utils.yaml_loader import get_cases, render

_neg_cases = get_cases("post_data.yaml", "negative_cases")
_neg_ids = [c["title"] for c in _neg_cases]
_ts = int(time.time())


@allure.feature("岗位管理接口")
@pytest.mark.user
class TestPost:
    @allure.story("岗位增删改查全链路")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_post_full_flow(self, post_api: PostApi, cleanup_items):
        post_name = f"post_{_ts}"
        post_code = f"post_code_{_ts}"

        # 1) 新增
        resp = post_api.add_post(postName=post_name, postCode=post_code,
                                 postSort=9, status="0")
        assert BaseApi.is_success(resp), f"新增失败: {BaseApi.json(resp)}"
        post_id = post_api.find_post_id(post_name)
        assert post_id is not None, "新增后查询不到 postId"
        cleanup_items.append((None, post_api.delete_post, post_id))

        # 2) 修改
        resp = post_api.update_post(post_id, postName=f"{post_name}_改",
                                    postCode=post_code, postSort=9, status="0")
        assert BaseApi.is_success(resp), f"修改失败: {BaseApi.json(resp)}"
        assert post_api.find_post_id(f"{post_name}_改") is not None, "修改后查不到新名字"

        # 3) 删除 + 验证
        resp = post_api.delete_post(post_id)
        assert BaseApi.is_success(resp), f"删除失败: {BaseApi.json(resp)}"
        assert post_api.assert_post_gone(f"{post_name}_改"), "删除后仍能查到"

    @allure.story("岗位逆向用例（yaml 数据驱动）")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("case", _neg_cases, ids=_neg_ids)
    def test_post_negative(self, post_api: PostApi, case):
        data = render(case, ts=_ts)
        if data.get("action") == "delete":
            resp = post_api.delete_post(data["post_id"])
        else:
            payload = {k: v for k, v in data["payload"].items() if v not in (None, "")}
            resp = post_api.add_post(**payload)
        body = BaseApi.json(resp)
        assert body.get("code") == data["expected_code"], f"code 不符: {body}"
        assert data["expected_msg"] in (body.get("msg") or ""), f"msg 不符: {body}"
