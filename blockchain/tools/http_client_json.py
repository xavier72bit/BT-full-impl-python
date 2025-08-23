# -*- coding: UTF-8 -*-
# @Project: core-impl-python
# @File   : http_client_json.py
# @Author : Xavier Wu
# @Date   : 2025/8/3 14:49

# std import
import json

# 3rd import
import requests


class JSONClient:
    def get(self, url):
        req: requests.Response = requests.get(url)
        if req.ok:
            return req.json()

        return None

    def post(self, url, data):
        data = json.dumps(data, sort_keys=True)
        headers = {"Content-Type": "application/json"}
        req: requests.Response = requests.post(url, data=data, headers=headers)
        if req.ok:
            return req.json()

        return None
