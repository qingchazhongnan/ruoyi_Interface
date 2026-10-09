# -*- coding: utf-8 -*-
"""
若依后端接口契约校准脚本
============================================================
用途：后端启动后跑一次本脚本，把真实的 code/msg 文案打出来，
     与 data/user_data.yaml 里的 expected 对齐（改文案只改 yaml，不动代码）。

用法（在项目 .venv 下）：
    .venv\\Scripts\\python.exe scripts\\probe_api.py
"""
import json

import requests

API = "http://localhost:8080"
s = requests.Session()


def show(title, r):
    try:
        body = r.json()
    except Exception:
        body = r.text[:300]
    print(f"\n### {title}")
    print(f"HTTP {r.status_code} | body: {json.dumps(body, ensure_ascii=False)[:400]}")


if __name__ == "__main__":
    print(f"校准目标: {API}（确保若依后端已启动）")

    show("GET /captchaImage（验证码开关）", s.get(f"{API}/captchaImage", timeout=10))

    r = s.post(f"{API}/login", json={"username": "admin", "password": "admin123"}, timeout=10)
    show("POST /login 正确账号密码", r)
    token = r.json().get("token")

    show("POST /login 密码错误", s.post(f"{API}/login", json={"username": "admin", "password": "wrong"}, timeout=10))
    show("POST /login 用户名为空", s.post(f"{API}/login", json={"username": "", "password": ""}, timeout=10))
    show("POST /login 无 body", s.post(f"{API}/login", timeout=10))

    if token:
        h = {"Authorization": f"Bearer {token}"}
        show("GET /system/user/list 带token", s.get(f"{API}/system/user/list", params={"pageNum": 1, "pageSize": 5}, headers=h, timeout=10))

        name = "api_probe_001"
        payload = {
            "userName": name, "nickName": "探测用户", "password": "Test@123456",
            "phonenumber": "13800138000", "email": "probe@test.com",
            "sex": "0", "status": "0", "deptId": 103, "roleIds": [2], "postIds": [],
        }
        show("POST /system/user 新增用户", s.post(f"{API}/system/user", json=payload, headers=h, timeout=10))
        show("POST /system/user 重复用户名", s.post(f"{API}/system/user", json=payload, headers=h, timeout=10))

        r = s.get(f"{API}/system/user/list", params={"pageNum": 1, "pageSize": 10, "userName": name}, headers=h, timeout=10)
        show("GET /system/user/list?userName 查id", r)
        rows = r.json().get("rows", [])
        uid = rows[0]["userId"] if rows else None
        if uid:
            show("DELETE /system/user/{id}", s.delete(f"{API}/system/user/{uid}", headers=h, timeout=10))
            r = s.get(f"{API}/system/user/list", params={"pageNum": 1, "pageSize": 10, "userName": name}, headers=h, timeout=10)
            show("确认删除后 total", r)
