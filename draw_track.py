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
u_new = np.linspace(0, 1, 100)
lng_smooth, lat_smooth = splev(u_new, tck)

# 中心
center_lat = np.mean(lat)
center_lng = np.mean(lng)

# 画10米宽条带：往内、往外各5米
half_width = 0.00003  # 5米半宽，总宽10米
inner_lat = center_lat + (lat_smooth - center_lat)*0.9993
inner_lng = center_lng + (lng_smooth - center_lng)*0.9993
outer_lat = center_lat + (lat_smooth - center_lat)*1.0007
outer_lng = center_lng + (lng_smooth - center_lng)*1.0007

plt.figure(figsize=(10,8))
# 画跑道带：填充内外两条线之间的区域
plt.fill_betweenx(outer_lat, inner_lng, outer_lng, color='lightgreen', alpha=0.5, label='10米宽跑道')
plt.plot(lng_smooth, lat_smooth, 'b-', linewidth=2, label='跑步中心线')
plt.title("10米宽跑道条带效果")
plt.legend()
plt.grid(True)
plt.axis('equal')
plt.savefig("E:/跑步/10米宽跑道效果图.png", dpi=100)
print("效果图已保存")
