# -*- coding: UTF-8 -*-
# @Project: core-impl-python
# @File   : http_json.py
# @Author : Xavier Wu
# @Date   : 2025/8/3 14:49

# 3rd import
import requests

class JSONClient:
    def get(self, url):
        req: requests.Response = requests.get(url)
        if req.ok:
            return req.json()

        return None

    def post(self, url, data):
        req: requests.Response = requests.post(url, json=data)
        if req.ok:
            return req.json()

        return None
