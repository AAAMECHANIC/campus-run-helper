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

# 10米宽：往内缩20米，往外扩20米，绿色带宽40米，肯定能看到
inner_scale = 0.997
outer_scale = 1.003

inner_lat = center_lat + (lat_smooth - center_lat)*inner_scale
inner_lng = center_lng + (lng_smooth - center_lng)*inner_scale
outer_lat = center_lat + (lat_smooth - center_lat)*outer_scale
outer_lng = center_lng + (lng_smooth - center_lng)*outer_scale

# 拼成多边形
poly_lng = np.concatenate([outer_lng, inner_lng[::-1]])
poly_lat = np.concatenate([outer_lat, inner_lat[::-1]])

plt.figure(figsize=(10,8))
plt.fill(poly_lng, poly_lat, color='lightgreen', alpha=0.8, label='跑道区域')
plt.plot(lng_smooth, lat_smooth, 'b-', linewidth=2, label='跑步路线')
plt.scatter([p[1] for p in original], [p[0] for p in original], c='red', s=30, label='你标的边界点')
plt.title("跑道条带效果图")
plt.legend()
plt.grid(True)
plt.axis('equal')
plt.savefig("E:/跑步/跑道条带图.png", dpi=100)
print("图已生成")
