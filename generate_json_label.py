#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   generate_json_label.py
@Time    :   2019/07/02 11:37:39
@Author  :   guo.zhiwei 
@Version :   1.0
@Desc    :   根据图片名称提取有效的部分生成json文件，作为模型训练的label
'''

####################功能场景描述######################
## 图片名称示例：
# 0197-3_16-277&467_471&552-471&552_294&541_277&467_454&478-0_0_8_31_31_32_9-106-16.jpg

## 文件名由7个字段构成(用-分开)，各个字段的含义如下：
# 第1个字段：面积(025)：车牌面积与整个图片面积之比
# 第2个字段：倾斜度(95_113)：水平倾斜度和垂直倾斜度
# 第3个字段：边框坐标(154&383_386&473)：左下顶点和右下顶点的坐标
# 第4个字段：四个顶点坐标(386&473_177&454_154&383_363&402)：
#           整幅图像中车牌四个顶点的精确(x，y),这些坐标从右下顶点开始，顺时针旋转。
# 第5个字段：车牌号：CCPD中每个图片有一个车牌
#           每个车牌号由一个汉字(provinces数组)、一个字母(alphabets数组)
#			和五个字母或数字(ads数组)组成。
#			"0_0_22_27_27_33_16"是上面字符数组的索引。
# 第6个字段：亮度(37)：车牌区域的亮度
# 第7个字段：模糊度(15)：车牌区域的模糊度


# here put the import lib


##################生成json文件脚本####################
import json
import os
import argparse
from PIL import Image

# 函数定义

# 写数据到json文件
def WriteLabel2File(fileName, listLabel):
    try:
        with open(fileName, 'w') as fp:   # a是追加方式写入
            strJson = json.dumps(listLabel, indent=4) # ,separators=(',', ': ')
            fp.write(strJson)
            fp.close()
        #return 0, ""
    except Exception as e:
        print("文件读取错误，pass...")
        pass

# 得到指定路径下的所有jpg文件，返回list形式
def GetFileList(path):
    fileList = []
    files = os.listdir(path)
    for f in files:
        str = f[-3:]
        if f[-3:] == "jpg":
            fileList.append(f)
    return fileList

# 得到指定路径下的所有的文件夹，返回list形式
def GetFolderList(path):
    folderList = []
    files = os.listdir(path)
    for f in files:
        if f[-5:]!='.json':
            folderList.append(f)
    return folderList

# 根据图片名称解析出车牌的位置坐标信息
def GetPointsList(str):
    strList = str.replace('.jpg','').split('-')[3].split("_")
    xList = []
    yList = []
    for i in range(4):
        xy = strList[i].split('&')
        xList.append(int(xy[0]))
        yList.append(int(xy[1]))
    return xList, yList

# 获取图片大小height,weight
def GetImgSize(path):
    img = Image.open(path)
    width, height = img.size
    return width,height

###########################################################
# 执行
print("start")

parser = argparse.ArgumentParser(description='manual to this script')
parser.add_argument('--file_path', type=str)
args = parser.parse_args()

file_path = args.file_path
label_file_name = file_path + '/label_new.json'

#file_list = GetFileList(file_path)
write_dict = {} # 待写入的内容

#import pdb
print("......")
#pdb.set_trace()

index = 0
for folder in GetFolderList(file_path):
    print(file_path+'/'+folder)
    #pdb.set_trace()
    for f in GetFileList(file_path+'/'+folder):
        img = Image.open(file_path+'/'+folder+'/'+f)
        width,height = img.size
        file_name = folder + '/' + f
        x,y = GetPointsList(f)
        write_dict[str(index)] = {"filename":file_name,"file_attributes":{"height":height,"width":width}, "regions":{"0":{"shape_attributes": \
                                  {"name":"polygon", "all_points_x":x, "all_points_y":y},\
                                    "region_attributes":{"name":"LicensePlate"}}}}
        index += 1

    #pdb.set_trace()
#pdb.set_trace()
WriteLabel2File(label_file_name, write_dict)

print("process ", index, "个图片")
