# -*- coding: utf-8 -*-
"""ConfigApi：若依参数设置接口"""
import allure

from api.base_api import BaseApi


class ConfigApi(BaseApi):
    """参数设置接口对象：list / add / update / delete
    注意：configType="Y" 会被后端视为"内置参数"禁止删除；
         正向用例请用 configType="N"（普通参数可增删改）。
    """

    @allure.step("查询参数列表 GET /system/config/list")
    def list_configs(self, page_num: int = 1, page_size: int = 10, **extra):
        params = {"pageNum": page_num, "pageSize": page_size}
        params.update(extra)  # 支持 configName / configKey / configType 筛选
        return self.get("/system/config/list", params=params)

    @allure.step("新增参数 POST /system/config")
    def add_config(self, **payload):
        """新增参数；必填：configName/configKey/configValue/configType"""
        return self.post("/system/config", json=payload)

    @allure.step("修改参数 PUT /system/config")
    def update_config(self, config_id, **payload):
        payload["configId"] = config_id
        return self.put("/system/config", json=payload)

    @allure.step("删除参数 DELETE /system/config/")
    def delete_config(self, config_id):
        return self.delete(f"/system/config/{config_id}")

    def find_config_id(self, config_name: str):
        """按参数名查 configId（清理数据用）；查不到返回 None"""
        resp = self.list_configs(page_num=1, page_size=20, configName=config_name)
        rows = self.json(resp).get("rows") or []
        for row in rows:
            if row.get("configName") == config_name:
                return row["configId"]
        return None

    @allure.step("断言参数不存在 GET /system/config/list?configName=")
    def assert_config_gone(self, config_name: str) -> bool:
        resp = self.list_configs(page_num=1, page_size=20, configName=config_name)
        return self.json(resp).get("total", -1) == 0
