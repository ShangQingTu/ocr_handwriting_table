from ocr import ocrFrom
from extractTable import extractTableFrom
from pdf2png import pdfConvert
import os


def main(pdf_position='pdfs'):
    # pdfConvert把pdf每一页转换为png,存放在data文件夹下,一个xx.pdf的png存进一个./data/xx文件夹
    pdfConvert(pdf_position)
    # 遍历在pdf文件夹中的文件,所以pdf名称最好不要重复
    for pdfName in os.listdir("./" + pdf_position):
        # dicName是pdf去掉后缀的名字
        dicName = pdfName[:-4]
        # 从./data/xx/yy.png里面提取出若干个表格yy_zz.png,存进./slice/xx文件夹
        extractTableFrom(dicName)
        # 对于这些表格图片,用讯飞ocr的接口提取出文字,存进./result/xx文件夹
        ocrFrom(dicName)


if __name__ == '__main__':
    # pdf_position是保留pdf文件的文件夹名称
    pdf_position = 'pdfs'
    main(pdf_position)
