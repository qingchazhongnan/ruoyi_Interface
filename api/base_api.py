# -*- coding: utf-8 -*-
"""
BaseApi：接口对象基类（对应 UI 框架的 base_page.py）
============================================================
职责：请求封装（get/post/put/delete）、token 注入、统一日志、失败证据留痕。
"最近一次请求/响应"保存在类变量 LAST_LOG，用例失败时由 conftest 的 hook 取走挂到 Allure。
"""
import json
import logging
import os
import time

import requests

logger = logging.getLogger(__name__)

API_BASE = os.getenv("RUOYI_API", "http://localhost:8080")


class BaseApi:
    """封装 requests，带 Bearer token 注入与最近请求/响应记录"""

    # 最近一次请求/响应留痕（类变量，全框架共享，失败 hook 读取）
    LAST_LOG = {}

    def __init__(self, token: str = ""):
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

    # ---------- 请求头 ----------
    @property
    def headers(self) -> dict:
        h = {"Content-Type": "application/json"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    # ---------- 通用请求 ----------
    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = path if path.startswith("http") else f"{API_BASE}{path}"
        kwargs.setdefault("timeout", 15)
        t0 = time.time()
        resp = self.session.request(method, url, headers=self.headers, **kwargs)
        elapsed = time.time() - t0

        # 留痕：失败时 conftest hook 会读它挂到 Allure
        BaseApi.LAST_LOG = {
            "method": method.upper(),
            "url": url,
            "request": kwargs.get("json") or kwargs.get("params") or kwargs.get("data"),
            "status": resp.status_code,
            "response": self._safe_text(resp),
            "elapsed_sec": round(elapsed, 3),
        }
        # 统一日志（同时进 logs/run.log 和控制台）
        logger.info("[API] %s %s -> %s (%.2fs)", method.upper(), url, resp.status_code, elapsed)
        if resp.status_code >= 400:
            logger.error(
                "[API] %s %s 失败: status=%s body=%s",
                method.upper(), url, resp.status_code, self._safe_text(resp)[:300],
            )
        return resp

    @staticmethod
    def _safe_text(resp: requests.Response) -> str:
        try:
            return resp.text
        except Exception:
            return "<响应读取失败>"

    # ---------- 常用方法 ----------
    def get(self, path: str, params: dict = None, **kw):
        return self._request("GET", path, params=params, **kw)

    def post(self, path: str, json=None, **kw):
        return self._request("POST", path, json=json, **kw)

    def put(self, path: str, json=None, **kw):
        return self._request("PUT", path, json=json, **kw)

    def delete(self, path: str, **kw):
        return self._request("DELETE", path, **kw)

    # ---------- 响应解析辅助 ----------
    @staticmethod
    def json(resp: requests.Response) -> dict:
        """解析若依统一返回结构 {code, msg, rows, total, token, ...}"""
        try:
            return resp.json()
        except Exception:
            return {"code": -1, "msg": f"非 JSON 响应: {resp.text[:200]}"}

    @staticmethod
    def is_success(resp: requests.Response) -> bool:
        """若依约定：code==200 即成功"""
        return BaseApi.json(resp).get("code") == 200

    @staticmethod
    def dump_log() -> str:
        """把留痕转成可读文本（失败证据）"""
        return json.dumps(BaseApi.LAST_LOG, ensure_ascii=False, indent=2, default=str)
