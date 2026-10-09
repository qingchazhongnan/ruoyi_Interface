# -*- coding: utf-8 -*-
"""yaml 测试数据加载工具"""
import os

import yaml

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def load_yaml(file_name: str) -> dict:
    """读取 data 目录下的 yaml 文件"""
    path = os.path.join(DATA_DIR, file_name)
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_cases(file_name: str, key: str) -> list:
    """取 yaml 里某个 key 下的用例列表（[{title, ...}, ...]）"""
    data = load_yaml(file_name)
    return data.get(key, [])


def render(case: dict, **kwargs) -> dict:
    """
    渲染模板变量：把用例里的 {ts} 之类的占位符替换成真实值。
    例如 userName: api_auto_{ts} -> api_auto_1730000000
    """
    import copy

    new = copy.deepcopy(case)
    for k, v in new.items():
        if isinstance(v, str):
            new[k] = v.format(**kwargs)
    return new
