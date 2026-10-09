# -*- coding: utf-8 -*-
"""
登录接口用例（yaml 数据驱动）
- 成功用例断言 token 存在
- 失败用例断言 code/msg 文案
- 全部独立发请求，不依赖登录态 fixture（接口测试用例间互不影响）
"""
import allure
import pytest

from api.base_api import BaseApi
from api.login_api import LoginApi
from utils.yaml_loader import get_cases

_cases = get_cases("user_data.yaml", "login_cases")
_ids = [c["title"] for c in _cases]


@allure.feature("登录接口")
@pytest.mark.smoke
class TestLogin:
    @allure.story("登录成功")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize(
        "case",
        [c for c in _cases if c["expected_code"] == 200],
        ids=[c["title"] for c in _cases if c["expected_code"] == 200],
    )
    def test_login_success(self, case):
        resp = LoginApi().login(case["username"], case["password"])
        body = BaseApi.json(resp)
        assert body.get("code") == case["expected_code"], f"code 不符: {body}"
        assert case["expected_msg"] in (body.get("msg") or ""), f"msg 不符: {body}"
        if case.get("check_token"):
            assert body.get("token"), f"登录成功但无 token: {body}"

    @allure.story("登录失败场景")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize(
        "case",
        [c for c in _cases if c["expected_code"] != 200],
        ids=[c["title"] for c in _cases if c["expected_code"] != 200],
    )
    def test_login_fail(self, case):
        resp = LoginApi().login(case["username"], case["password"])
        body = BaseApi.json(resp)
        assert body.get("code") == case["expected_code"], f"code 不符: {body}"
        assert case["expected_msg"] in (body.get("msg") or ""), f"msg 不符: {body}"
