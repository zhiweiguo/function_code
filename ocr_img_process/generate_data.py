# -*- encoding: utf-8 -*-
#### 该文件主要包括两个功能：
#### 1. 读取百度在线文字识别得到的json格式结果，提取坐标信息和识别到的文字信息，
####    然后根据坐标信息截取每一个片段的图片，并保存图片名称和文字到TXT中
#### 2. 读取截取到的每张图片，随机组合，生成一张大图（即类似于合同图片的一页）

## 导入库
import json
import os
from PIL import Image
import pdb
import time
import random

## 路径设置
bg_img_dir = './bg_imgs/'                   # 背景图片的路径
img_dir = './img_json_files/imgs/'          # 原始的图片路径
json_dir = './img_json_files/json/'         # 原始图片对应的百度检测结果json文件路径
rec_dir = './dataset_1015/chinese_dataset/' # 生成的识别数据集保存路径
det_dir = './dataset_ctpn/mlt_raw/'         # 生成的检测数据集保存路径

## 图像尺寸设置
img_width = 2400
img_height = 1000   # 3500

#if not os.path.exists(rec_dir):
#    os.makedirs(rec_dir+'images/')
#if not os.path.exists(det_dir):
#    os.makedirs(det_dir+'label/')  
#    os.makedirs(det_dir+'image/')

## 处理json文件，提取坐标信息裁剪图片进行保存，同时保存标签文本信息到TXT中
def resolveJson(img_path, json_path):
    f_annotation = open(rec_dir+'annotation.txt', 'a') # 识别数据集标签文件
#    pdb.set_trace()
    img_name = img_path.split('/')[-1][:-4] # 截取实际的图片名称
    img = Image.open(img_path)
    f = open(json_path, 'r')
    f_json = json.load(f)
    res_list = f_json['words_result'] # 得到一个list，长度即为检测到的片段个数
    idx = 1
    for res in res_list:
        left = res['location']['left']
        upper = res['location']['top']
        right = left + res['location']['width']
        lower = upper + res['location']['height']
        crop_img = img.crop((left, upper, right, lower))  # (left, upper, right, lower)
        save_img_path = rec_dir+'images/'+img_name+'_'+str(idx)+'.jpg'
        crop_img.save(save_img_path)
        f_annotation.write(save_img_path.split('/')[-1] + ' ' + res['words'] + '\n')
        idx += 1
    
    f_annotation.close()

## 生成识别数据集
def getRecDataset():
    ## 创建文件夹
    if not os.path.exists(rec_dir):
        os.makedirs(rec_dir+'images/')
    img_name_list = os.listdir(img_dir)
    for img_name in img_name_list:
        img_path = img_dir + img_name
        json_path = json_dir + img_name[:-4] + '.json'
        resolveJson(img_path, json_path) 

## 生成检测数据集
def getDetDataset(data_num):
    ## 创建文件夹
    if not os.path.exists(det_dir):
        os.makedirs(det_dir+'label/')
        os.makedirs(det_dir+'image/')
    
    ## 背景图
    bg_img_list = os.listdir(bg_img_dir)
    bg_img_num = len(bg_img_list)

    rec_imgs_list = open(rec_dir + 'annotation.txt', 'r').readlines()
    img_num = len(rec_imgs_list) # 识别数据集图片个数
    ## 根据要求的数据量创建检测数据集
    for i in range(0,data_num):
        ##to_img = Image.new('RGB',(img_width,img_height),(255,255,255)) #创建一个空白图
        ##to_img = Image.new('RGB',(img_width,img_height),(random.randint(180,255),random.randint(180,255),random.randint(180,255))) #创建一个空白图
        to_img = Image.open(bg_img_dir+bg_img_list[random.randint(0,bg_img_num-1)]).resize((img_width,img_height))
        #det_img_name = time.strftime('%y_%m_%d_%H_%M_%S', time.localtime(time.time())) # 不可行，因为处理时间太
        det_img_name = str(int(time.time()*10000000))
        det_img_path = det_dir + 'image/' + det_img_name + '.jpg' # 检测图片名称
        det_label_path = det_dir + 'label/gt_' + det_img_name + '.txt' # 检测图片对应标签文本
        det_label_file = open(det_label_path, 'a')
        start_height_idx = 300 # 每张图片从height=300处开始放置文字
#        pdb.set_trace()
        while start_height_idx < img_height:
            from_img_info = rec_imgs_list[random.randint(0,img_num-1)]
            from_img_name = from_img_info[0:from_img_info.index(' ')] # 图片名称,空格前内容
            from_img_txt = from_img_info[(from_img_info.index(' ')+1):-1] # 图片内容，空格后内容
            from_img = Image.open(rec_dir + 'images/' + from_img_name)
            w, h = from_img.size  # 获取图像宽高
            if start_height_idx+h > img_height-300 :
                break
            width_sub = img_width - 600 - w   # 左右两边需要空出各300像素宽度
            if width_sub > 0 :
                rand_move = random.randint(0,width_sub)
            else :
                continue
           
            # 图片paste
            min_x = 300 + rand_move
            min_y = start_height_idx
            to_img.paste(from_img,(min_x, min_y))
            # 计算坐标，并写入txt
            x2 = min_x + w
            y3 = min_y + h
            txt = str(min_x)+','+str(min_y)+',' \
                  +str(x2)+','+str(min_y)+',' \
                  +str(x2)+','+str(y3)+',' \
                  +str(min_x)+','+str(y3)+',' \
                  +'None,' +from_img_txt
            print(txt)
            det_label_file.write(txt)
            det_label_file.write('\n')
            # 更新索引
            start_height_idx += (h+40)
        to_img.save(det_img_path)
        det_label_file.close()

#### 主程序入口 ####
def main():
    ## 得到识别数据集
    ## getRecDataset()

    ## 得到检测数据集
    data_num = 20000  ## 检测数据集数量
    getDetDataset(data_num)



#### start ####
main()


