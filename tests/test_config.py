# -*- coding: utf-8 -*-
"""
参数设置接口用例
- 正向全链路：增→查→改→删→验证无残留（注意 configType 用 "N"，"Y" 视为内置参数禁删）
- 逆向数据驱动：缺必填 / 重复 / 删除不存在
- 业务逆向：删除内置参数应失败（先查出内置参数 id 再删，不产生新数据）
"""
import time

import allure
import pytest

from api.base_api import BaseApi
from api.config_api import ConfigApi
from utils.yaml_loader import get_cases, render

_neg_cases = get_cases("config_data.yaml", "negative_cases")
_neg_ids = [c["title"] for c in _neg_cases]
_ts = int(time.time())


@allure.feature("参数设置接口")
@pytest.mark.user
class TestConfig:
    @allure.story("参数增删改查全链路")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_config_full_flow(self, config_api: ConfigApi, cleanup_items):
        config_name = f"config_{_ts}"
        config_key = f"config.key.{_ts}"

        # 1) 新增（configType 必须用 "N"，否则视为内置参数删不掉）
        resp = config_api.add_config(configName=config_name, configKey=config_key,
                                     configValue="1", configType="N")
        assert BaseApi.is_success(resp), f"新增失败: {BaseApi.json(resp)}"
        config_id = config_api.find_config_id(config_name)
        assert config_id is not None, "新增后查询不到 configId"
        cleanup_items.append((None, config_api.delete_config, config_id))

        # 2) 修改
        resp = config_api.update_config(config_id, configName=f"{config_name}_改",
                                        configKey=config_key, configValue="2", configType="N")
        assert BaseApi.is_success(resp), f"修改失败: {BaseApi.json(resp)}"
        assert config_api.find_config_id(f"{config_name}_改") is not None, "修改后查不到新名字"

        # 3) 删除 + 验证
        resp = config_api.delete_config(config_id)
        assert BaseApi.is_success(resp), f"删除失败: {BaseApi.json(resp)}"
        assert config_api.assert_config_gone(f"{config_name}_改"), "删除后仍能查到"

    @allure.story("参数逆向用例（yaml 数据驱动）")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.parametrize("case", _neg_cases, ids=_neg_ids)
    def test_config_negative(self, config_api: ConfigApi, case):
        data = render(case, ts=_ts)
        if data.get("action") == "delete":
            resp = config_api.delete_config(data["config_id"])
        else:
            payload = {k: v for k, v in data["payload"].items() if v not in (None, "")}
            resp = config_api.add_config(**payload)
        body = BaseApi.json(resp)
        assert body.get("code") == data["expected_code"], f"code 不符: {body}"
        assert data["expected_msg"] in (body.get("msg") or ""), f"msg 不符: {body}"

    @allure.story("删除内置参数应失败（不产生新数据）")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_inner_config_failed(self, config_api: ConfigApi):
        """内置参数（configType=Y）受保护，删除应返回 500 内置参数不能删除"""
        resp = config_api.list_configs(page_num=1, page_size=50, configKey="sys.account")
        rows = BaseApi.json(resp).get("rows") or []
        inner = [r for r in rows if r.get("configType") == "Y"]
        assert inner, "未找到内置参数（测试前提不成立）"

        resp = config_api.delete_config(inner[0]["configId"])
        body = BaseApi.json(resp)
        assert body.get("code") == 500, f"内置参数竟被删掉: {body}"
        assert "内置参数" in (body.get("msg") or ""), f"文案不符: {body}"
