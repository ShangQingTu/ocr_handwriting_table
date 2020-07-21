# -*- coding: utf-8 -*-
from urllib import parse
import base64
import hashlib
import time
import requests
import re
import cv2
import os

"""
  手写文字识别WebAPI接口调用示例接口文档(必看):https://doc.xfyun.cn/rest_api/%E6%89%8B%E5%86%99%E6%96%87%E5%AD%97%E8%AF%86%E5%88%AB.html
  图片属性：jpg/png/bmp,最短边至少15px，最长边最大4096px,编码后大小不超过4M,识别文字语种：中英文
  webapi OCR服务参考帖子(必看)：http://bbs.xfyun.cn/forum.php?mod=viewthread&tid=39111&highlight=OCR
  (Very Important)创建完webapi应用添加服务之后一定要设置ip白名单，找到控制台--我的应用--设置ip白名单，如何设置参考：http://bbs.xfyun.cn/forum.php?mod=viewthread&tid=41891
  错误码链接：https://www.xfyun.cn/document/error-code (code返回错误码时必看)
  @author iflytek
"""
# OCR手写文字识别接口地址
URL = "http://webapi.xfyun.cn/v1/service/v1/ocr/handwriting"
# 应用APPID(必须为webapi类型应用,并开通手写文字识别服务,参考帖子如何创建一个webapi应用：http://bbs.xfyun.cn/forum.php?mod=viewthread&tid=36481)
APPID = "5f11123b"
# 接口密钥(webapi类型应用开通手写文字识别后，控制台--我的应用---手写文字识别---相应服务的apikey)
API_KEY = "2252342ffcdd901aeaa115d9e6c5e5ac"


def getHeader():
    curTime = str(int(time.time()))
    param = "{\"language\":\"" + language + "\",\"location\":\"" + location + "\"}"
    paramBase64 = base64.b64encode(param.encode('utf-8'))

    m2 = hashlib.md5()
    str1 = API_KEY + curTime + str(paramBase64, 'utf-8')
    m2.update(str1.encode('utf-8'))
    checkSum = m2.hexdigest()
    # 组装http请求头
    header = {
        'X-CurTime': curTime,
        'X-Param': paramBase64,
        'X-Appid': APPID,
        'X-CheckSum': checkSum,
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
    }
    return header


def getBody(filepath):
    with open(filepath, 'rb') as f:
        imgfile = f.read()
    data = {'image': str(base64.b64encode(imgfile), 'utf-8')}
    return data


# 语种设置
language = "en"
# 是否返回文本位置信息
location = "true"


def process(picFilePath, savePath):
    resName = picFilePath.split('/')[-1][:-4]
    # headers=getHeader(language, location)
    r = requests.post(URL, headers=getHeader(), data=getBody(picFilePath))
    line = r.content

    # 转换字典
    byteDic = eval(line)
    print(byteDic)
    lineList = byteDic["data"]["block"][0]["line"]
    # block的value是[]
    lines = []
    for line in lineList:
        # 每一行的信息
        words = line["word"]
        wordList = []
        for word in words:
            wordContent = word["content"]
            wordList.append(wordContent)
        lineContent = " ".join(wordList)
        print(lineContent)
        lines.append(lineContent)

    with open(savePath + "/" + resName + ".txt", "w") as res_w:
        for line in lines:
            if line[-1] != "\n":
                line = line + "\n"
            res_w.write(line)


def readImg(picFilePath):
    Img = cv2.imread(picFilePath, 0)
    cv2.imshow("handwriting", Img)
    cv2.waitKey(2000)
    cv2.destroyAllWindows()

def ocrFrom(dicName):
    cutImg_path = './slice/' + dicName
    for cutImgName in os.listdir(cutImg_path):
        print(cutImgName)
        picFilePath = cutImg_path + "/" + cutImgName
        savePath = "./result/" + dicName
        if not os.path.exists(savePath):
            os.mkdir(savePath)
        process(picFilePath, savePath)

if __name__ == '__main__':
    dicName = '工作票.'
    ocrFrom(dicName)

