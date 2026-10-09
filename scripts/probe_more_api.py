# -*- coding: utf-8 -*-
"""
扩展契约校准脚本：角色/部门/岗位/字典/参数/公告 六模块
用途：把真实 code/msg 打出来，用于校准各模块 yaml/xlsx 的 expected 文案
用法：.venv\\Scripts\\python.exe scripts\\probe_more_api.py
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
    print(f"HTTP {r.status_code} | body: {json.dumps(body, ensure_ascii=False)[:300]}")


def main():
    print(f"校准目标: {API}")
    r = s.post(f"{API}/login", json={"username": "admin", "password": "admin123"}, timeout=10)
    token = r.json().get("token")
    if not token:
        print("登录失败，退出")
        return
    h = {"Authorization": f"Bearer {token}"}

    # ---------- 角色 ----------
    print("\n========== 角色管理 ==========")
    role_payload = {"roleName": "probe角色", "roleKey": "probe_role", "roleSort": 9,
                    "status": "0", "menuIds": [1], "remark": ""}
    show("POST /system/role 新增角色", s.post(f"{API}/system/role", json=role_payload, headers=h, timeout=10))
    show("POST /system/role 重复 roleKey", s.post(f"{API}/system/role", json=role_payload, headers=h, timeout=10))
    r = s.get(f"{API}/system/role/list", params={"pageNum": 1, "pageSize": 10, "roleName": "probe角色"}, headers=h, timeout=10)
    show("GET /system/role/list 查角色列表", r)
    rows = r.json().get("rows", [])
    rid = rows[0]["roleId"] if rows else None
    if rid:
        role_payload2 = dict(role_payload, roleName="probe角色改", roleId=rid)
        show("PUT /system/role 修改角色", s.put(f"{API}/system/role", json=role_payload2, headers=h, timeout=10))
        show(f"DELETE /system/role/{rid} 删除角色", s.delete(f"{API}/system/role/{rid}", headers=h, timeout=10))
    show("DELETE /system/role/999999 删除不存在角色", s.delete(f"{API}/system/role/999999", headers=h, timeout=10))
    show("POST /system/role 缺少 roleName", s.post(f"{API}/system/role", json={"roleKey": "x", "roleSort": 1, "status": "0"}, headers=h, timeout=10))

    # ---------- 部门 ----------
    print("\n========== 部门管理 ==========")
    dept_payload = {"parentId": 103, "deptName": "probe部门", "orderNum": 9, "status": "0"}
    show("POST /system/dept 新增部门", s.post(f"{API}/system/dept", json=dept_payload, headers=h, timeout=10))
    r = s.get(f"{API}/system/dept/list", params={"deptName": "probe部门"}, headers=h, timeout=10)
    show("GET /system/dept/list 查部门列表", r)
    rows = r.json().get("rows", [])
    did = rows[0]["deptId"] if rows else None
    if did:
        show(f"DELETE /system/dept/{did} 删除部门", s.delete(f"{API}/system/dept/{did}", headers=h, timeout=10))
    show("POST /system/dept 缺少 deptName", s.post(f"{API}/system/dept", json={"parentId": 103, "orderNum": 1, "status": "0"}, headers=h, timeout=10))

    # ---------- 岗位 ----------
    print("\n========== 岗位管理 ==========")
    post_payload = {"postName": "probe岗位", "postCode": "probe_post", "postSort": 9, "status": "0"}
    show("POST /system/post 新增岗位", s.post(f"{API}/system/post", json=post_payload, headers=h, timeout=10))
    show("POST /system/post 重复 postCode", s.post(f"{API}/system/post", json=post_payload, headers=h, timeout=10))
    r = s.get(f"{API}/system/post/list", params={"pageNum": 1, "pageSize": 10, "postName": "probe岗位"}, headers=h, timeout=10)
    show("GET /system/post/list 查岗位列表", r)
    rows = r.json().get("rows", [])
    pid = rows[0]["postId"] if rows else None
    if pid:
        show(f"DELETE /system/post/{pid} 删除岗位", s.delete(f"{API}/system/post/{pid}", headers=h, timeout=10))
    show("POST /system/post 缺少 postName", s.post(f"{API}/system/post", json={"postCode": "x", "postSort": 1, "status": "0"}, headers=h, timeout=10))

    # ---------- 字典类型 ----------
    print("\n========== 字典类型 ==========")
    dict_payload = {"dictName": "probe字典", "dictType": "probe_dict", "status": "0"}
    show("POST /system/dict/type 新增字典类型", s.post(f"{API}/system/dict/type", json=dict_payload, headers=h, timeout=10))
    show("POST /system/dict/type 重复 dictType", s.post(f"{API}/system/dict/type", json=dict_payload, headers=h, timeout=10))
    r = s.get(f"{API}/system/dict/type/list", params={"pageNum": 1, "pageSize": 10, "dictName": "probe字典"}, headers=h, timeout=10)
    show("GET /system/dict/type/list 查字典类型列表", r)
    rows = r.json().get("rows", [])
    dctid = rows[0]["dictId"] if rows else None
    if dctid:
        show(f"DELETE /system/dict/type/{dctid} 删除字典类型", s.delete(f"{API}/system/dict/type/{dctid}", headers=h, timeout=10))
    show("POST /system/dict/type 缺少 dictType", s.post(f"{API}/system/dict/type", json={"dictName": "x", "status": "0"}, headers=h, timeout=10))

    # ---------- 参数设置 ----------
    print("\n========== 参数设置 ==========")
    cfg_payload = {"configName": "probe参数", "configKey": "probe.config.key", "configValue": "1", "configType": "Y"}
    show("POST /system/config 新增参数", s.post(f"{API}/system/config", json=cfg_payload, headers=h, timeout=10))
    show("POST /system/config 重复 configKey", s.post(f"{API}/system/config", json=cfg_payload, headers=h, timeout=10))
    r = s.get(f"{API}/system/config/list", params={"pageNum": 1, "pageSize": 10, "configName": "probe参数"}, headers=h, timeout=10)
    show("GET /system/config/list 查参数列表", r)
    rows = r.json().get("rows", [])
    cid = rows[0]["configId"] if rows else None
    if cid:
        show(f"DELETE /system/config/{cid} 删除参数", s.delete(f"{API}/system/config/{cid}", headers=h, timeout=10))
    show("POST /system/config 缺少 configKey", s.post(f"{API}/system/config", json={"configName": "x", "configValue": "1", "configType": "Y"}, headers=h, timeout=10))

    # ---------- 通知公告 ----------
    print("\n========== 通知公告 ==========")
    ntc_payload = {"noticeTitle": "probe公告", "noticeType": "1", "noticeContent": "probe内容", "status": "0"}
    show("POST /system/notice 新增公告", s.post(f"{API}/system/notice", json=ntc_payload, headers=h, timeout=10))
    r = s.get(f"{API}/system/notice/list", params={"pageNum": 1, "pageSize": 10, "noticeTitle": "probe公告"}, headers=h, timeout=10)
    show("GET /system/notice/list 查公告列表", r)
    rows = r.json().get("rows", [])
    nid = rows[0]["noticeId"] if rows else None
    if nid:
        show(f"DELETE /system/notice/{nid} 删除公告", s.delete(f"{API}/system/notice/{nid}", headers=h, timeout=10))
    show("POST /system/notice 缺少 noticeTitle", s.post(f"{API}/system/notice", json={"noticeType": "1", "noticeContent": "x", "status": "0"}, headers=h, timeout=10))


if __name__ == "__main__":
    main()
