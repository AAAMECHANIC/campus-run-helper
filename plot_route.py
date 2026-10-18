import matplotlib.pyplot as plt

# 读取route.txt里的坐标
points = []
with open("E:/跑步/route.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        lat, lng = map(float, line.split(","))
        points.append((lng, lat))  # 经度x，纬度y

# 把点拆成x和y
x = [p[0] for p in points]
y = [p[1] for p in points]

# 画图
plt.figure(figsize=(10, 8))
plt.plot(x, y, 'b-o', linewidth=2, markersize=5)
plt.title("当前跑道路线图")
plt.xlabel("经度")
plt.ylabel("纬度")
plt.grid(True)
plt.axis('equal')  # 等比例，不然形状歪
plt.savefig("E:/跑步/路线图.png", dpi=100)
print("图已保存到E:/跑步/路线图.png")
