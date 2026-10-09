# -*- coding: utf-8 -*-
"""
通知公告接口用例
- 正向全链路：增→查→改→删→验证无残留
- 逆向数据驱动：缺必填 / 删除不存在
"""
import time

import allure
import pytest

from api.base_api import BaseApi
from api.notice_api import NoticeApi
from utils.yaml_loader import get_cases, render

_neg_cases = get_cases("notice_data.yaml", "negative_cases")
_neg_ids = [c["title"] for c in _neg_cases]
_ts = int(time.time())


@allure.feature("通知公告接口")
@pytest.mark.user
class TestNotice:
    @allure.story("公告增删改查全链路")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_notice_full_flow(self, notice_api: NoticeApi, cleanup_items):
        notice_title = f"notice_{_ts}"

        # 1) 新增
        resp = notice_api.add_notice(noticeTitle=notice_title, noticeType="1",
                                     noticeContent=f"公告内容_{_ts}", status="0")
        assert BaseApi.is_success(resp), f"新增失败: {BaseApi.json(resp)}"
        notice_id = notice_api.find_notice_id(notice_title)
        assert notice_id is not None, "新增后查询不到 noticeId"
        cleanup_items.append((None, notice_api.delete_notice, notice_id))

        # 2) 修改
        resp = notice_api.update_notice(notice_id, noticeTitle=f"{notice_title}_改",
                                        noticeType="1", noticeContent="改后内容", status="0")
        assert BaseApi.is_success(resp), f"修改失败: {BaseApi.json(resp)}"
        assert notice_api.find_notice_id(f"{notice_title}_改") is not None, "修改后查不到新标题"

        # 3) 删除 + 验证
        resp = notice_api.delete_notice(notice_id)
        assert BaseApi.is_success(resp), f"删除失败: {BaseApi.json(resp)}"
        assert notice_api.assert_notice_gone(f"{notice_title}_改"), "删除后仍能查到"

    @allure.story("公告逆向用例（yaml 数据驱动）")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("case", _neg_cases, ids=_neg_ids)
    def test_notice_negative(self, notice_api: NoticeApi, case):
        data = render(case, ts=_ts)
        if data.get("action") == "delete":
            resp = notice_api.delete_notice(data["notice_id"])
        else:
            payload = {k: v for k, v in data["payload"].items() if v not in (None, "")}
            resp = notice_api.add_notice(**payload)
        body = BaseApi.json(resp)
        assert body.get("code") == data["expected_code"], f"code 不符: {body}"
        assert data["expected_msg"] in (body.get("msg") or ""), f"msg 不符: {body}"
