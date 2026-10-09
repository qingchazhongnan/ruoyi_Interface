# -*- coding: utf-8 -*-
"""
用户管理接口用例 + 接口 Mock 演示（面试高频考点）
- TestAddUser    : 新增用户（yaml 数据驱动，{ts} 渲染保证唯一，后置自动清理）
- TestDeleteUser : 删除用户（先造数据再删，验证 total=0）
- TestUserApiMock: requests_mock 四种典型写法（不依赖真实后端）
"""
import json
import time

import allure
import pytest
import requests

from api.base_api import BaseApi
from api.user_api import UserApi
from utils.yaml_loader import get_cases, render

_add_cases = get_cases("user_data.yaml", "add_user_cases")
_add_ids = [c["title"] for c in _add_cases]
_ts = int(time.time())  # 本次运行的时间戳，保证账号唯一


# ============================================================
# 1. 新增用户用例（数据驱动 + 自动清理）
# ============================================================
@allure.feature("用户管理接口")
@pytest.mark.user
@pytest.mark.parametrize("case", _add_cases, ids=_add_ids)
class TestAddUser:
    @allure.story("新增用户")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_user(self, user_api: UserApi, cleanup_users, case):
        data = render(case, ts=_ts)  # 渲染 {ts} 占位符，账号唯一
        fields = {k: v for k, v in data.items()
                  if k not in ("title", "expected_code", "expected_msg", "cleanup")}

        # 需要清理的账号先登记（后置自动删；重复用户名用例不登记，避免误删内置账号）
        if data.get("cleanup", True):
            cleanup_users.append(data["userName"])

        resp = user_api.add_user(**fields)
        body = BaseApi.json(resp)
        assert body.get("code") == data["expected_code"], f"code 不符: {body}"
        assert data["expected_msg"] in (body.get("msg") or ""), f"msg 不符: {body}"

        # 新增成功的话，再查一次确认数据真的落了库
        if data.get("expected_code") == 200:
            assert user_api.find_user_id(data["userName"]) is not None, "新增成功但查询不到"


# ============================================================
# 2. 删除用户用例（先造数据，再删，最后验证无残留）
# ============================================================
@allure.feature("用户管理接口")
@pytest.mark.user
class TestDeleteUser:
    @allure.story("删除用户")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_user(self, user_api: UserApi, cleanup_users):
        # 前置：直接调接口造一个用户（比走 UI 快且稳定）
        username = f"api_del_{_ts}"
        cleanup_users.append(username)  # 先登记，用例失败也能清理
        resp = user_api.add_user(
            userName=username, nickName="待删除用户", password="Test@123456",
            deptId=103, roleIds=[2], postIds=[], phonenumber="13800000009",
            email="del@test.com", sex="0", status="0",
        )
        assert BaseApi.is_success(resp), f"造数据失败: {BaseApi.json(resp)}"

        user_id = user_api.find_user_id(username)
        assert user_id is not None, "造数据后查询不到 userId"

        # 核心步骤：删除
        resp = user_api.delete_user(user_id)
        body = BaseApi.json(resp)
        assert body.get("code") == 200, f"删除失败: {body}"
        assert "成功" in (body.get("msg") or "") or body.get("code") == 200

        # 后置校验：再查，total 必须为 0
        assert user_api.assert_user_gone(username), f"删除后仍能查到 {username}"


# ============================================================
# 3. requests_mock 接口 Mock 演示（面试高频考点，不依赖真实后端）
# ============================================================
MOCK_LIST_URL = "http://localhost:8080/system/user/list"
FAKE_ROWS = [
    {"userId": 90001, "userName": "mock_zhangsan", "nickName": "Mock张三"},
    {"userId": 90002, "userName": "mock_lisi", "nickName": "Mock李四"},
]


@allure.feature("接口 Mock 演示")
@pytest.mark.mock
class TestUserApiMock:
    @allure.story("Mock 四种写法")
    @allure.severity(allure.severity_level.NORMAL)
    def test_mock_user_list_return_fake_data(self, requests_mock):
        """写法1：整体替换返回体（最常见）"""
        requests_mock.get(MOCK_LIST_URL, json={"code": 200, "rows": FAKE_ROWS, "total": 2})
        api = UserApi(token="fake-token")  # 直接 new，不走真实登录
        body = BaseApi.json(api.list_users())
        assert body["total"] == 2
        assert body["rows"][0]["userName"] == "mock_zhangsan"

    def test_mock_network_error(self, requests_mock):
        """写法2：模拟网络异常（接口挂了/断网）"""
        requests_mock.get(MOCK_LIST_URL,
                          exc=requests.exceptions.ConnectionError("模拟连接失败"))
        api = UserApi(token="fake-token")
        with pytest.raises(requests.exceptions.ConnectionError):
            api.list_users()

    def test_mock_latency(self, requests_mock):
        """写法3：模拟慢接口（测超时/loading 场景）"""
        def slow_cb(request, context):
            time.sleep(1.0)  # 模拟 1 秒延迟
            context.status_code = 200
            return json.dumps({"code": 200, "rows": FAKE_ROWS, "total": 2})

        requests_mock.get(MOCK_LIST_URL, text=slow_cb)
        api = UserApi(token="fake-token")
        t0 = time.time()
        api.list_users()
        assert time.time() - t0 >= 1.0, "模拟延迟未生效"

    def test_mock_partial_modify_response(self, requests_mock):
        """写法4：根据请求参数动态返回（模拟"透传改写"：不同查询条件给不同数据）"""
        def dynamic_cb(request, context):
            context.status_code = 200
            # 注意：requests_mock 的 request.qs 会把参数名转小写（userName -> username）
            qs = {k.lower(): v for k, v in request.qs.items()}
            username = (qs.get("username") or [""])[0]
            rows = [r for r in FAKE_ROWS if r["userName"] == username] if username else FAKE_ROWS
            return json.dumps({"code": 200, "rows": rows, "total": len(rows)})

        requests_mock.get(MOCK_LIST_URL, text=dynamic_cb)
        api = UserApi(token="fake-token")

        # 带 userName 过滤 -> 只返回张三
        body = BaseApi.json(api.list_users(userName="mock_zhangsan"))
        assert body["total"] == 1 and body["rows"][0]["userName"] == "mock_zhangsan"

        # 不带过滤 -> 返回全部假数据
        body = BaseApi.json(api.list_users())
        assert body["total"] == 2
