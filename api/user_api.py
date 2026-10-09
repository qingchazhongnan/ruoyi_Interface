# -*- coding: utf-8 -*-
"""UserApi：若依用户管理接口（对应 UI 框架的 user_page.py）"""
import allure

from api.base_api import BaseApi


class UserApi(BaseApi):
    """用户管理接口对象：list / add / get / delete"""

    @allure.step("查询用户列表 GET /system/user/list")
    def list_users(self, page_num: int = 1, page_size: int = 10, **extra):
        params = {"pageNum": page_num, "pageSize": page_size}
        params.update(extra)  # 支持 userName / phonenumber 等筛选
        return self.get("/system/user/list", params=params)

    @allure.step("新增用户 POST /system/user（{userName}）")
    def add_user(self, **payload):
        """新增用户；必填：userName/nickName/password，可选：deptId/roleIds/..."""
        return self.post("/system/user", json=payload)

    @allure.step("查询用户详情 GET /system/user/{user_id}")
    def get_user(self, user_id):
        return self.get(f"/system/user/{user_id}")

    @allure.step("删除用户 DELETE /system/user/{user_id}")
    def delete_user(self, user_id):
        return self.delete(f"/system/user/{user_id}")

    def find_user_id(self, username: str) -> int:
        """按用户名查 userId（清理数据用）；查不到返回 None"""
        resp = self.list_users(page_num=1, page_size=10, userName=username)
        rows = self.json(resp).get("rows") or []
        for row in rows:
            if row.get("userName") == username:
                return row["userId"]
        return None

    @allure.step("断言用户不存在 GET /system/user/list?userName={username}")
    def assert_user_gone(self, username: str) -> bool:
        """删除后校验：按用户名查 total == 0"""
        resp = self.list_users(page_num=1, page_size=10, userName=username)
        total = self.json(resp).get("total", -1)
        return total == 0
