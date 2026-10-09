# -*- coding: utf-8 -*-
"""LoginApi：若依登录相关接口（对应 UI 框架的 login_page.py）"""
import allure

from api.base_api import BaseApi


class LoginApi(BaseApi):
    """登录接口对象：captchaImage / login"""

    @allure.step("获取验证码信息 GET /captchaImage")
    def get_captcha(self):
        """验证码接口；若依 captchaEnabled=false 时登录无需验证码"""
        return self.get("/captchaImage")

    @allure.step("登录 POST /login（{username}）")
    def login(self, username: str, password: str):
        """登录：返回若依统一结构 {code, msg, token, ...}"""
        return self.post("/login", json={"username": username, "password": password})
