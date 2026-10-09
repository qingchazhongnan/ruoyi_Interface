# 若依接口自动化测试框架（ruoyi_Interface）

基于 **Pytest + requests + YAML** 的接口自动化测试模板，面向 RuoYi（若依）管理系统后端接口。
与 `ruoyi_playwright`（UI 框架）同源同构：分层思想、数据驱动、自动清理、Mock、Allure/Jenkins 一一对应。

## 一、目录结构

```
ruoyi_Interface/
├── conftest.py                # fixture：登录态(token)/清理数据/失败报文 hook
├── pytest.ini                 # pytest 配置（pytest-html + Allure 双报告）
├── requirements.txt           # 依赖
├── Jenkinsfile                # Jenkins 流水线（参数化 + Allure 发布）
├── docs/
│   └── JENKINS_SETUP.md        # Jenkins 安装 / Allure 联调指南
├── api/                       # API 对象层（对应 UI 框架的 pages/）
│   ├── base_api.py             #   基类：请求封装 + token 注入 + 失败留痕
│   ├── login_api.py            #   登录接口
│   └── user_api.py             #   用户管理接口
├── tests/                     # 用例层（对应 UI 框架的 tests/）
│   ├── test_login.py           #   登录用例（yaml 数据驱动）
│   └── test_user.py            #   新增/删除 + requests_mock Mock 演示
├── data/
│   └── user_data.yaml          #   登录/新增用户数据（{ts} 模板变量保证唯一）
├── utils/
│   └── yaml_loader.py          #   yaml 加载 + {ts} 渲染
├── scripts/
│   └── probe_api.py            #   接口契约校准脚本（后端启动后跑）
└── reports/                    # 运行生成：report.html / allure-results / failures/
```

## 二、环境准备

```bash
# 1. 创建虚拟环境并装依赖（本框架已建好 .venv）
cd D:\DSKETOP\软测相关\ruoyi_Interface
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# 2. 后端地址与账号（环境变量可覆盖，Jenkins 参数化对接用）
set RUOYI_API=http://localhost:8080
set RUOYI_ADMIN=admin
set RUOYI_ADMIN_PWD=admin123
```

> 若依验证码已关闭（`captchaEnabled: false`），登录接口无需 code/uuid。

## 三、运行用例

```bash
# 全部（11 条：登录3 + 新增3 + 删除1 + Mock4）
pytest

# 只跑登录
pytest tests/test_login.py -v

# 只跑用户接口（真实后端）
pytest -m user

# 只跑 Mock 演示（不依赖后端，可离线跑）
pytest -m mock

# 冒烟
pytest -m smoke
```

## 四、核心能力对照（与 UI 框架一一对应）

| UI 框架能力 | 接口框架对应 | 实现位置 |
|---|---|---|
| PO 分层 pages/ | **API 对象层 api/** | `base_api.py` + `login_api.py` + `user_api.py` |
| 登录态复用 storage_state | **session 级 token fixture** | `conftest.py::api_token`（整个进程只登录一次） |
| YAML 数据驱动 | 相同 + `{ts}` 模板渲染 | `data/user_data.yaml` + `utils/yaml_loader.py` |
| 失败截图 | **失败报文证据**（请求/响应 JSON 挂 Allure） | `conftest.py::pytest_runtest_makereport` hook |
| 新增用户用例 | `tests/test_user.py::TestAddUser` | 断言 code/msg + 查库确认 |
| 删除用户用例 | `tests/test_user.py::TestDeleteUser` | 造数→删→验证 total=0 |
| **自动清理脏数据** | `cleanup_users` yield fixture | teardown 按 userName 查 id 再 DELETE |
| **page.route Mock** | **requests_mock 四种写法** | `tests/test_user.py::TestUserApiMock` |
| Allure / Jenkins | 相同（Allure 步骤 + 趋势 + CI） | `Jenkinsfile` + `docs/JENKINS_SETUP.md` |

## 五、`cleanup_users` 工作原理

```python
# 用例里：
def test_add_user(user_api, cleanup_users):
    cleanup_users.append("api_auto_xxx")   # 1. 先登记（防断言失败残留）
    user_api.add_user(userName=..., ...)   # 2. 造数据

# 用例结束（无论断言成败）teardown 自动：
#   GET /system/user/list?userName=xxx -> 拿 userId
#   DELETE /system/user/{userId}        -> 删掉
```

- **重复用户名用例**（如新增 admin）在 yaml 里标 `cleanup: false`，不会误删内置账号
- 清理失败只打日志，不让用例变红

## 六、requests_mock 四种写法速查（面试考点）

```python
# 1. 整体替换返回体
requests_mock.get(url, json={"code": 200, "rows": [...], "total": 2})

# 2. 模拟网络异常
requests_mock.get(url, exc=requests.exceptions.ConnectionError("断网了"))

# 3. 模拟慢接口
def slow(request, context):
    time.sleep(1.0)
    context.status_code = 200
    return json.dumps({...})
requests_mock.get(url, text=slow)

# 4. 根据请求参数动态返回（透传改写效果）
def dynamic(request, context):
    qs = {k.lower(): v for k, v in request.qs.items()}   # 注意 qs 键是小写
    ...
requests_mock.get(url, text=dynamic)
```

> 坑点提醒：`requests_mock` 的 `request.qs` 会把参数名转成小写（`userName` → `username`）。

## 七、失败证据（接口版"失败截图"）

用例失败时自动：
1. 把**最近一次请求/响应报文**写入 `reports/failures/<用例名>_<时间>.json`
2. 作为 JSON 附件挂到 Allure 报告，失败现场可追溯

## 八、后端契约校准（重要）

`data/user_data.yaml` 里的 expected 文案基于若依 RuoYi-Vue 标准契约。
若你的后端文案不同，**启动后端后跑一次校准脚本**，按真实输出改 yaml 即可：

```bash
.venv\Scripts\python.exe scripts\probe_api.py
```
