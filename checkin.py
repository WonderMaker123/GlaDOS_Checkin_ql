#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
cron: 40 0 * * *
new Env('GlaDOS签到');
"""

import requests
import json
import os
import sys
import time


# ===============================
# 获取Cookie
# ===============================
def get_cookies():
    if os.environ.get("GR_COOKIE"):
        if '&' in os.environ["GR_COOKIE"]:
            cookies = os.environ["GR_COOKIE"].split('&')
        elif '\n' in os.environ["GR_COOKIE"]:
            cookies = os.environ["GR_COOKIE"].split('\n')
        else:
            cookies = [os.environ["GR_COOKIE"]]
    else:
        print("未获取到 GlaDOS Cookie")
        return []

    print(f"共获取到 {len(cookies)} 个账号\n")
    return cookies


# ===============================
# 通知
# ===============================
def load_send():
    cur_path = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(cur_path)
    if os.path.exists(cur_path + "/sendNotify.py"):
        from sendNotify import send
        return send
    else:
        return None


# ===============================
# 核心签到逻辑
# ===============================
def checkin(cookie):

    BASE_URL = os.environ.get("GLADOS_BASE_URL", "https://glados.cloud").rstrip("/")

    checkin_url = f"{BASE_URL}/api/user/checkin"
    status_url = f"{BASE_URL}/api/user/status"
    points_url = f"{BASE_URL}/api/user/points"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json;charset=UTF-8",
        "Referer": f"{BASE_URL}/console/checkin",
        "Origin": BASE_URL,
        "Cookie": cookie
    }

    # 🔥 修复关键：固定 token
    body = {
        "token": "glados.one"
    }

    try:
        # ===== 签到 =====
        resp = requests.post(
            checkin_url,
            headers=headers,
            data=json.dumps(body),
            timeout=15
        )

        checkin_result = resp.json()
        message = checkin_result.get("message", "未知返回")

        # ===== 查询状态 =====
        status_resp = requests.get(status_url, headers=headers, timeout=15)
        status_data = status_resp.json().get("data", {})

        email = status_data.get("email", "未知账号")
        left_days = str(status_data.get("leftDays", "0")).split(".")[0]

        # ===== 查询积分 =====
        points_resp = requests.get(points_url, headers=headers, timeout=15)
        points_data = points_resp.json().get("data", {})
        points = points_data.get("points", 0)

        content = (
            f"账号：{email}\n"
            f"签到结果：{message}\n"
            f"剩余天数：{left_days}\n"
            f"当前积分：{points}\n\n"
        )

        print(content)
        return content

    except Exception as e:
        error_msg = f"签到异常：{e}\n\n"
        print(error_msg)
        return error_msg


# ===============================
# 主执行
# ===============================
def main():
    contents = ""
    cookies = get_cookies()

    for cookie in cookies:
        contents += checkin(cookie)

    return contents


if __name__ == "__main__":

    title = "GlaDOS签到通知"
    content = main()

    send = load_send()

    if send:
        if not content:
            content = "签到失败，请检查 Cookie 或网络"
        send(title, content)
