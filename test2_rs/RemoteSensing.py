import numpy as np
import shapefile
from PIL import Image, ImageDraw
from osgeo import gdal_array, gdal


def world2Pixel(geoMatrix, x, y):
    """ 使用GDAL库的geomatrix对象（(gdal.GetGeoTransform())）计算地理坐标的像素位置 """
    ulx = geoMatrix[0]
    ulY = geoMatrix[3]
    xDist = geoMatrix[1]
    yDist = geoMatrix[5]
    rtnX = geoMatrix[2]
    rtnY= geoMatrix[4]
    pixel = int((x-ulx)/xDist)
    line = int((ulY-y)/abs(yDist))
    return (pixel,line)

def imageToArray(i):
    """ 将一个Python影像库的数组转换为一个gdal_array图片 """
    a = gdal_array.numpy.frombuffer(i.tobytes(), 'b')
    a.shape = i.im.size[1], i.im.size[0]
    return a

b4 = r'LC81200382021277LGN00/LC08_L1TP_120038_20211004_20211013_01_T1_B4.TIF'  # 红外波段
b5 = r'LC81200382021277LGN00/LC08_L1TP_120038_20211004_20211013_01_T1_B5.TIF'  # 近红外波段

RED = gdal_array.LoadFile(b4).astype(float)
NRI = gdal_array.LoadFile(b5).astype(float)
gdal_array.numpy.seterr(all="ignore")
NDVI = ((NRI-RED))/((NRI+RED)) # 计算归一化植被指数的公式
nan_index = np.isnan(NDVI)
NDVI[nan_index] = 0  # 将not a number(0/0无意义）的像素值赋为0
NDVI = NDVI.astype(np.float32)
output = gdal_array.SaveArray(NDVI, 'output_ndvi.tif', format="GTiff", prototype=b4)  # 调用原图片，输出计算NDVI后的结果
output = None

'''
开始对原图像裁剪出南京区域
'''
# 使用PyShp库打开Shapefile(南京)文件
r = shapefile.Reader('./nanjing/nanjing_utm.shp', encoding='gbk')  # 使用pyshp打开南京矢量文件
raster = 'output_ndvi.tif'  # 被裁剪的源数据-计算NDVI后的gdal_array对象
src = gdal.Open(raster)
geoTrans = src.GetGeoTransform()

# 将图层扩展转换为图片像素坐标
minX, minY, maxX, maxY = r.bbox
ulX, ulY = world2Pixel(geoTrans, minX, maxY)
lrX, lrY = world2Pixel(geoTrans, maxX, minY)

# 计算新图片的像素尺寸
pxWidth = int(lrX-ulX)
pXHeight = int(lrY-ulY)
clip = NDVI[ulY:lrY, ulX:lrX]
# 为图片创建一个新的geomatrix对象以便附加地理参照数据
geoTrans = list(geoTrans)
geoTrans[0] = minX
geoTrans[3] = maxY
# 把南京边界线(点)映射为像素
pixels = []
for p in r.shape(0).points:
    pixels.append(world2Pixel(geoTrans, p[0], p[1]))
rasterPoly = Image.new("L", (pxWidth, pXHeight), 1)  # 创建一个空白的8字节黑白遮罩图片
# 使用PIL创建一个空白图片用于绘制多边形
rasterize = ImageDraw.Draw(rasterPoly)
rasterize.polygon(pixels, 0)  # 完成绘制多边形（南京）
# 将PIL图片转换为NumPy遮罩数组
mask = imageToArray(rasterPoly)
# 掩膜与原图像做交运算
clip = gdal_array.numpy.choose(mask, (clip, 1))
out = gdal_array.SaveArray(clip, 'nanjing_clip.tif', format="GTiff", prototype=raster)
out = None
'''对裁剪后的图像基于其NDVI指数进行分类'''
# 输入文件（南京NDVI结果）
none_classify = gdal_array.LoadFile('nanjing_clip.tif')  # 加载裁剪后的图像
# 根据类别数目将直方图分割成5个颜色区间
classes = gdal_array.numpy.histogram(none_classify, bins=5)[1]
# 颜色查找表的记录数必须为len(classes)+1
# 声明R、G、B 元组
colors = [[255, 255, 255], [51, 153, 255], [255, 255, 51], [105, 179, 14], [0, 255, 0], [255, 255, 255]]
# 分类初始值
start = -1
# 创建一个RGB颜色的JPEG输出图片
rgb = gdal_array.numpy.zeros((3, none_classify.shape[0], none_classify.shape[1]), gdal_array.numpy.float32)
# 处理每个类别并分配颜色
for i in range(len(classes)):
    mask1 = gdal_array.numpy.logical_and(start<=none_classify, none_classify<=classes[i])
    for j in range(len(colors[i])):
        rgb[j] = gdal_array.numpy.choose(mask1, (rgb[j], colors[i][j]))
        start = classes[i] + 0.001
# 保存图片
classify_result = gdal_array.SaveArray(rgb.astype(gdal_array.numpy.uint8), 'nanjing_classificaiton.jpg', format='jpeg')
classify_result = None

