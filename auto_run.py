import subprocess
import time
import math
import os

# ========== 配置参数 ==========
SPEED = 2.8  # 跑步速度，单位：米/秒（普通慢跑约2.5-3.5，可调）
LOOP = True  # 是否自动循环路线
UPDATE_INTERVAL = 1  # 每隔多少秒更新一次定位
# ==============================

ADB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "platform-tools", "adb.exe")
ROUTE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "route.txt")

PROVIDERS = ["gps", "network"]  # 同时模拟GPS和网络定位，防止被对比检测


def run_adb(args):
    cmd = [ADB_PATH] + args
    # 修复：Windows下ADB输出是GBK编码，用errors=ignore避免解码崩溃
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='gbk', errors='ignore')
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def haversine(lat1, lon1, lat2, lon2):
    """计算两个经纬度点之间的距离（米）"""
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def load_route():
    """从route.txt读取路线点"""
    points = []
    with open(ROUTE_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split(',')
            if len(parts) >= 2:
                lat = float(parts[0].strip())
                lng = float(parts[1].strip())
                points.append((lat, lng))
    return points


def init_mock_location():
    """初始化模拟定位：同时开GPS和网络两个provider"""
    print("[*] 初始化模拟定位...")
    for provider in PROVIDERS:
        run_adb(["shell", "cmd", "location", "providers", "add-test-provider", provider])
        run_adb(["shell", "cmd", "location", "providers", "set-test-provider-enabled", provider, "true"])
        # 设置精度为正常GPS精度（约10米），让APP看起来更真实
        run_adb(["shell", "cmd", "location", "providers", "set-test-provider-accuracy", provider, "10.0"])
    print(f"[+] 模拟定位已开启（{', '.join(PROVIDERS)}）")


def stop_mock_location():
    """关闭模拟定位，恢复正常"""
    print("[*] 关闭模拟定位...")
    for provider in PROVIDERS:
        run_adb(["shell", "cmd", "location", "providers", "remove-test-provider", provider])
    print("[+] 模拟定位已关闭，恢复正常定位")


def set_location(lat, lng):
    """同时更新两个provider的位置"""
    for provider in PROVIDERS:
        run_adb(["shell", "cmd", "location", "providers", "set-test-provider-location",
                 provider, "--location", f"{lat},{lng}"])


def main():
    # 检查ADB连接
    out, err, code = run_adb(["devices"])
    lines = [l for l in out.split('\n')[1:] if l.strip() and '\tdevice' in l]
    if not lines:
        print("[!] 没有检测到已连接的安卓设备！")
        print("[!] 请先确认手机已开启无线调试并完成配对连接")
        input("按回车键退出...")
        return

    print(f"[+] 检测到设备: {lines[0].split()[0]}")

    # 读取路线
    if not os.path.exists(ROUTE_FILE):
        print(f"[!] 找不到路线文件: route.txt")
        input("按回车键退出...")
        return

    route = load_route()
    if len(route) < 2:
        print("[!] 路线点太少，至少需要2个点")
        input("按回车键退出...")
        return

    print(f"[+] 路线共 {len(route)} 个点")
    print(f"[+] 跑步速度: {SPEED} m/s (约{SPEED*3.6:.1f} km/h)")

    # 初始化
    init_mock_location()
    time.sleep(1)

    total_distance = 0
    start_time = time.time()

    try:
        point_idx = 0
        while True:
            lat1, lng1 = route[point_idx]
            lat2, lng2 = route[(point_idx + 1) % len(route)]

            seg_dist = haversine(lat1, lng1, lat2, lng2)
            seg_time = seg_dist / SPEED
            steps = max(1, int(seg_time / UPDATE_INTERVAL))

            for i in range(steps):
                ratio = i / steps
                cur_lat = lat1 + (lat2 - lat1) * ratio
                cur_lng = lng1 + (lng2 - lng1) * ratio
                set_location(cur_lat, cur_lng)

                elapsed = time.time() - start_time
                print(f"\r[>] 第{point_idx+1}/{len(route)}段 | 已跑{elapsed/60:.1f}分钟 | 位置: {cur_lat:.6f},{cur_lng:.6f}    ", end='', flush=True)
                time.sleep(UPDATE_INTERVAL)

            total_distance += seg_dist
            point_idx += 1

            if point_idx >= len(route):
                if LOOP:
                    print(f"\n[+] 一圈完成，累计跑了{total_distance:.0f}米，开始下一圈...")
                    point_idx = 0
                else:
                    break

    except KeyboardInterrupt:
        print("\n[*] 收到停止指令...")
    finally:
        stop_mock_location()
        elapsed = time.time() - start_time
        print(f"\n[+] 本次结束：共跑了{total_distance:.0f}米，用时{elapsed/60:.1f}分钟")
        input("按回车键退出...")


if __name__ == "__main__":
    main()
