# -*- coding: utf-8 -*-
"""DictApi：若依字典管理接口（字典类型）"""
import allure

from api.base_api import BaseApi


class DictApi(BaseApi):
    """字典类型接口对象：list / add / update / delete"""

    @allure.step("查询字典类型列表 GET /system/dict/type/list")
    def list_dict_types(self, page_num: int = 1, page_size: int = 10, **extra):
        params = {"pageNum": page_num, "pageSize": page_size}
        params.update(extra)  # 支持 dictName / dictType / status 筛选
        return self.get("/system/dict/type/list", params=params)

    @allure.step("新增字典类型 POST /system/dict/type")
    def add_dict_type(self, **payload):
        """新增字典类型；必填：dictName/dictType/status"""
        return self.post("/system/dict/type", json=payload)

    @allure.step("修改字典类型 PUT /system/dict/type")
    def update_dict_type(self, dict_id, **payload):
        payload["dictId"] = dict_id
        return self.put("/system/dict/type", json=payload)

    @allure.step("删除字典类型 DELETE /system/dict/type/")
    def delete_dict_type(self, dict_id):
        return self.delete(f"/system/dict/type/{dict_id}")

    def find_dict_id(self, dict_name: str):
        """按字典名查 dictId（清理数据用）；查不到返回 None"""
        resp = self.list_dict_types(page_num=1, page_size=20, dictName=dict_name)
        rows = self.json(resp).get("rows") or []
        for row in rows:
            if row.get("dictName") == dict_name:
                return row["dictId"]
        return None

    @allure.step("断言字典类型不存在 GET /system/dict/type/list?dictName=")
    def assert_dict_gone(self, dict_name: str) -> bool:
        resp = self.list_dict_types(page_num=1, page_size=20, dictName=dict_name)
        return self.json(resp).get("total", -1) == 0
