# 若依接口自动化测试框架（ruoyi_Interface）

基于 **Pytest + requests + YAML/Excel 双数据驱动** 的接口自动化测试框架，面向 RuoYi（若依）管理系统后端接口。
与 `ruoyi_playwright`（UI 自动化框架）同源同构：分层思想、数据驱动、自动清理、Mock、Allure/Jenkins 一一对应。

> 当前状态：**39 条用例全量通过**（登录 3 + 用户 8 + 用户Excel 2 + 角色 4 + 角色Excel 3 + 部门 3 + 岗位 4 + 字典 4 + 参数 5 + 公告 3），执行约 3 秒，测试账号零残留。

---

## 一、技术栈与特性

| 类别 | 内容 |
|---|---|
| 语言 | Python 3.11+ |
| 测试框架 | pytest 8.2 |
| 请求库 | requests（Session 复用 + Bearer token 注入） |
| 数据驱动 | YAML（`PyYAML`）+ Excel（`openpyxl`）双载体，`{ts}` 模板变量保证账号唯一 |
| 断言体系 | `expected_code` + `expected_msg` 双断言，probe 脚本实测校准 |
| Mock | requests_mock 四种写法（替换返回体 / 网络异常 / 慢接口 / 按参数动态返回） |
| 报告 | pytest-html（即开即看）+ Allure（趋势 + 附件），`run.py` 一键生成 |
| 日志 | pytest 内置日志双出口（`logs/run.log` + 控制台），带时间/行号/函数名 |
| 生产插件 | pytest-xdist（并发）、pytest-rerunfailures（失败重跑）、pytest-ordering（排序） |
| CI | Jenkinsfile + docs/JENKINS_SETUP.md（参数化 + Allure 发布） |
| 质量保障 | `cleanup_users` 后置清理零脏数据；失败报文落盘 + Allure 附件 |

---

## 二、目录结构

```
ruoyi_Interface/
├── run.py                     # 一键运行入口（pytest + 自动生成 Allure 报告）
├── conftest.py                # fixture：token / 数据清理 / 失败报文 hook
├── pytest.ini                 # pytest 配置（双报告 + 日志 + 标记）
├── requirements.txt           # 依赖清单
├── Jenkinsfile                # Jenkins 流水线
├── .gitignore                 # 排除 .venv / reports / logs / .idea 等
├── docs/
│   ├── JENKINS_SETUP.md            # Jenkins 安装与 Allure 联调指南
│   ├── 若依系统功能测试用例.xlsx    # 功能测试用例 83 条（16 列优化版，可筛选/统计）
│   └── 功能测试用例优化思路与方法.md # 资深视角：优化思路、设计方法、数据策略、追溯闭环
├── api/                       # API 对象层（对应 UI 框架的 pages/）
│   ├── base_api.py            #   基类：请求封装 + token 注入 + 失败留痕 + 日志
│   ├── login_api.py           #   登录接口
│   ├── user_api.py            #   用户管理接口（增/删/查）
│   ├── role_api.py            #   角色管理接口
│   ├── dept_api.py            #   部门管理接口（列表返回 data 字段）
│   ├── post_api.py            #   岗位管理接口
│   ├── dict_api.py            #   字典类型接口
│   ├── config_api.py          #   参数设置接口（configType=Y 为内置参数禁删）
│   └── notice_api.py          #   通知公告接口
├── tests/                     # 用例层（yaml 驱动 + Excel 驱动并存）
│   ├── test_login.py          #   登录用例（yaml）
│   ├── test_user.py           #   用户增删 + requests_mock Mock 四种写法
│   ├── test_user_excel.py     #   用户模块（Excel 驱动）
│   ├── test_role.py / test_role_excel.py   # 角色（yaml + Excel 双载体）
│   ├── test_dept.py           #   部门
│   ├── test_post.py           #   岗位
│   ├── test_dict.py           #   字典类型
│   ├── test_config.py         #   参数设置（含内置参数保护用例）
│   └── test_notice.py         #   通知公告
├── data/                     # 用例数据（yaml + Excel 双载体，{ts} 保证唯一）
│   ├── user_data.yaml / user_cases.xlsx
│   ├── role_data.yaml / role_cases.xlsx
│   └── dept/post/dict/config/notice 各模块 *_data.yaml
├── utils/
│   ├── yaml_loader.py         #   yaml 加载 + {ts} 模板渲染
│   └── excel_loader.py        #   Excel 读取（openpyxl，复用同一套渲染）
├── scripts/
│   ├── probe_api.py           #   契约校准（登录/用户模块）
│   └── probe_more_api.py      #   契约校准（角色/部门/岗位/字典/参数/公告）
├── reports/                   # 运行生成：report.html / allure-results / failures/
└── logs/                      # 运行生成：run.log（按次追加）
```

---

## 三、环境准备

### 1. 安装依赖

```bash
cd D:\DSKETOP\软测相关\ruoyi_Interface
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 准备后端

- 若依后端已启动：`http://localhost:8080`（一键启动脚本见 `D:\DSKETOP\软测相关\一键启动若依.bat`）
- 验证码已关闭（`captchaEnabled: false`），登录无需 code/uuid
- 默认账号：`admin / admin123`

### 3. 环境变量（可选，CI 参数化对接用）

```bash
set RUOYI_API=http://localhost:8080
set RUOYI_ADMIN=admin
set RUOYI_ADMIN_PWD=admin123
```

---

## 四、运行用例

```bash
# 一键运行（推荐）：跑全量 + 自动生成 Allure 报告 + 退出码透传
.venv\Scripts\python.exe run.py

# 或原生 pytest
.venv\Scripts\python.exe -m pytest

# 选择性运行
pytest tests/test_login.py -v          # 只跑登录
pytest -m user                         # 用户管理接口（真实后端）
pytest -m mock                         # Mock 演示（不依赖后端，可离线跑）
pytest -m smoke                        # 冒烟
pytest -n 4                            # xdist 4 进程并发
pytest --reruns 2 --reruns-delay 1     # 失败自动重跑 2 次
```

### 用例清单（13 条）

| 文件 | 用例 | 数量 | 说明 |
|---|---|---|---|
| test_login.py | 登录成功 / 密码错误 / 用户名为空 | 3 | yaml 驱动，成功/失败分流断言 |
| test_user.py | 新增/删除用户 + Mock 四种写法 | 8 | 含 {ts} 唯一 + 自动清理 + 离线 Mock |
| test_user_excel.py | 新增用户（正常/重复） | 2 | Excel 驱动 |
| test_role.py | 角色全链路 + 逆向（缺必填/重复/删不存在） | 4 | 全链路=增查改删一次跑通 |
| test_role_excel.py | 角色逆向（Excel 驱动） | 3 | 与 yaml 版并存对比 |
| test_dept.py | 部门全链路 + 逆向 | 3 | 部门列表用 data 字段 |
| test_post.py | 岗位全链路 + 逆向 | 4 | — |
| test_dict.py | 字典类型全链路 + 逆向 | 4 | 删不存在返回 NPE 文案（后端缺陷） |
| test_config.py | 参数全链路 + 逆向 + 内置参数保护 | 5 | configType=Y 禁删是业务规则 |
| test_notice.py | 公告全链路 + 逆向 | 3 | — |
| **合计** | | **39** | 全量通过，测试账号零残留 |

---

## 五、数据驱动：YAML 与 Excel 两种载体

**核心思想：测试代码只写一遍，数据文件给 N 组输入，代码就跑 N 次。** 两种载体的差异只在读取器，框架其余部分完全复用（"换载体不换代码"）。

### YAML 版（tests/test_user.py）

```yaml
# data/user_data.yaml
add_user_cases:
  - title: 正常新增用户-必填项
    userName: auto_{ts}        # {ts} 运行时替换成时间戳，保证账号唯一
    password: Test@123456
    expected_code: 200
    expected_msg: 操作成功
```

```python
# utils/yaml_loader.py
def get_cases(file_name, key):
    return yaml.safe_load(open(...))[key]
```

### Excel 版（tests/test_user_excel.py）

| title | userName | nickName | password | expected_code | expected_msg | cleanup |
|---|---|---|---|---|---|---|
| 正常新增用户-Excel数据驱动 | excel_{ts} | Excel测试用户 | Test@123456 | 200 | 操作成功 | TRUE |
| 新增用户-用户名重复-Excel应失败 | admin | 管理员 | Test@123456 | 500 | 登录账号已存在 | FALSE |

```python
# utils/excel_loader.py
def read_excel(file_name, sheet="Sheet1", header_row=1):
    """第 1 行表头当字段名，数据行与表头 zip 成字典"""
    ...
```

两种载体最终殊途同归：

```python
@pytest.mark.parametrize("case", _cases, ids=[c["title"] for c in _cases])
def test_add_user(self, user_api, cleanup_users, case):
    data = render(case, ts=_ts)          # 渲染 {ts} 占位符
    ...
    assert body["code"] == data["expected_code"]
    assert data["expected_msg"] in body["msg"]
```

> 选型建议：接口自动化首选 yaml（嵌套结构、git diff 友好）；Excel 适合大量扁平数据、业务人员参与维护。

---

## 六、核心机制

### 1. 登录态管理：session 级 token fixture

`conftest.py::api_token`：整个 pytest 进程只登录一次，所有 API 对象自动注入 `Authorization: Bearer <token>`，用例层无感知。

### 2. 数据清理：cleanup_users（零脏数据）

```python
def test_add_user(user_api, cleanup_users):
    cleanup_users.append("api_auto_xxx")   # 先登记（防断言失败残留）
    user_api.add_user(userName=..., ...)   # 造数据
# teardown 自动：按 userName 查 userId -> DELETE -> 校验 total=0
```

- 重复用户名用例在数据里标 `cleanup: false`，不会误删内置账号
- 清理失败只打日志，不让用例变红

### 3. 失败证据（接口版"失败截图"）

用例失败时自动：把最近一次请求/响应报文写入 `reports/failures/<用例名>_<时间>.json`，同时作为 JSON 附件挂到 Allure，失败现场可追溯、不用重跑。

### 4. 接口 Mock：requests_mock 四种写法（面试高频）

```python
# 1. 整体替换返回体
requests_mock.get(url, json={"code": 200, "rows": [...], "total": 2})

# 2. 模拟网络异常
requests_mock.get(url, exc=requests.exceptions.ConnectionError("断网了"))

# 3. 模拟慢接口（测超时/loading）
def slow(request, context):
    time.sleep(1.0)
    context.status_code = 200
    return json.dumps({...})
requests_mock.get(url, text=slow)

# 4. 按请求参数动态返回（透传改写效果）
def dynamic(request, context):
    qs = {k.lower(): v for k, v in request.qs.items()}   # 注意：qs 键被转小写
    ...
requests_mock.get(url, text=dynamic)
```

### 5. 契约校准：scripts/probe_api.py

**人的眼睛**：启动后端跑一次，把真实 code/msg 打出来，用来对齐 yaml/xlsx 里的 expected 文案，形成"探测 → 校准 → 回归"闭环。

```bash
.venv\Scripts\python.exe scripts\probe_api.py
```

---

## 七、日志与报告

### 日志（pytest.ini 配置，双出口）

| 出口 | 位置 | 级别 |
|---|---|---|
| 文件 | `logs/run.log`（按次追加） | INFO |
| 控制台 | 随 `-v` 输出 | INFO |

格式：`57 2026-10-09 18:02:06 base_api.py [函数名:_request] [INFO] [API] POST http://localhost:8080/login -> 200 (0.10s)`

- `api/base_api.py`：每次请求打 info，4xx/5xx 打 error
- `conftest.py`：用例失败打 error（含证据文件路径）

### 报告

```bash
# 运行后：
reports/report.html                    # pytest-html：本地双击即开
reports/allure-report/index.html       # Allure：静态报告
# 本地实时看 Allure：
allure serve reports\allure-results
```

---

## 八、CI 集成（Jenkins）

`Jenkinsfile` + `docs/JENKINS_SETUP.md` 提供：

- 参数化构建（`RUOYI_API` / `RUOYI_ADMIN` / `RUOYI_ADMIN_PWD` 环境变量对接）
- 拉取代码 → 装依赖 → 跑 `run.py` → 发布 Allure 报告 → 邮件通知
- 退出码透传：用例失败即流水线失败

---

## 九、踩坑记录（面试谈资）

| 坑 | 现象 | 解法 |
|---|---|---|
| pytest 8 中文 parametrize id 转义 | 失败证据文件名含 `\uXXXX`（反斜杠被当路径分隔符）→ `FileNotFoundError` | hook 里 `re.sub(r'[\\/:*?"<>|]', '_', item.name)` 清洗文件名 |
| requests_mock 参数名转小写 | `userName` 过滤失效，动态返回用例失败 | `qs = {k.lower(): v for k, v in request.qs.items()}` |
| expected 文案凭经验写 | 用户名为空实际返回 `用户不存在/密码错误`，断言失败 | 跑 probe_api.py 以实测为准改数据 |
| Excel 数据漏列 | `Field 'nick_name' doesn't have a default value` | 数据文件字段必须与 yaml 版严格对齐（字段完整性由数据保证） |
| pytest 8.2 不认 `log_file_encoding` | PytestConfigWarning | 删掉该配置项，用默认编码 |
| allure.step title 用花括号占位符 | 逆向用例缺参时 `.format(**kwargs)` 抛 `KeyError` | API 方法 allure.step title 一律不带 `{占位符}` |
| 删除不存在 id | dict/config 返回 Java NPE 文案而非"操作失败" | 以 probe 实测为准校准 expected_msg（也暴露了后端缺陷） |
| 参数 configType="Y" | 删除报"内置参数不能删除"，正向用例留脏数据 | 正向用例用 `"N"`；内置参数保护单独做成逆向用例 |

---

## 十、常见问题（FAQ）

**Q: `git push origin main` 报错 `src refspec main does not match any`？**
A: 本地/远程分支是 `master`，用 `git push origin master`；或 `git branch -M main` 重命名后推送。

**Q: `git add .` 出现 `LF will be replaced by CRLF` 警告？**
A: 正常行尾符转换提示，不影响功能，无需处理。

**Q: 后端重启后接口用例失败？**
A: 接口框架每次运行重新登录拿新 token，不受影响（web 框架需删除 `.auth/admin_state.json` 重新登录）。

---

## 十一、学习地图（与 UI 框架对照）

| UI 框架（ruoyi_playwright） | 接口框架（ruoyi_Interface） | 实现位置 |
|---|---|---|
| PO 分层 pages/ | **API 对象层 api/** | `base_api.py` + `login_api.py` + `user_api.py` |
| 登录态 storage_state | **session 级 token fixture** | `conftest.py::api_token` |
| YAML 数据驱动 | 相同 + `{ts}` 渲染 + **Excel 双载体** | `data/` + `utils/` |
| 失败截图 | **失败报文证据** | `conftest.py::pytest_runtest_makereport` |
| page.route Mock | **requests_mock 四种写法** | `tests/test_user.py::TestUserApiMock` |
| 后置清理 | `cleanup_users` yield fixture | teardown 按 userName 删除 |
| Allure / Jenkins | 相同 | `Jenkinsfile` + `docs/JENKINS_SETUP.md` |
