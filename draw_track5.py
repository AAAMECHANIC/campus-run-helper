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
original.append(original[0])

lat = np.array([p[0] for p in original])
lng = np.array([p[1] for p in original])

tck, u = splprep([lng, lat], s=0.0000002, per=True)
u_new = np.linspace(0, 1, 200)
lng_smooth, lat_smooth = splev(u_new, tck)

# 中心
center_lat = np.mean(lat)
center_lng = np.mean(lng)

# 10米宽：往内5米，往外5米
half_width = 0.00008  # 半宽，总宽大概20米，明显点
inner_lat = center_lat + (lat_smooth - center_lat)*(1 - half_width)
inner_lng = center_lng + (lng_smooth - center_lng)*(1 - half_width)
outer_lat = center_lat + (lat_smooth - center_lat)*(1 + half_width)
outer_lng = center_lng + (lng_smooth - center_lng)*(1 + half_width)

plt.figure(figsize=(10,8), dpi=120)
# 画跑道中心线，黑色实线
plt.plot(lng_smooth, lat_smooth, 'k-', linewidth=2, label='跑步路线')
# 外边界：红色点划线
plt.plot(outer_lng, outer_lat, 'r-.', linewidth=2, label='跑道外边界')
# 内边界：蓝色点划线
plt.plot(inner_lng, inner_lat, 'b-.', linewidth=2, label='跑道内边界')
# 中间填充浅灰色
plt.fill(np.concatenate([outer_lng, inner_lng[::-1]]),
         np.concatenate([outer_lat, inner_lat[::-1]]),
         color='lightgray', alpha=0.7)

plt.title("10米宽跑道示意图")
plt.legend(loc='upper right')
plt.grid(True)
plt.axis('equal')
plt.savefig("E:/跑步/跑道示意图.png", dpi=120)
print("图已生成")
