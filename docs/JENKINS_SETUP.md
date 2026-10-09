# Jenkins + Allure 联调指南（若依接口自动化框架）

> 与 UI 框架（ruoyi_playwright）的联调方式基本一致，差异点：
> 接口框架不需要浏览器，环境更轻；Jenkins 节点只需 Python + allure 命令行。

## 一、本地查看报告

```bash
cd D:\DSKETOP\软测相关\ruoyi_Interface

# 1. 跑用例（pytest.ini 已默认带 --alluredir）
.venv\Scripts\activate
pytest

# 2. 方式 A：实时网页
allure serve reports\allure-results

# 3. 方式 B：生成静态报告目录
allure generate reports\allure-results -o reports\allure-report --clean
allure open reports\allure-report
```

Allure 报告里能看到：
- feature/story 分组的用例树（登录接口 / 用户管理接口 / 接口 Mock 演示）
- 每个用例的**接口调用步骤**（@allure.step）
- **失败用例自动附带"请求/响应报文"附件**（接口版失败截图，conftest hook 实现）
- 历史趋势图（Jenkins 里聚合）

## 二、Jenkins 安装（Windows）

1. 下载 Jenkins LTS，解压运行（**注意避开 8080 端口**，若依后端占用了它）：
   ```
   java -jar jenkins.war --httpPort=8082
   ```
2. 初始化密码在 `C:\Users\Administrator\.jenkins\secrets\initialAdminPassword`
3. 装插件：**Allure Jenkins Plugin**（必装）、HTML Publisher（可选）
4. 全局工具配置里指向本机 JDK 17
5. 确认 Jenkins 节点能执行 `python`、`allure`（PATH 配好；找不到命令时在 全局属性 里补 PATH）

## 三、创建流水线任务

1. 新建任务 → 流水线（Pipeline）
2. 定义：`Pipeline script from SCM`（Git 仓库，脚本路径 `Jenkinsfile`）或直接粘贴项目根目录 `Jenkinsfile`
3. 构建触发器：
   - 定时构建：`H 22 * * *`（每晚 22 点）
   - 若依后端接口契约变更触发：配 webhook
4. Build Now 试跑

## 四、Jenkinsfile 说明

```
Checkout(拉代码) -> 环境准备 -> pytest 执行(参数选范围) -> 发布 Allure 报告
                                └──────── post: 失败通知
```

- 参数化：`RUOYI_API / 账号密码 / 测试范围` 构建页可改，`conftest.py` 读环境变量天然对接
- 接口框架无浏览器，比 UI 框架快很多（mock 用例 1 秒内跑完）

## 五、常见问题

| 现象 | 原因 / 处理 |
|---|---|
| `allure: command not found` | Jenkins 服务没继承 PATH；全局属性里补 npm 全局 bin 目录 |
| 真实接口用例全失败 | 若依后端没启动；先确认 `http://localhost:8080` 可访问，或改 `RUOYI_API` |
| `用户不存在/密码错误` 文案不符 | 后端契约可能不同；跑 `scripts/probe_api.py` 校准，改 `data/user_data.yaml` 的 expected |
| 测试账号残留 | `cleanup_users` fixture 会自动删；即使用例失败也会清理（teardown 兜底） |
| 重复用户名用例误删 admin | 该用例 yaml 里 `cleanup: false`，不会登记清理，放心 |

## 六、最终形态

```
每晚 22:00 触发
    │
    ▼
Jenkins 流水线
  ├─ python -m pytest --alluredir=reports/allure-results
  └─ Allure 发布（趋势 + 步骤树 + 失败报文附件）
    │
    ▼
失败 → 邮件 / 企业微信通知
```
