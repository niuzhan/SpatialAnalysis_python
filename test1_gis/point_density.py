import random
import shapefile
import pngcanvas

def point_in_poly(x, y, poly):
    '''判断一个点是否在多边形内部'''
    # 判断点是否是顶点
    if (x,y) in poly: return True
    # 判断点是否在边框上
    for i in range(len(poly)):
        p1 = None
        p2 = None
        if i == 0:
            p1 = poly[0]
            p2 = poly[1]
        else:
            p1 = poly[i-1]
            p2 = poly[i]
        if p1[1] == p2[1] and p1[1] == y and x > min(p1[0], p2[0]) and x < max(p1[0], p2[0]):
            return True
    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(n+1):
        p2x, p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y
    if inside:
        return True
    else:
        return False

def world2screen(bbox, w, h, x, y):
    '''地理坐标转换为屏幕坐标'''
    minx, miny, maxx, maxy = bbox
    xdist = maxx-minx
    ydist = maxy-miny
    xratio = w/xdist
    yratio = h/ydist
    px = int(w-((maxx-x) * xratio))
    py = int((maxy-y)*yratio)
    return (px,py)

# inShp = shapefile.Reader("gd_UTM/gd_utm", encoding='gbk')
inShp = shapefile.Reader("guangdong/gd_w", encoding='gbk')

# 设置输出图片尺寸
iwidth = 1200
iheight = 800
dots = []
# 获取人口记录索引
# fieldNames = [item[0] for item in inShp.fields[1:]]
# pop_index = fieldNames.index('POP')
for i, f in enumerate(inShp.fields):
    # 找到“人口”字段的索引
    if f[0] == "POP":
        pop_index = i-1

# 计算点密度并绘制相关点
for sr in inShp.iterShapeRecords():
    population = sr.record[pop_index]
    desity = population/10000
    found = 0
    # 随机绘制点，直到密度达到指定比率
    while found < desity:
        minx, miny, maxx, maxy = sr.shape.bbox
        x = random.uniform(minx, maxx)
        y = random.uniform(miny, maxy)
        if point_in_poly(x, y, sr.shape.points):
            dots.append((x, y))
            found += 1
# 为输出PNG图片做准备
c = pngcanvas.PNGCanvas(iwidth, iheight)
# 绘制红色的点
c.color = (255, 0, 0, 0xff)
for d in dots:
    x, y = world2screen(inShp.bbox,iwidth,iheight, *d)
    c.filled_rectangle(x-1, y-1, x+1, y+1)
# 绘制人口普查区域

c.color = (0, 0, 0, 0xff)
for s in inShp.iterShapes():
    pixels = []
    for p in s.points:
        pixel = world2screen(inShp.bbox, iwidth, iheight, *p)
        pixels.append(pixel)
    c.polyline(pixels)
# 保存图片
img = open("./DotDensity.png", "wb")
img.write(c.dump())
img.close()