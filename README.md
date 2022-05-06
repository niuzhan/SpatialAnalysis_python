# python空间分析实验代码仓库
## 遇到的坑：

### 实验1：

1.读的矢量文件属性表里有汉字的

![属性表](G:\研一下\python空间分析\实验报告\实验一\属性表.jpg)

代码中读写矢量文件这一步

```python
r = shapefile.Reader("guangdong/guangdong.shp") 
```

添加编码方式

```python
r = shapefile.Reader("guangdong/guangdong.shp", encoding="gbk") #采用gbk编码！
```

### 实验2：

注意用**float**类型读取landsat8波段

```python
RED = gdal_array.LoadFile(b4).astype(float)
NRI = gdal_array.LoadFile(b5).astype(float)
```

### 实验3：

1.新版本laspy中，读LAS文件由

```python
from laspy import File
#------------------------------
path = "xx.las"
las = File.file(path,mode='r')
```

更换为

```python
import laspy
#------------------------------
path = "xx.las"
las = laspy.open(path)
```

2.voronoi.py

```python
479 newedge.a = dx / dy
```

改为

```python
479 newedge.a = dx / (dy+float(1e-8))
```

3.主文件.py

```
w.poly([part])
```

改为

```python
w.polyz([part]) # 注意要换成 polyz !!!
```

