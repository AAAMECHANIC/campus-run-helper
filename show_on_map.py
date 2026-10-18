import folium

# 读取路线点
points = []
with open("E:/跑步/route.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        lat, lng = map(float, line.split(","))
        points.append((lat, lng))

# 中心坐标
center_lat = sum(p[0] for p in points)/len(points)
center_lng = sum(p[1] for p in points)/len(points)

# 创建地图，用卫星影像底图
m = folium.Map(location=[center_lat, center_lng], zoom_start=17, tiles=None)

# 加卫星底图
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri Satellite',
    name='卫星地图'
).add_to(m)

# 画路线
folium.PolyLine(points, color="red", weight=4, opacity=0.8).add_to(m)

# 起点标个蓝点
folium.Marker(points[0], popup="起点", icon=folium.Icon(color='blue')).add_to(m)

# 保存成HTML
m.save("E:/跑步/路线卫星图.html")
print("卫星图已生成，打开E:/跑步/路线卫星图.html就能看")
