import math
import shapefile
from PIL import Image, ImageDraw

def world2screen(bbox, w,h, x, y):
    '''地理坐标转换为屏幕坐标'''
    minx,miny,maxx,maxy = bbox
    xdist=maxx-minx
    ydist=maxy-miny
    xratio=w/xdist
    yratio=h/ydist
    px=int(w-((maxx-x) * xratio))
    py=int((maxy - y) * yratio)
    return (px,py)


inShp = shapefile.Reader("gd_UTM/gd_utm.shp", encoding='gbk')
# inShp = shapefile.Reader("guangdong/gd_w", encoding='gbk')
iwidth = 1200
iheight = 800
# 初始化PIL库的Image对象
img = Image.new("RGB", (iwidth, iheight), (255,255, 255))
# PIL库的Draw模块用于填充多边形
draw = ImageDraw.Draw(img)

fieldNames = [item[0] for item in inShp.fields[1:]]
GDP_index = fieldNames.index('GDP')
pop_index = fieldNames.index('POP')

for sr in inShp.iterShapeRecords():
    density = sr.record[GDP_index]/sr.record[pop_index]
    # weight可以用来配置人口相关的颜色深度
    weight = min(math.sqrt(density/10000.0), 1.0)*200
    R = int(5+weight)
    G = int(15+weight)
    B = int(45+weight)
    pixels = []
    for x, y in sr.shape.points:
        (px, py) = world2screen(inShp.bbox, iwidth, iheight, x, y)
        pixels.append((px, py))
    draw.polygon(pixels, outline=(255, 255, 255), fill=(R, G ,B))

img.save("./equivalent.png")

