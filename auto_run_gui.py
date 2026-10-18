import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
import math
import os
import map_server

ADB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "platform-tools", "adb.exe")
MUMU_CLI_PATH = r"E:\Program Files\Netease\MuMu\nx_main\mumu-cli.exe"
ROUTE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "route.txt")


def run_adb(args):
    cmd = [ADB_PATH] + args
    result = subprocess.run(cmd, capture_output=True, text=True, encoding='gbk', errors='ignore')
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def gcj02_to_wgs84(lat, lng):
    """高德火星坐标(GCJ-02)转GPS地球坐标(WGS-84)"""
    a = 6378245.0
    ee = 0.00669342162296594323

    def transform_lat(x, y):
        ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
        ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(y * math.pi) + 40.0 * math.sin(y / 3.0 * math.pi)) * 2.0 / 3.0
        ret += (160.0 * math.sin(y / 12.0 * math.pi) + 320 * math.sin(y * math.pi / 30.0)) * 2.0 / 3.0
        return ret

    def transform_lng(x, y):
        ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
        ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(x * math.pi) + 40.0 * math.sin(x / 3.0 * math.pi)) * 2.0 / 3.0
        ret += (150.0 * math.sin(x / 12.0 * math.pi) + 300.0 * math.sin(x / 30.0 * math.pi)) * 2.0 / 3.0
        return ret

    dlat = transform_lat(lng - 105.0, lat - 35.0)
    dlng = transform_lng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * math.pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * math.pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * math.pi)
    mglat = lat + dlat
    mglng = lng + dlng
    # 反向修正，近似得到WGS-84
    wgs_lat = lat * 2 - mglat
    wgs_lng = lng * 2 - mglng
    return wgs_lat, wgs_lng


def gcj02_to_bd09(lat, lng):
    """高德火星坐标(GCJ-02)转百度坐标(BD-09)，用于mumu定位"""
    x_pi = math.pi * 3000.0 / 180.0
    z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * x_pi)
    theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * x_pi)
    bd_lng = z * math.cos(theta) + 0.0065
    bd_lat = z * math.sin(theta) + 0.006
    return bd_lat, bd_lng


def set_mumu_location(lat, lng):
    """用MuMu官方命令设置GPS位置，和手动点虚拟定位效果一样"""
    try:
        cmd = [MUMU_CLI_PATH, "control", "--vmindex", "0", "tool", "location",
               "--longitude", str(lng), "--latitude", str(lat)]
        subprocess.run(cmd, capture_output=True, timeout=2)
    except:
        pass


def shake_mumu():
    """模拟摇手机，模拟跑步步频"""
    try:
        cmd = [MUMU_CLI_PATH, "control", "--vmindex", "0", "tool", "func", "--name", "shake"]
        subprocess.run(cmd, capture_output=True, timeout=2)
    except:
        pass


def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def load_route():
    """读取路线文件，返回统一格式：[(纬度BD09, 经度BD09), ...]
    route.txt 实际格式为「经度,纬度」高德坐标(GCJ02)，需转成百度坐标(BD09)供mumu定位"""
    points = []
    with open(ROUTE_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split(',')
            if len(parts) >= 2:
                lng_gcj = float(parts[0].strip())
                lat_gcj = float(parts[1].strip())
                lat_bd, lng_bd = gcj02_to_bd09(lat_gcj, lng_gcj)
                points.append((lat_bd, lng_bd))
    return points


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("校园跑助手")
        self.root.geometry("460x450")
        self.root.resizable(False, False)

        self.running = False
        self.thread = None
        self.total_distance = 0
        self.start_time = 0

        self._build_ui()

        # 窗口关闭时先清理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _build_ui(self):
        # 运行控制区
        ctrl_frame = ttk.LabelFrame(self.root, text="运行控制")
        ctrl_frame.pack(fill='x', padx=10, pady=10)

        ttk.Label(ctrl_frame, text="跑步速度").grid(row=0, column=0, padx=10, pady=10)
        self.speed_var = tk.DoubleVar(value=3.5)
        self.speed_slider = ttk.Scale(ctrl_frame, from_=2.5, to=5.0, variable=self.speed_var,
                                      orient='horizontal', length=220, command=self._update_speed_label)
        self.speed_slider.grid(row=0, column=1, padx=10, pady=10)
        self.speed_label = ttk.Label(ctrl_frame, text="3.5 m/s")
        self.speed_label.grid(row=0, column=2, padx=10, pady=10)

        self.loop_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(ctrl_frame, text="自动循环跑圈", variable=self.loop_var).grid(row=1, column=0, columnspan=3, padx=5, pady=3)

        btn_frame = ttk.Frame(ctrl_frame)
        btn_frame.grid(row=2, column=0, columnspan=3, pady=10)
        self.prepare_btn = ttk.Button(btn_frame, text="准备起点", command=self.prepare_start)
        self.prepare_btn.pack(side='left', padx=10)
        self.start_btn = ttk.Button(btn_frame, text="开始跑", command=self.start_run)
        self.start_btn.pack(side='left', padx=10)
        self.stop_btn = ttk.Button(btn_frame, text="停止", command=self.stop_run, state='disabled')
        self.stop_btn.pack(side='left', padx=10)
        self.map_btn = ttk.Button(btn_frame, text="地图", command=self.open_map)
        self.map_btn.pack(side='left', padx=10)

        # 状态显示区
        status_frame = ttk.LabelFrame(self.root, text="运行状态")
        status_frame.pack(fill='both', expand=True, padx=10, pady=5)

        self.dist_label = ttk.Label(status_frame, text="已跑距离: 0 米", font=("Arial", 12))
        self.dist_label.pack(pady=3)
        self.time_label = ttk.Label(status_frame, text="用时: 0 分钟", font=("Arial", 12))
        self.time_label.pack(pady=3)
        self.circle_label = ttk.Label(status_frame, text="圈数: 0", font=("Arial", 12))
        self.circle_label.pack(pady=3)
        self.log_text = tk.Text(status_frame, height=7, state='disabled', wrap='word')
        self.log_text.pack(fill='both', expand=True, padx=5, pady=5)

    def _update_speed_label(self, _=None):
        s = self.speed_var.get()
        self.speed_label.config(text=f"{s:.1f} m/s")

    def _log(self, msg):
        self.log_text.config(state='normal')
        self.log_text.insert('end', msg + '\n')
        self.log_text.see('end')
        self.log_text.config(state='disabled')

    def _init_mock(self):
        # MuMu官方定位接口不需要初始化，直接设置就行
        self._log("使用MuMu官方定位接口")

    def _stop_mock(self):
        # MuMu定位不需要清理，直接停止就行
        pass

    def _set_loc(self, lat, lng):
        # 用MuMu官方命令设置位置，APP完全检测不出来
        set_mumu_location(lat, lng)
        map_server.record_position(lat, lng)  # 同步给地图，跑步时红点实时移动

    def _pos_at(self, distance, route, seg_starts):
        """根据沿路线累计距离(米)，线性插值算出当前坐标
        逻辑依据：速度=坐标移动距离÷时间，所以先按距离定位，再算坐标"""
        d = distance
        for i in range(len(seg_starts) - 1):
            if d <= seg_starts[i + 1]:
                seg_len = seg_starts[i + 1] - seg_starts[i]
                if seg_len <= 0:
                    continue
                ratio = (d - seg_starts[i]) / seg_len
                lat1, lng1 = route[i]
                lat2, lng2 = route[(i + 1) % len(route)]
                return lat1 + (lat2 - lat1) * ratio, lng1 + (lng2 - lng1) * ratio
        return route[0]

    def _run_loop(self):
        route = load_route()
        if len(route) < 2:
            self._log("路线点太少！请先编辑route.txt")
            return

        # 计算每段距离与累计起点，路线首尾闭环
        n = len(route)
        seg_starts = [0.0]
        for i in range(n):
            lat1, lng1 = route[i]
            lat2, lng2 = route[(i + 1) % n]
            seg_starts.append(seg_starts[-1] + haversine(lat1, lng1, lat2, lng2))
        total_len = seg_starts[-1]  # 一圈总长(米)

        self._init_mock()
        time.sleep(1)
        self.total_distance = 0
        self.start_time = time.time()
        circle = 0
        done = 0.0  # 沿路线累计走过的距离(米)

        while self.running:
            t0 = time.time()
            cur_lat, cur_lng = self._pos_at(done, route, seg_starts)
            self._set_loc(cur_lat, cur_lng)
            shake_mumu()  # 摇一下手机，模拟步频

            dt = time.time() - t0   # 实测这一步实际耗时
            speed = self.speed_var.get()
            step_dist = speed * dt  # 这一步坐标应移动的距离 = 速度 × 实测时间

            done += step_dist
            self.total_distance += step_dist

            # 跑满一圈处理
            while done >= total_len:
                done -= total_len
                circle += 1
                self.root.after(0, lambda c=circle: self.circle_label.config(text=f"圈数: {c}"))
                self._log(f"一圈完成，累计 {self.total_distance:.0f} 米")
                if not self.loop_var.get():
                    self.running = False
                    break

            elapsed = time.time() - self.start_time
            self.root.after(0, lambda e=elapsed: self.time_label.config(text=f"用时: {e/60:.1f} 分钟"))
            self.root.after(0, lambda: self.dist_label.config(text=f"已跑距离: {self.total_distance:.0f} 米"))

        self._stop_mock()
        self.root.after(0, lambda: self.start_btn.config(state='normal'))
        self.root.after(0, lambda: self.stop_btn.config(state='disabled'))
        self._log("已停止，模拟定位已关闭")

    def open_map(self):
        """打开地图定位插件（简易版百度地图）"""
        if map_server.open_map():
            self._log("地图已打开，点击地图可跳转定位")
        else:
            messagebox.showerror("错误", "地图服务启动失败，可能端口被占用")

    def prepare_start(self):
        """定位到起点，不动"""
        route = load_route()
        if len(route) < 1:
            messagebox.showerror("错误", "路线文件为空！")
            return
        lat, lng = route[0]
        set_mumu_location(lat, lng)
        self._log(f"已定位到起点: {lat:.6f},{lng:.6f}")
        self._log("现在可以在APP里点开始跑步了，准备好后点「开始跑」")

    def start_run(self):
        if not os.path.exists(ROUTE_FILE):
            messagebox.showerror("错误", "找不到route.txt路线文件！")
            return

        route = load_route()
        if len(route) < 2:
            messagebox.showerror("错误", "路线点太少，请先编辑route.txt填好操场路线！")
            return

        self.running = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self._log("开始跑步...")
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop_run(self):
        self.running = False
        self._log("正在停止...")

    def on_closing(self):
        # 修复：窗口关闭前先停止模拟定位，不然手机会一直假定位
        if self.running:
            self.running = False
            time.sleep(0.5)  # 等子线程退出
        self._stop_mock()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
