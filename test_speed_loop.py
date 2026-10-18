# -*- coding: utf-8 -*-
"""验证新主循环：速度=坐标移动距离÷实测耗时，配速恒定"""
import sys, time, math
sys.path.insert(0, r"E:\跑步")

# 打桩：不真调mumu，用假实现模拟命令耗时
import auto_run_gui as m
m.set_mumu_location = lambda lat, lng: None
m.shake_mumu = lambda: time.sleep(0.15)  # 模拟每次命令耗时0.15秒

import tkinter as tk
from tkinter import ttk

# 造一个无窗口的假root，让after直接执行
class FakeRoot:
    def __init__(self):
        self.calls = []
    def after(self, delay, fn):
        self.calls.append(fn)
        return 0

# 构造App实例但跳过UI
root = FakeRoot()
app = m.App.__new__(m.App)
app.root = root
app.running = True
app.loop_var = type("V", (), {"get": lambda self: True})()  # 自动循环
app.speed_var = type("V", (), {"get": lambda self: 3.5})()  # 设定速度3.5m/s

# 记录日志/标签
logs = []
app._log = lambda msg: logs.append(msg)
app._init_mock = lambda: None
app._stop_mock = lambda: None
for name in ["time_label", "dist_label", "circle_label", "start_btn", "stop_btn"]:
    setattr(app, name, type("L", (), {"config": lambda self, **k: None})())

# 跑固定时长(比如20秒)后自动停止
import threading
def stop_after():
    time.sleep(20)
    app.running = False
threading.Thread(target=stop_after, daemon=True).start()

# 用真实route.txt
app._run_loop()

# 统计：跑了多久、多少距离
elapsed_total = time.time() - app.start_time
print("总用时: %.1f 秒" % elapsed_total)
print("总距离: %.0f 米" % app.total_distance)
print("圈数: %.1f 圈" % (app.total_distance / 400))

# 验证配速：距离/时间 应接近 3.5 m/s
real_speed = app.total_distance / elapsed_total
print("实际平均速度: %.3f m/s (设定 3.5 m/s)" % real_speed)
assert abs(real_speed - 3.5) < 0.2, "配速偏差过大!"
print("✅ 配速恒定验证通过：速度 = 坐标移动距离 ÷ 实测耗时")
