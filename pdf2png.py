import fitz
import os

def pdfConvert(position):
    name = os.listdir('./%s' % position)
    for n in name:

        #  打开PDF文件，生成一个对象
        path = r'./pdfs/%s' % n

        doc = fitz.open(path)

        for pg in range(doc.pageCount):
            page = doc[pg]
            rotate = int(0)
            # 每个尺寸的缩放系数为2，这将为我们生成分辨率提高四倍的图像。
            zoom_x = 2
            zoom_y = 2
            trans = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
            pm = page.getPixmap(matrix=trans, alpha=False)

            dir_1 = './data/%s/' % n[:-4]
            mkdirlambda = lambda x: os.makedirs(x) if not os.path.exists(x) else True  # 目录是否存在,不存在则创建
            mkdirlambda(dir_1)

            pm.writePNG('%s%s.png' % (dir_1,pg+1))

# position = 'pdfs'  # 这个就是pdf文件需要转png的文件位置
# pdfConvert(position)
