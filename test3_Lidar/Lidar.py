import colorsys

from PIL import Image,ImageOps
import laspy
import numpy as np

# LAS源文件
source = "points.las"
# 输出的ASCII DEM文件
target = "points.asc"
# 网格尺寸（数据单位）
cell = 1.0
# 输出的DEM的NODATA值
NODATA = 0
# 打开LIDAR的LAS的文件
las = laspy.read(source)
# xyz的极值
min = las.header.min
max = las.header.max
# 以m为单位获取x轴的距离
xdist = max[0] - min[0]
# 以m为单位获取y轴的距离
ydist = max[1] - min[1]
# 网格的列数
cols = int(xdist/cell)
# 网格的行数
rows = int(ydist/cell)

cols += 1
rows += 1
# 统计平均高程值数量
count = np.zeros((rows, cols)).astype(np.float32)
# 平均高程值
zsum = np.zeros((rows, cols)).astype(np.float32)
# y分辨率是负值
ycell = -1 * cell
# 将x,y的值投影到网络
projx = (las.x-min[0]) / cell
projy = (las.y-min[1]) / ycell
# 将数据转换为整数并提取部分用作索引
ix = projx.astype(np.int32)
iy = projy.astype(np.int32)

# 遍历x,y,z数组，将其添加到网格形状中并添加平均值
for x, y, z in np.nditer([ix, iy, las.z]):
    count[y, x] +=1
    zsum[y,x] += z
# 修改0值为1避免numpy报错以及数组出现NaN值
nonzero = np.where(count>0,count,1)
# 平均化z值
zavg = zsum / nonzero
# 将0值插入数组中避免网格出现缺口
mean = np.ones((rows, cols)) * np.mean(zavg)
left = np.roll(zavg, -1, 1)
lavg = np.where(left > 0, left, mean)
right = np.roll(zavg, 1, 1)
ravg = np.where(right > 0, right, mean)
interpolate = (lavg + ravg) / 2
fill = np.where(zavg > 0, zavg, interpolate)

# 创建ASCII DEM的头部信息
header = "ncols {}\n".format(fill.shape[1])
header += "nrows {}\n".format(fill.shape[0])
header += "xllcorner {}\n".format(min[0])
header += "yllcorner {}\n".format(min[1])
header += "cellsize {}\n".format(cell)
header += "NODATA_value {}\n".format(NODATA)

# 打开输出文件，添加头部信息，保存数组
with open(target, "wb") as f:
    f.write(bytes(header, 'UTF-8'))
    np.savetxt(f, fill, fmt="%1.2f")

# Lidar-DEM文件
src = "points.asc"
# 可视化图片
pic = "lidar.bmp"

arr = np.loadtxt(src, skiprows=6)
im = Image.fromarray(arr).convert('L')

im = ImageOps.equalize(im)
im = ImageOps.autocontrast(im)

palette = []
h = .67
s = 1
v = 1

step = h/256.0
for i in range(256):
    rp, gp, bp = colorsys.hsv_to_rgb(h, s, v)
    r = int(rp * 255)
    g = int(gp * 255)
    b = int(bp * 255)
    palette.extend([r, g, b])
    h -= step
im.putpalette(palette)

im.save(pic)



