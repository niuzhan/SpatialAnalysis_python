import pickle
import os
import time
import math
import numpy as np
import shapefile
import laspy
import voronoi

# LAS源文件
source = "points.las"
# 输出的Shapefile文件
target = "mesh"
# 三角形数据文件归档
archive = "triangles.p"
# Pyshp文件归档
pyshp = "mesh_pyshp.p"

class Point(object):
    """Point类需要调用的voronoi模块"""
    def __init__(self, x, y):
        self.px = x
        self.py = y
    def x(self):
        return self.px
    def y(self):
        return self.py

# 三角形数组保存的三点索引元组用于点集查询
# voronoi模块载入归档文件创建三角面
triangles = None

if os.path.exists(archive):
    print("Loading triangle archive...")
    f = open(archive, "rb")
    triangles = pickle.load(f)
    f.close()
    # 打开LIDAR的LAS文件
    las= laspy.read(source)
else:
    # 打开LIDAR的LAS文件
    las = laspy.read(source)
    points = []
    print("Assembling points...")
    # 从LAS文件中读取点集
    for x, y in np.nditer((las.x, las.y)):
        points.append(Point(x, y))
    print("Composing triangles..")
    # Delaunay三角剖分
    triangles = voronoi.computeDelaunayTriangulation(points)
    # 如果写入的Shapefile文件有多个，可以先保存三角面记录
    f = open(archive, "wb")
    pickle.dump(triangles, f, protocol=2)
    f.close()
print("Creating shapefile...")
w = None
if os.path.exists(pyshp):
    f = open(pyshp, "rb")
    w = pickle.load(f)
    f.close()
else:
    # PolygonZ shapefile (x, y, z, m)
    w = shapefile.Writer(target, shapefile.POLYGONZ)
    w.field("X1", "C", "40")
    w.field("X2", "C", "40")
    w.field("X3", "C", "40")
    w.field("Y1", "C", "40")
    w.field("Y2", "C", "40")
    w.field("Y3", "C", "40")
    w.field("Z1", "C", "40")
    w.field("Z2", "C", "40")
    w.field("Z3", "C", "40")
    tris = len(triangles)
    # 遍历所有形状，进度信息每10%更新一次
    last_percent = 0
    for i in range(tris):
        t = triangles[i]
        percent = int((i/(tris * 1.0)) * 100.0)
        if percent % 10.0 == 0 and percent > last_percent:
            last_percent = percent
        print("{} % done - Shape {}/{} at {}".format(percent, i, tris, time.asctime()))
        part = []
        x1 = las.x[t[0]]
        y1 = las.y[t[0]]
        z1 = las.z[t[0]]
        x2 = las.x[t[1]]
        y2 = las.y[t[1]]
        z2 = las.z[t[1]]
        x3 = las.x[t[2]]
        y3 = las.y[t[2]]
        z3 = las.z[t[2]]
        # 沿凸包边缘进行海量三角面片段检查
        # 这在Delaunay三角剖分中是很普遍的操作
        max = 3
        if math.sqrt((x2-x1)**2+(y2-y1)**2) > max:
            continue
        if math.sqrt((x3-x2)**2+(y3-y2)**2) > max:
            continue
        if math.sqrt((x3-x1)**2+(y3-y1)**2) > max:
            continue
        part.append([x1, y1, z1, 0])
        part.append([x2, y2, z2, 0])
        part.append([x3, y3, z3, 0])
        w.polyz([part])  # 注意要换成 polyz !!!
        w.record(x1, x2, x3, y1, y2, y3, z1, z2, z3)
print("Saving shapefile...")
# 归档写入数据以防万一。并确保在重新创建
# 这些shapefile文件之前将其删除
f = open(pyshp, "wb")
pickle.dump(w, f, protocol=2)
f.close()
w.save(target)
print("Done.")