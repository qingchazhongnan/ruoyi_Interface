# -*- coding: utf-8 -*-
"""RoleApi：若依角色管理接口"""
import allure

from api.base_api import BaseApi


class RoleApi(BaseApi):
    """角色管理接口对象：list / add / update / delete"""

    @allure.step("查询角色列表 GET /system/role/list")
    def list_roles(self, page_num: int = 1, page_size: int = 10, **extra):
        params = {"pageNum": page_num, "pageSize": page_size}
        params.update(extra)  # 支持 roleName / roleKey 筛选
        return self.get("/system/role/list", params=params)

    @allure.step("新增角色 POST /system/role")
    def add_role(self, **payload):
        """新增角色；必填：roleName/roleKey/roleSort/status/menuIds"""
        return self.post("/system/role", json=payload)

    @allure.step("修改角色 PUT /system/role")
    def update_role(self, role_id, **payload):
        payload["roleId"] = role_id
        return self.put("/system/role", json=payload)

    @allure.step("删除角色 DELETE /system/role/")
    def delete_role(self, role_id):
        return self.delete(f"/system/role/{role_id}")

    def find_role_id(self, role_name: str):
        """按角色名查 roleId（清理数据用）；查不到返回 None"""
        resp = self.list_roles(page_num=1, page_size=20, roleName=role_name)
        rows = self.json(resp).get("rows") or []
        for row in rows:
            if row.get("roleName") == role_name:
                return row["roleId"]
        return None

    @allure.step("断言角色不存在 GET /system/role/list?roleName=")
    def assert_role_gone(self, role_name: str) -> bool:
        resp = self.list_roles(page_num=1, page_size=20, roleName=role_name)
        return self.json(resp).get("total", -1) == 0
