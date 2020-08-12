from Picture import work
from pdf2png import pdfConvert
from imgcorr import correct_tilt_img
import os


def main(pdf_position='pdfs'):
    # pdfConvert把pdf每一页转换为png,存放在data文件夹下,一个xx.pdf的png存进一个./data/xx文件夹
    pdfConvert(pdf_position)

    # 遍历在pdf文件夹中的文件,所以pdf名称最好不要重复
    for pdfName in os.listdir("./" + pdf_position):
        # dicName是pdf去掉后缀的名字
        dicName = pdfName[:-4]
        # 矫正图片
        data_path = os.path.join("data", dicName)
        for imgName in os.listdir(data_path):
            img_path = os.path.join(data_path, imgName)
            correct_tilt_img(img_path)
        # 从./data/xx/yy.png里面提取出若干个表格yy_zz.png,存进./result/cut/xx文件夹
        # work(dicName)


if __name__ == '__main__':
    # pdf_position是保留pdf文件的文件夹名称
    pdf_position = 'pdfs'
    main(pdf_position)
