import cv2
import numpy as np
import xlsxwriter
# import pytesseract
import os
from util import count_distence, make_points, clustering, clust_rows, clust_columns
from extractTable import FindContours
from ocr import process


class Picture():
    def __init__(self, img, xs, ys):
        self.img = img
        self.points = make_points(xs=xs, ys=ys)
        self.clusts = clustering(self.points)
        self.clust_center_points = self.get_center_points()
        self.row_points = clust_rows(self.clust_center_points)
        self.col_points = clust_columns(self.clust_center_points)
        for col in self.col_points:
            print("col", col)
        for row in self.row_points:
            print("row", row)
        # 最大的行数列数
        self.row_max_num, self.col_max_num = self.get_max_num()
        # 最长行,最长列的坐标
        self.longest_row, self.longest_col = self.get_longest()
        # 定下坐标标准,为excel分格子做依据, 过滤孤立点,得到网格
        self.standard_x_locations = sorted([x[0] for x in self.longest_row])
        # self.standard_x_locations = self.standard_x_locations.sort()
        self.standard_y_locations = sorted([x[1] for x in self.longest_col])
        # self.standard_y_locations = self.standard_y_locations.sort()
        print("standard_x_locations", self.standard_x_locations)
        print("standard_y_locations", self.standard_y_locations)

    def get_center_points(self):
        # 每个clust里面取一个点做代表
        clust_center_points = []
        for clust in self.clusts:
            clust_center_points.append(clust[0])
        return clust_center_points

    def get_max_num(self):
        # 最大的行数列数
        row_max_num = 0
        col_max_num = 0
        for row in self.row_points:
            # len(row)是一行有多少列
            col_max_num = max(len(row), col_max_num)
        for col in self.col_points:
            row_max_num = max(len(col), row_max_num)
        return row_max_num, col_max_num

    def get_longest(self):
        longest_row = []
        longest_col = []
        for row in self.row_points:
            if len(row) == self.col_max_num:
                longest_row = row
                break
        for col in self.col_points:
            if len(col) == self.row_max_num:
                longest_col = col
                break
        return longest_row, longest_col

    def wirte_excel(self, filepath, dicName, cutImg_name):
        # 保存cut
        pdfName_path = os.path.join(filepath, "cut", dicName)
        if not os.path.exists(pdfName_path):
            os.mkdir(pdfName_path)
        cutImg_path = os.path.join(pdfName_path, cutImg_name)
        if not os.path.exists(cutImg_path):
            os.mkdir(cutImg_path)
        # 创建一个新Excel文件并添加一个工作表
        save_xls_path = os.path.join(cutImg_path, "pic_excel.xls")
        workbook = xlsxwriter.Workbook(save_xls_path)
        worksheet = workbook.add_worksheet()
        print("row_num", self.row_max_num)
        for i in range(self.row_max_num):
            for j in range(self.col_max_num):
                x0 = self.standard_x_locations[j]
                y0 = self.standard_y_locations[i]
                label = "(%d,%d)" % (x0, y0)
                if i < self.row_max_num - 1 and j < self.col_max_num - 1:
                    x1 = self.standard_x_locations[j + 1]
                    y1 = self.standard_y_locations[i + 1]
                    print("x0,x1", x0, x1)
                    print("y0,y1", y0, y1)
                    cut_img = self.img[y0:y1, x0:x1]
                    save_path = cutImg_path + '/' + str(i) + '_' + str(j) + '.png'
                    print(save_path)
                    cv2.imwrite(save_path, cut_img)  # 保存截取的图片
                    # 在单元格里写入图片
                    worksheet.insert_image(2 * i + 1, 3 * j + 1,
                                           save_path,
                                           {'x_scale': 0.5, 'y_scale': 0.5})
                    # 在单元格里写入识别字
                    word = process(save_path)
                    worksheet.write(2 * i + 1, 3 * j + 2, word)
                    # worksheet.write(2 * i + 1, 2 * j + 1, word)
                # 在单元格里写入对应的坐标值
                worksheet.write(2 * i, 3 * j, label)
                # worksheet.write(2 * i, 2 * j, label)

        workbook.close()  # 保存文件


def work(dicName):
    slice_path = os.path.join("./data", dicName)
    for rawImgName in os.listdir(slice_path):
        pic_path = os.path.join(slice_path, rawImgName)
        print(pic_path)
        img, Net_img, contours = FindContours(pic_path)
        # 识别黑白图中的白色点
        ys, xs = np.where(Net_img > 0)
        # 聚类等过程
        picture = Picture(img, xs, ys)
        # 写excel
        cutImg_name = pic_path.split('/')[-1][:-4]
        cv2.imshow("Net_img", Net_img)
        cv2.waitKey(10)
        # try:
        #     picture.wirte_excel('result', dicName, cutImg_name)
        # except:
        #     continue
        picture.wirte_excel('result', dicName, cutImg_name)


if __name__ == '__main__':
    work("操作票")
