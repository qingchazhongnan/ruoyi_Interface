# -*- coding: utf-8 -*-
"""PostApi：若依岗位管理接口"""
import allure

from api.base_api import BaseApi


class PostApi(BaseApi):
    """岗位管理接口对象：list / add / update / delete"""

    @allure.step("查询岗位列表 GET /system/post/list")
    def list_posts(self, page_num: int = 1, page_size: int = 10, **extra):
        params = {"pageNum": page_num, "pageSize": page_size}
        params.update(extra)  # 支持 postName / postCode / status 筛选
        return self.get("/system/post/list", params=params)

    @allure.step("新增岗位 POST /system/post")
    def add_post(self, **payload):
        """新增岗位；必填：postName/postCode/postSort/status"""
        return self.post("/system/post", json=payload)

    @allure.step("修改岗位 PUT /system/post")
    def update_post(self, post_id, **payload):
        payload["postId"] = post_id
        return self.put("/system/post", json=payload)

    @allure.step("删除岗位 DELETE /system/post/")
    def delete_post(self, post_id):
        return self.delete(f"/system/post/{post_id}")

    def find_post_id(self, post_name: str):
        """按岗位名查 postId（清理数据用）；查不到返回 None"""
        resp = self.list_posts(page_num=1, page_size=20, postName=post_name)
        rows = self.json(resp).get("rows") or []
        for row in rows:
            if row.get("postName") == post_name:
                return row["postId"]
        return None

    @allure.step("断言岗位不存在 GET /system/post/list?postName=")
    def assert_post_gone(self, post_name: str) -> bool:
        resp = self.list_posts(page_num=1, page_size=20, postName=post_name)
        return self.json(resp).get("total", -1) == 0
