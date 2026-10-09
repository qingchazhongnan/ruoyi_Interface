# -*- coding: utf-8 -*-
"""DeptApi：若依部门管理接口"""
import allure

from api.base_api import BaseApi


class DeptApi(BaseApi):
    """部门管理接口对象：list / add / update / delete
    注意：部门列表接口返回结构特殊——数据在 data 字段（数组），不是 rows/total。
    """

    @allure.step("查询部门列表 GET /system/dept/list")
    def list_depts(self, **extra):
        """部门列表不分页，筛选条件直接拼 params"""
        return self.get("/system/dept/list", params=extra)

    @allure.step("新增部门 POST /system/dept")
    def add_dept(self, **payload):
        """新增部门；必填：parentId/deptName/orderNum/status"""
        return self.post("/system/dept", json=payload)

    @allure.step("修改部门 PUT /system/dept")
    def update_dept(self, dept_id, **payload):
        payload["deptId"] = dept_id
        return self.put("/system/dept", json=payload)

    @allure.step("删除部门 DELETE /system/dept/")
    def delete_dept(self, dept_id):
        return self.delete(f"/system/dept/{dept_id}")

    def find_dept_id(self, dept_name: str):
        """按部门名查 deptId（清理数据用）；查不到返回 None"""
        resp = self.list_depts(deptName=dept_name)
        rows = self.json(resp).get("data") or []  # 注意：部门列表用 data 字段
        for row in rows:
            if row.get("deptName") == dept_name:
                return row["deptId"]
        return None

    @allure.step("断言部门不存在 GET /system/dept/list?deptName=")
    def assert_dept_gone(self, dept_name: str) -> bool:
        resp = self.list_depts(deptName=dept_name)
        rows = self.json(resp).get("data") or []
        return not any(r.get("deptName") == dept_name for r in rows)
