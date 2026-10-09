# -*- coding: utf-8 -*-
"""
pytest 全局 fixture 配置 - 若依接口自动化框架
============================================================
提供能力：
1. api_token：session 级登录一次，拿 Bearer token（登录态复用）
2. user_api：带 token 的用户管理接口对象
3. cleanup_users：测试账号自动清理（yield fixture，绝不留脏数据）
4. 失败证据 hook：用例失败自动把最近请求/响应报文挂到 Allure（接口版"截图"）

环境说明：
- 后端接口 : http://localhost:8080 （RUOYI_API 可覆盖）
- 账号     : admin / admin123（RUOYI_ADMIN / RUOYI_ADMIN_PWD 可覆盖）
- 认证方式 : Authorization: Bearer <token>
"""
import json
import logging
import os
import re
import time

logger = logging.getLogger(__name__)

import allure
import pytest

from api.base_api import BaseApi
from api.login_api import LoginApi
from api.user_api import UserApi
from api.role_api import RoleApi
from api.dept_api import DeptApi
from api.post_api import PostApi
from api.dict_api import DictApi
from api.config_api import ConfigApi
from api.notice_api import NoticeApi

# 后端接口地址与账号（环境变量可覆盖，Jenkins 参数化对接用）
API_BASE = os.getenv("RUOYI_API", "http://localhost:8080")
ADMIN_USER = os.getenv("RUOYI_ADMIN", "admin")
ADMIN_PWD = os.getenv("RUOYI_ADMIN_PWD", "admin123")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FAILURE_DIR = os.path.join(BASE_DIR, "reports", "failures")
os.makedirs(FAILURE_DIR, exist_ok=True)


# ============================================================
# 1. 登录态复用（session 级：整个 pytest 进程只登录一次）
# ============================================================
@pytest.fixture(scope="session")
def api_token() -> str:
    """用管理员账号登录拿 token；登录失败直接报错（环境问题要第一时间暴露）"""
    resp = LoginApi().login(ADMIN_USER, ADMIN_PWD)
    body = BaseApi.json(resp)
    token = body.get("token")
    if not token:
        raise RuntimeError(
            f"获取 token 失败: HTTP {resp.status_code} {body}\n"
            f"请确认若依后端已启动（{API_BASE}）且账号密码正确"
        )
    return token


@pytest.fixture(scope="session")
def user_api(api_token: str) -> UserApi:
    """带 token 的用户管理接口对象（清理数据 / 业务用例共用）"""
    return UserApi(token=api_token)


# 其余业务模块的 API 对象（带 token，供各自模块用例使用）
@pytest.fixture(scope="session")
def role_api(api_token: str) -> RoleApi:
    return RoleApi(token=api_token)


@pytest.fixture(scope="session")
def dept_api(api_token: str) -> DeptApi:
    return DeptApi(token=api_token)


@pytest.fixture(scope="session")
def post_api(api_token: str) -> PostApi:
    return PostApi(token=api_token)


@pytest.fixture(scope="session")
def dict_api(api_token: str) -> DictApi:
    return DictApi(token=api_token)


@pytest.fixture(scope="session")
def config_api(api_token: str) -> ConfigApi:
    return ConfigApi(token=api_token)


@pytest.fixture(scope="session")
def notice_api(api_token: str) -> NoticeApi:
    return NoticeApi(token=api_token)


# ============================================================
# 2.5 通用后置清理（多模块复用；用户模块仍用 cleanup_users）
# ============================================================
@pytest.fixture
def cleanup_items():
    """
    通用后置清理：注册 (find_func, delete_func, key) 三元组，teardown 自动删除。
    两种注册方式：
      1) (find_func, delete_func, key)  -> 先按 key 查出 id，再 delete(id)
      2) (None, delete_func, id)        -> 已持有 id，直接 delete(id)（全链路用例推荐）
    用法：
      def test_xxx(role_api, cleanup_items):
          cleanup_items.append((role_api.find_role_id, role_api.delete_role, "role_1"))
          # 或新增成功后：cleanup_items.append((None, role_api.delete_role, role_id))
    """
    registered: list = []

    yield registered

    for find_func, delete_func, key in registered:
        try:
            if find_func is None:
                resp = delete_func(key)
            else:
                obj_id = find_func(key)
                if obj_id is None:
                    print(f"[cleanup] {key} 不存在，跳过")
                    continue
                resp = delete_func(obj_id)
            body = BaseApi.json(resp)
            print(f"[cleanup] 删除 {key} -> code {body.get('code')} {body.get('msg')}")
        except Exception as e:
            print(f"[cleanup] 删除 {key} 异常: {e}")


# ============================================================
# 2. 测试账号自动清理（yield fixture，teardown 永远执行）
# ============================================================
@pytest.fixture
def cleanup_users(user_api: UserApi):
    """
    用例里登记要清理的账号名，用例结束后（无论断言成败）自动删除：
      1. 按 userName 查 userId
      2. DELETE /system/user/{userId}
    用法：
      def test_add_user(user_api, cleanup_users):
          cleanup_users.append("api_auto_xxx")
          user_api.add_user(...)
    """
    registered: list = []

    yield registered

    for username in registered:
        try:
            user_id = user_api.find_user_id(username)
            if user_id is None:
                print(f"[cleanup] {username} 不存在，跳过")
                continue
            resp = user_api.delete_user(user_id)
            body = BaseApi.json(resp)
            print(f"[cleanup] 删除 {username}(id={user_id}) -> code {body.get('code')} {body.get('msg')}")
        except Exception as e:
            # 清理失败不能让用例变红，只打日志
            print(f"[cleanup] 删除 {username} 异常: {e}")


# ============================================================
# 3. 失败证据 hook（接口版"失败截图"：最近请求/响应报文）
# ============================================================
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        log_text = BaseApi.dump_log()
        # 1) 落盘 reports/failures/<用例名>_<时间>.json
        safe_name = re.sub(r'[\\/:*?"<>|\x00-\x1f]', '_', str(item.name))
        fname = f"{safe_name}_{int(time.time())}.json"
        fpath = os.path.join(FAILURE_DIR, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(log_text)
        # 2) 挂到 Allure 报告（失败现场可追溯）
        allure.attach(
            log_text,
            name=f"{item.name} 请求/响应报文",
            attachment_type=allure.attachment_type.JSON,
        )
        logger.error("[用例失败] %s -> 失败证据: %s", item.name, fpath)
        print(f"\n[失败证据] {fpath}")
