# -*- coding: utf-8 -*-
"""NoticeApi：若依通知公告接口"""
import allure

from api.base_api import BaseApi


class NoticeApi(BaseApi):
    """通知公告接口对象：list / add / update / delete"""

    @allure.step("查询公告列表 GET /system/notice/list")
    def list_notices(self, page_num: int = 1, page_size: int = 10, **extra):
        params = {"pageNum": page_num, "pageSize": page_size}
        params.update(extra)  # 支持 noticeTitle / noticeType / status 筛选
        return self.get("/system/notice/list", params=params)

    @allure.step("新增公告 POST /system/notice")
    def add_notice(self, **payload):
        """新增公告；必填：noticeTitle/noticeType/noticeContent/status"""
        return self.post("/system/notice", json=payload)

    @allure.step("修改公告 PUT /system/notice")
    def update_notice(self, notice_id, **payload):
        payload["noticeId"] = notice_id
        return self.put("/system/notice", json=payload)

    @allure.step("删除公告 DELETE /system/notice/")
    def delete_notice(self, notice_id):
        return self.delete(f"/system/notice/{notice_id}")

    def find_notice_id(self, notice_title: str):
        """按公告标题查 noticeId（清理数据用）；查不到返回 None"""
        resp = self.list_notices(page_num=1, page_size=20, noticeTitle=notice_title)
        rows = self.json(resp).get("rows") or []
        for row in rows:
            if row.get("noticeTitle") == notice_title:
                return row["noticeId"]
        return None

    @allure.step("断言公告不存在 GET /system/notice/list?noticeTitle=")
    def assert_notice_gone(self, notice_title: str) -> bool:
        resp = self.list_notices(page_num=1, page_size=20, noticeTitle=notice_title)
        return self.json(resp).get("total", -1) == 0
