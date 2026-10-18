# -*- coding: utf-8 -*-
"""地图插件完整测试：启动服务->检查所有接口->关闭"""
import json
import urllib.request
import sys
import os
sys.path.insert(0, r"E:\跑步")
import map_server

ok_all = True

def check(name, cond, extra=""):
    global ok_all
    mark = "✅" if cond else "❌"
    print(f"{mark} {name} {extra}")
    if not cond:
        ok_all = False

# 1. 启动服务
ok = map_server.start_map_server()
check("服务启动", ok)

def get(url):
    return urllib.request.urlopen(url, timeout=5).read().decode('utf-8')

# 2. 健康检查
d = json.loads(get("http://127.0.0.1:8765/api/health"))
check("健康检查", d.get("ok") is True)

# 3. 路线接口
d = json.loads(get("http://127.0.0.1:8765/api/route"))
pts = d.get("points", [])
check("路线接口", d.get("ok") is True and len(pts) >= 2, f"(共{len(pts)}个点)")
if pts:
    # route.txt = 高德坐标(GCJ02)，格式[经度,纬度]，应在哈尔滨范围内
    lng, lat = pts[0]
    check("路线格式(经度,纬度)", 126 < lng < 127 and 45 < lat < 46,
          f"第1点: 经度{lng:.6f}, 纬度{lat:.6f}")

# 4. 首页
html = get("http://127.0.0.1:8765/")
check("地图页面", "leaflet" in html and "高德卫星" in html, f"(页面{len(html)}字节)")

# 5. 定位接口（只验证返回结构，不真调mumu，避免误动定位）
import map_server as ms
orig = ms.set_mumu_location
ms.set_mumu_location = lambda lat, lng: True  # 打桩，不真调用
req = urllib.request.Request("http://127.0.0.1:8765/api/setloc",
                             data=json.dumps({"lat": 45.719900, "lng": 126.621000}).encode(),
                             headers={"Content-Type": "application/json"})
d = json.loads(urllib.request.urlopen(req, timeout=5).read().decode())
check("定位接口", d.get("ok") is True, f"(坐标 {d.get('lat')},{d.get('lng')})")
ms.set_mumu_location = orig

print("\n" + ("🎉 全部测试通过，地图插件可用" if ok_all else "⚠️ 有测试失败，需修复"))
sys.exit(0 if ok_all else 1)
