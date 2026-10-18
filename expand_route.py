import math

# 原24个点
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
    (45.720121,126.621998),
]

# 计算中心
center_lat = sum(p[0] for p in original)/len(original)
center_lng = sum(p[1] for p in original)/len(original)

# 向外扩5米：纬度方向5米≈0.000045度，经度方向5米≈0.000065度
expand_lat = 0.000045  # 5米纬度
expand_lng = 0.000065  # 5米经度

new_points = []
for lat, lng in original:
    # 计算点相对于中心的方向
    dx = lng - center_lng
    dy = lat - center_lat
    # 单位向量
    dist = math.sqrt(dx*dx + dy*dy)
    ux = dx / dist
    uy = dy / dist
    # 往外扩
    new_lat = lat + uy * expand_lat
    new_lng = lng + ux * expand_lng
    new_points.append((new_lat, new_lng))

# 保存新路线
with open("E:/跑步/route.txt", "w", encoding="utf-8") as f:
    f.write("# 向外扩5米后的跑道路线\n")
    for lat, lng in new_points:
        f.write(f"{lat:.6f},{lng:.6f}\n")
    # 最后一个点回到第一个点闭环
    f.write(f"{new_points[0][0]:.6f},{new_points[0][1]:.6f}\n")

print("扩好的路线已保存")

# 画图
import matplotlib.pyplot as plt
x_old = [p[1] for p in original]
y_old = [p[0] for p in original]
x_new = [p[1] for p in new_points]
y_new = [p[0] for p in new_points]

plt.figure(figsize=(10,8))
plt.plot(x_old, y_old, 'r--', label='原路线')
plt.plot(x_new, y_new, 'b-o', linewidth=2, markersize=5, label='向外扩5米后')
plt.title("路线向外扩5米效果")
plt.legend()
plt.grid(True)
plt.axis('equal')
plt.savefig("E:/跑步/扩5米效果图.png", dpi=100)
print("效果图已保存")
