# -*- coding: utf-8 -*-
"""
地图插件服务端：简易版百度地图
- 提供地图页面 + 接收地图点选坐标 -> 调用MuMu定位
- 坐标系统：百度坐标(BD09)，和mumu虚拟定位/APP一致
"""
import json
import os
import subprocess
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

MUMU_CLI_PATH = r"E:\Program Files\Netease\MuMu\nx_main\mumu-cli.exe"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROUTE_FILE = os.path.join(BASE_DIR, "route.txt")
PORT = 8765

_server = None
_thread = None
_current_pos = None  # 当前定位坐标(百度坐标 lat,lng)，供地图实时显示


def record_position(lat, lng):
    """记录当前定位坐标(百度坐标)。主程序每次定位时调用，地图页面轮询读取"""
    global _current_pos
    _current_pos = (lat, lng)


def get_current_position():
    return _current_pos


def set_mumu_location(lat, lng):
    """调用MuMu官方命令设置GPS位置"""
    try:
        cmd = [MUMU_CLI_PATH, "control", "--vmindex", "0", "tool", "location",
               "--longitude", str(lng), "--latitude", str(lat)]
        subprocess.run(cmd, capture_output=True, timeout=2)
        return True
    except Exception:
        return False


def load_route():
    points = []
    with open(ROUTE_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split(',')
            if len(parts) >= 2:
                points.append([float(parts[0].strip()), float(parts[1].strip())])
    return points


class MapHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # 静默日志

    def _send_json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path.startswith('/api/route'):
            try:
                pts = load_route()
                self._send_json({"ok": True, "points": pts})
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)}, 500)
        elif self.path.startswith('/api/health'):
            self._send_json({"ok": True, "msg": "地图服务运行中"})
        elif self.path.startswith('/api/current'):
            pos = get_current_position()
            if pos:
                self._send_json({"ok": True, "lat": pos[0], "lng": pos[1]})
            else:
                self._send_json({"ok": True, "lat": None, "lng": None})
        else:
            # 返回地图页面
            page = os.path.join(BASE_DIR, "map_page.html")
            try:
                with open(page, 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            except Exception:
                self._send_json({"ok": False, "error": "找不到map_page.html"}, 404)

    def do_POST(self):
        if self.path.startswith('/api/setloc'):
            try:
                length = int(self.headers.get('Content-Length', 0))
                body = json.loads(self.rfile.read(length).decode('utf-8'))
                lat = float(body.get('lat'))
                lng = float(body.get('lng'))
                ok = set_mumu_location(lat, lng)
                record_position(lat, lng)  # 记录，地图实时显示
                self._send_json({"ok": ok, "lat": lat, "lng": lng})
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)}, 500)
        else:
            self._send_json({"ok": False, "error": "未知接口"}, 404)


def start_map_server(port=PORT):
    """启动地图服务（幂等，不会重复启动）"""
    global _server, _thread
    if _server is not None:
        return True
    try:
        _server = ThreadingHTTPServer(("127.0.0.1", port), MapHandler)
        _thread = threading.Thread(target=_server.serve_forever, daemon=True)
        _thread.start()
        return True
    except Exception:
        return False


def open_map():
    """启动服务并打开浏览器地图页面"""
    if not start_map_server():
        return False
    webbrowser.open(f"http://127.0.0.1:{PORT}/")
    return True


if __name__ == "__main__":
    if open_map():
        print(f"地图已打开: http://127.0.0.1:{PORT}/")
    else:
        print("地图服务启动失败，检查端口占用")
