import cv2
import numpy as np
import xlsxwriter
# import pytesseract
import os
from util import count_distence, make_points, clustering, clust_rows, clust_columns, same_row_thres
from extractTable import FindContours
from ocr import process


class Picture():
    def __init__(self, img, xs, ys):
        self.img = img
        self.img_width = len(img[0])
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
        cv2.imshow("img", img)
        cv2.waitKey(10)

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

    # def get_interval(self):
    #     intervals = []
    #     for i in range(len(self.standard_y_locations)):
    #         if i != 0:
    #             interval = self.standard_y_locations[i] - self.standard_y_locations[i - 1]
    #             intervals.append(interval)
    #     print("interval all ", intervals)
    #     return 10

    def get_upper_line_num(self, clust_row):
        for i in range(len(clust_row)):
            if abs(clust_row[i][0] - self.standard_y_locations[0]) < same_row_thres:
                return i + 1

    def get_under_line_i(self, clust_row):
        for i in range(len(clust_row)):
            if abs(clust_row[i][0] - self.standard_y_locations[-1]) < same_row_thres:
                return i + 1

    def get_col_loc4row(self, row_num):
        # 对于第几行的列坐标是那些
        row_loc = self.standard_y_locations[row_num]
        col_locs = []
        for row in self.row_points:
            # 第一个点y做代表
            if abs(row[0][1] - row_loc) < same_row_thres:
                # 同一行的点的x坐标
                for point in row:
                    col_locs.append(point[0])
                return col_locs

    def wirte_excel(self, filepath, dicName, cutImg_name, clust_row):
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
        # 表格之上,有 整间隔 + 1行
        upper_line_num = self.get_upper_line_num(clust_row)
        # if upper_line_num != 1:
        # 等于一说明表格最上面就是图片最上面
        interval = clust_row[1][0] - clust_row[0][0]
        # 实际上是从最上一条线上面的内容行开始的,相当于多画了upper_line_num行
        upper_start_y = clust_row[0][0] - interval
        for i in range(upper_line_num):
            if i == upper_line_num - 1:
                next_line_y = self.standard_y_locations[0]
            else:
                next_line_y = clust_row[i][0]
            cut_img = self.img[upper_start_y:next_line_y, :]
            save_path = cutImg_path + '/' + str(i) + '.png'
            cv2.imwrite(save_path, cut_img)  # 保存截取的图片
            worksheet.insert_image(2 * i + 1, 0,
                                   save_path,
                                   {'x_scale': 0.5, 'y_scale': 0.5})
            word = process(save_path)
            worksheet.write(2 * i + 1, 1, word)
            # 在单元格里写入对应的坐标值
            label = "(%d,%d)" % (0, upper_start_y)
            worksheet.write(2 * i, 0, label)
            upper_start_y = next_line_y
        # 多画了upper_line_num行
        self.row_max_num += upper_line_num
        # 表格
        print("row_num", self.row_max_num)
        for i in range(upper_line_num, self.row_max_num):
            if i == self.row_max_num - 1:
                break
            col_locs = sorted(self.get_col_loc4row(i - upper_line_num))
            print("col_locs,", col_locs)
            col_num = len(col_locs)
            for j in range(col_num):
                x0 = col_locs[j]
                y0 = self.standard_y_locations[i - upper_line_num]
                label = "(%d,%d)" % (x0, y0)
                #加了判断
                if i < self.row_max_num - 1 and j < col_num - 1:
                    x1 = col_locs[j + 1]
                    y1 = self.standard_y_locations[i + 1 - upper_line_num]
                    print("x0,x1", x0, x1)
                    print("y0,y1", y0, y1)
                    cut_img = self.img[y0:y1, x0:x1]
                    save_path = cutImg_path + '/' + str(i - upper_line_num) + '_' + str(j) + '.png'
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
        # 表格区下方
        first_under_line_i = self.get_under_line_i(clust_row)
        under_start_y = self.standard_y_locations[-1]

        for clust_number in range(first_under_line_i, len(clust_row)):
            next_line_y = clust_row[clust_number][0]
            cut_img = self.img[under_start_y:next_line_y, :]
            i = clust_number - first_under_line_i + self.row_max_num
            save_path = cutImg_path + '/' + str(i) + '.png'
            cv2.imwrite(save_path, cut_img)  # 保存截取的图片
            worksheet.insert_image(2 * i + 1, 0,
                                   save_path,
                                   {'x_scale': 0.5, 'y_scale': 0.5})
            try:
                word = process(save_path)
            except TypeError:
                word = ""
            worksheet.write(2 * i + 1, 1, word)
            # 在单元格里写入对应的坐标值
            label = "(%d,%d)" % (0, under_start_y)
            worksheet.write(2 * i, 0, label)
            under_start_y = next_line_y
        workbook.close()  # 保存文件


def work(dicName):
    slice_path = os.path.join("./data", dicName)
    for rawImgName in os.listdir(slice_path):
        # rawImgName = "2.png"
        pic_path = os.path.join(slice_path, rawImgName)
        print(pic_path)
        img, Net_img, contours, row_locations = FindContours(pic_path)
        # 获取直线的y坐标聚类
        clust_row = clust_rows(row_locations, False)
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
        picture.wirte_excel('result', dicName, cutImg_name, clust_row)


if __name__ == '__main__':
    work("操作票")
    # work("工作票")
