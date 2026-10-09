// ============================================================
// Jenkinsfile - 若依接口自动化测试流水线（Windows）
// ============================================================
// 使用方式：
//   1. Jenkins 安装 Allure 插件
//   2. 新建任务 -> 流水线（Pipeline）-> 粘贴本文件，或 SCM 指向本仓库
//   3. 构建触发：定时构建（如 H 22 * * * 每晚22点）或 Webhook
//
// 环境变量（与 conftest.py 对齐）：
//   RUOYI_API        后端接口地址（默认 http://localhost:8080）
//   RUOYI_ADMIN / RUOYI_ADMIN_PWD  登录账号
// ============================================================

pipeline {
    agent any

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))   // 保留最近 10 次构建
        timestamps()                                      // 日志带时间戳
        timeout(time: 30, unit: 'MINUTES')                // 超时保护
    }

    environment {
        RUOYI_API = "${params.RUOYI_API}"
        RUOYI_ADMIN = "${params.RUOYI_ADMIN}"
        RUOYI_ADMIN_PWD = "${params.RUOYI_ADMIN_PWD}"
        ALLURE_RESULTS = 'reports/allure-results'
    }

    parameters {
        string(name: 'RUOYI_API', defaultValue: 'http://localhost:8080', description: '若依后端接口地址')
        string(name: 'RUOYI_ADMIN', defaultValue: 'admin', description: '登录账号')
        string(name: 'RUOYI_ADMIN_PWD', defaultValue: 'admin123', description: '登录密码')
        choice(name: 'TEST_SCOPE', choices: ['全部用例', '冒烟 smoke', '用户接口 user', 'Mock mock'], description: '选择执行范围')
    }

    stages {
        stage('1. 拉取代码') {
            steps { checkout scm }
        }

        stage('2. 环境准备') {
            steps {
                // Windows 下用 bat。依赖未装时取消注释：
                // bat 'python -m pip install -r requirements.txt'
                echo 'Python 环境就绪（依赖建议在 Jenkins 节点初始化脚本里预装）'
            }
        }

        stage('3. 执行自动化测试') {
            steps {
                script {
                    def scope = ''
                    if (params.TEST_SCOPE == '冒烟 smoke') {
                        scope = '-m smoke'
                    } else if (params.TEST_SCOPE == '用户接口 user') {
                        scope = '-m user'
                    } else if (params.TEST_SCOPE == 'Mock mock') {
                        scope = '-m mock'
                    }
                    bat "python -m pytest ${scope} --alluredir=${ALLURE_RESULTS} --clean-alluredir --tb=short"
                }
            }
        }

        stage('4. 发布 Allure 报告') {
            steps {
                script {
                    allure includeProperties: false, jdk: '', results: [[path: ALLURE_RESULTS]]
                }
            }
        }
    }

    post {
        always {
            echo '流水线结束，测试结果已发布到 Allure'
        }
        failure {
            echo "构建失败，报告地址: ${env.BUILD_URL}allure/"
            // mail to: 'test@example.com', subject: "若依接口测试失败 ${env.JOB_NAME}", body: "查看报告: ${env.BUILD_URL}allure/"
        }
    }
}
