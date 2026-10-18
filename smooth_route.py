import numpy as np
from scipy.interpolate import splprep, splev
import matplotlib.pyplot as plt

# 原路线点
original = [
    (45.720093,126.622232),
    (45.720169,126.622202),
    (45.720175,126.621796),
    (45.720166,126.621571),
    (45.720144,126.621320),
    (45.720115,126.621032),
    (45.720081,126.620790),
    (45.720043,126.620574),
    (45.719939,126.620413),
    (45.719804,126.620296),
    (45.719668,126.620318),
    (45.719458,126.620426),
    (45.719376,126.620574),
    (45.719366,126.620866),
    (45.719366,126.621091),
    (45.719395,126.621338),
    (45.719420,126.621580),
    (45.719442,126.621810),
    (45.719486,126.622034),
    (45.719568,126.622241),
    (45.719712,126.622353),
    (45.719917,126.622331),
]

# 闭合：加第一个点到最后
original.append(original[0])

# 拆成x和y
lat = np.array([p[0] for p in original])
lng = np.array([p[1] for p in original])

# B样条平滑
tck, u = splprep([lng, lat], s=0.0000002, per=True)
u_new = np.linspace(0, 1, 100)
lng_smooth, lat_smooth = splev(u_new, tck)

# 向内缩一点，在跑道中间（大概往里缩8米，在跑道中间）
# 计算中心
center_lat = np.mean(lat)
center_lng = np.mean(lng)

# 把平滑后的点往中心方向缩8米
scale_lat = 0.9995  # 缩一点
scale_lng = 0.9995
lat_mid = center_lat + (lat_smooth - center_lat)*scale_lat
lng_mid = center_lng + (lng_smooth - center_lng)*scale_lng

# 保存路线，每4个点取一个，减少点数量
step = 4
final_points = list(zip(lat_mid[::step], lng_mid[::step]))

with open("E:/跑步/route.txt", "w", encoding="utf-8") as f:
    f.write("# 平滑后的跑道路线（封闭椭圆，在跑道中间）\n")
    for la, ln in final_points:
        f.write(f"{la:.6f},{ln:.6f}\n")
    # 闭环
    f.write(f"{final_points[0][0]:.6f},{final_points[0][1]:.6f}\n")

print("平滑路线已保存")

# 画图
plt.figure(figsize=(10,8))
plt.plot(lng, lat, 'r--o', markersize=3, label='原始折线点')
plt.plot(lng_mid, lat_mid, 'b-', linewidth=2, label='平滑后跑道')
plt.title("平滑后的封闭跑道路线")
plt.legend()
plt.grid(True)
plt.axis('equal')
plt.savefig("E:/跑步/平滑路线图.png", dpi=100)
print("效果图已保存")
