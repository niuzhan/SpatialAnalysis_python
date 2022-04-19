import xlrd
import shapefile

xls = xlrd.open_workbook("gd_GDP.xls")
sheet = xls.sheet_by_index(0)

r = shapefile.Reader("guangdong/guangdong.shp", encoding="gbk")  # 读对象
w = shapefile.Writer("guangdong/gd_w", shapeType=r.shapeType, encoding='gbk')  # 写对象
w.fields = list(r.fields)  # 将旧shp对象的字段赋给新shp

for i in range(sheet.ncols-1):
    '''新添加lat，lon,pop,GDP 4个字段'''
    # 读取第一行表头信息
    w.field(str(sheet.cell(0, i+1).value), "F", 10, 5)

'''为新shp添加几何与属性信息'''
n = 1
for shaperec in r.iterShapeRecords():
    rec = shaperec.record
    j = 1
    lat = sheet.cell(n, j).value
    lon = sheet.cell(n, j+1).value
    GDP = sheet.cell(n, j+2).value * 100000000
    POP = sheet.cell(n, j+3).value * 10000
    rec.extend([lat, lon, GDP, POP])
    w.record(*rec)  # 添加属性信息
    print(*rec)
    w.shape(shaperec.shape)  # 添加几何信息
    n += 1


