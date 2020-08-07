# 聚类的门槛
distence_thres = 4
# 判断孤立点的门槛
isolat_thres = 10
# 判断是同一列/行的门槛
same_col_thres = 10
same_row_thres = 10

def make_points(xs, ys):
    points = []
    for i in range(len(ys)):
        x, y = (xs[i], ys[i])
        points.append((x, y))
    return points

def count_distence(point1, point2):
    x1 = point1[0]
    x2 = point2[0]
    y1 = point1[1]
    y2 = point2[1]
    return pow(pow(x1 - x2, 2) + pow(y1 - y2, 2), 0.5)

def clustering(points):
    # 记录相近点的所有类
    clusts = []
    checked_points = []
    for point in points:
        if point in checked_points:
            continue
        # 相近点聚成一个类
        clust = []
        for point2 in points:
            distence = count_distence(point, point2)
            if distence < distence_thres:
                clust.append(point2)
                checked_points.append(point2)
        clusts.append(clust)
    return clusts

def clust_columns(clust_center_points):
    # 找出同一列的点
    col_points = []
    checked_points = []
    for point in clust_center_points:
        if point in checked_points:
            continue
        # 相近点聚成一个类
        col = []
        for point2 in clust_center_points:
            # x方向距离
            distence = abs(point[0] - point2[0])
            if distence < same_col_thres:
                col.append(point2)
                checked_points.append(point2)
        col_points.append(col)

    return col_points


def clust_rows(clust_center_points):
    # 找出同一行的点
    row_points = []
    checked_points = []
    for point in clust_center_points:
        if point in checked_points:
            continue
        # 相近点聚成一个类
        row = []
        for point2 in clust_center_points:
            # y方向距离
            distence = abs(point[1] - point2[1])
            if distence < same_row_thres:
                row.append(point2)
                checked_points.append(point2)
        row_points.append(row)

    return row_points
