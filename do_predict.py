#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@author: chenhao
@time: 2023/7/11 20:53
"""

import requests
import json

DEFAULT_KWARGS = {
    "min_tokens": 0,
    "top_k": 0,
    "top_p": 0.75,
    "temperature": 0.95,
    "seed": 1234,
    "num_beams": 1,
    "length_penalty": 0
}


def generate(question, ip='172.16.0.102', port="5000", kwargs=DEFAULT_KWARGS):
    url = f'http://{ip}:{port}/generate'
    # print(url)

    prompt = question
    # print(prompt)
    data = {
        "prompt": prompt,
    }
    data.update(kwargs)

    response = requests.post(url, json=data)
    # print(response.json())

    # 检查请求是否成功
    if response.status_code == 200:
        # 获取响应结果
        result = response.json()['data']['outputText']
        return result
    else:
        return None


if __name__ == "__main__":
    result = generate(ip="http://172.17.0.3", question="帮我写一封信，信中的内容表达对女朋友的思念")
    print("result")
    print(result)
