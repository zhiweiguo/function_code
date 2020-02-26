# encoding:utf-8
# aip安装方式为pip install baidu-aip
from aip import AipOcr
import json
import os
import cv2
import time
import sys

""" 你的 APPID AK SK """
APP_ID = '18405471'
API_KEY = '4PqGGzOdH7W4KpBpwF0IoyKG'
SECRET_KEY = 'uOnKBuOUF1z3GuMS0GgAQ92WGGG7MjVx'

""" 另一个id """
#APP_ID = '18410135'
#API_KEY = 'KigWbQ10YwVYGZTZrGxnSPnv'
#SECRET_KEY = 'yMTEGmFcMaUQHsFoFMVFKGIXGfukuCyk'

client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

#### 待识别图片路径 ####
# image_dir = './HW_test/det/labels_05_156.jpg'


""" 可选参数(部分接口可以设置) """
#options = {}
#options["recognize_granularity"] = "big" # 默认为big,不定位单字符位置;small为定位单字符位置

#### 功能模块定义 ####
""" 读取图片 """
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

""" 带参数调用手写文字识别 """
def get_handwrite_result(image_dir):
    image = get_file_content(image_dir)
    """ 可选参数 """
    options = {}
    options["recognize_granularity"] = "big" # 默认为big,不定位单字符位置;small为定位单字符位置   
    result = client.handwriting(image, options) # 结果是字典类型
    return result

""" 调用通用文字识别（含位置高精度版） """
def get_accurate_result(image_dir):
    image = get_file_content(image_dir)
    """ 可选参数 """
    options = {}
    options["recognize_granularity"] = "small"
    options["detect_direction"] = "false" # false(默认):不检测图像朝向; true: 检测朝向(正常方向 逆时针旋转90/180/270度) 
    options["vertexes_location"] = "false" # false(默认), 是否返回文字外接多边形顶点位置,不支持单字位置
    options["probability"] = "true" # 是否返回每一行识别结果的置信度
    result = client.accurate(image, options) # 结果是字典类型
    return result

""" 调用通用文字识别（含位置版） """
def get_general_result(image_dir):
    #client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    image = get_file_content(image_dir)
    """ 可选参数 """
    options = {}
    options["recognize_granularity"] = "small"
    options["detect_direction"] = "false" # false(默认):不检测图像朝向; true: 检测朝向(正常方向 逆时针旋转90/180/270度) 
    options["vertexes_location"] = "false" # false(默认), 是否返回文字外接多边形顶点位置,不支持单字位置
    options["probability"] = "true" # 是否返回每一行识别结果的置信度
    result = client.generalUrl(image, options) # 结果是字典类型
    return result

''' 保存百度api识别的结果为json文件 '''
def save_to_json(file_path, result):
    try:
        with open(file_path, 'w', encoding='utf-8') as fp:
            str_json = json.dumps(result, indent=4)
            fp.write(str_json)
            fp.close()
    except Exception as e:
        print('{}读取错误, pass...'.format(file_path))
        pass

''' 保存百度api识别的结果为TXT文件 '''
def save_to_txt(out_path, result):
    # out_path: 提取出的内容保存txt文件
    # result: 百度api识别的结果
    # 功能描述：
    # 直接根据百度识别的结果提取出坐标信息、文本内容信息，保存为TXT格式
    # txt文件的内容格式为：左上x,左上y,右上x,右上y,右下x,右下y,左下x,左下y,None,文本内容
    # 多行内容时每行都为此格式
    res_list = result['words_result'] # 得到一个list，长度即为检测到的片段个数
    out_file = open(out_path, 'w')
    for res in res_list:
        left = res['location']['left']
        upper = res['location']['top']
        right = left + res['location']['width']
        lower = upper + res['location']['height']
        write_txt = str(left) + ',' + str(upper) + ',' \
                  + str(right) + ',' + str(upper) + ',' \
                  + str(right) + ',' + str(lower) + ',' \
                  + str(left) + ',' + str(lower) + ',' \
                  + 'None' + ',' + res['words']
        out_file.write(write_txt)
        out_file.write('\n')
    out_file.close()

''' 提取百度识别结果json文件中的各个文本区域的坐标及文本内容,保存为txt '''
def extract_json(json_path, out_dir):
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    _, base_name = os.path.split(json_path)
    stem, ext = os.path.splitext(base_name)
    out_txt_name = stem + '.txt'
    out_file = open(os.path.join(out_dir, out_txt_name), 'w')
    f = open(json_path, 'r')
    f_json = json.load(f)
    res_list = f_json['words_result'] # 得到一个list，长度即为检测到的片段个数
    idx = 1
    for res in res_list:
        left = res['location']['left']
        upper = res['location']['top']
        right = left + res['location']['width']
        lower = upper + res['location']['height']
        # crop_img = img.crop((left, upper, right, lower))  # (left, upper, right, lower)
        # save_img_path = rec_dir+'images/'+img_name+'_'+str(idx)+'.jpg'
        # crop_img.save(save_img_path)
        # f_annotation.write(save_img_path.split('/')[-1] + ' ' + res['words'] + '\n')
        write_txt = str(left) + ',' + str(upper) + ',' \
                  + str(right) + ',' + str(upper) + ',' \
                  + str(right) + ',' + str(lower) + ',' \
                  + str(left) + ',' + str(lower) + ',' \
                  + 'None' + ',' + res['words'] 
        out_file.write(write_txt)
        out_file.write('\n') 
        idx += 1
    out_file.close()
    
''' 利用百度api识别图片，将识别结果保存为json文件'''
def baidu_ocr_process():
    count = int(sys.argv[1])
    img_dir = './zhengjian/image/'
    out_json_dir = './zhengjian/json/'
    while count < 283:
        img_name = str(count)+'.jpg'
        img_path = os.path.join(img_dir, img_name)
        result = get_accurate_result(img_path)
        #result = get_general_result(img_path)
        #stem, ext = os.path.splitext(img_name) # 分离文件名称和后缀
        json_path = os.path.join(out_json_dir, str(count)+'.json') 
        save_to_json(json_path, result)
        print(result)
        print('处理完成{}图片......'.format(img_path))
        count += 1
        time.sleep(2)
        
    '''
    img_dir = '/home/aim/WorkSpace/dataset/OCR/zhengjian/'
    out_dir = './zhengjian/'
    out_img_dir = 'image'
    out_json_dir = 'json'
    if not os.path.exists(os.path.join(out_dir, out_img_dir)):
        os.makedirs(os.path.join(out_dir, out_img_dir))
    if not os.path.exists(os.path.join(out_dir, out_json_dir)):
        os.makedirs(os.path.join(out_dir, out_json_dir))

    count = 1
    import pdb
    # pdb.set_trace()
    # tmp = get_accurate_result('./HW_test/det/labels_05_156.jpg')

    for f in os.listdir(img_dir):
        for i in os.listdir(os.path.join(img_dir, f)):
            # pdb.set_trace()
            img_path = os.path.join(img_dir, f, i)
            if not os.path.exists(img_path):
                print('图片不存在...')
                continue
            # 读取图片，并保存
            img = cv2.imread(img_path, cv2.IMREAD_COLOR)
            # cv2.imwrite(os.path.join(out_dir, out_img_dir, str(count)+'.jpg'), img)
            # 获取识别结果，并保存
            # result = get_accurate_result(img_path)
            result = get_general_result(img_path)
            json_path = os.path.join(out_dir, out_json_dir, str(count)+'.json') 
            save_to_json(json_path, result)
            print('处理完成{}张图片......'.format(count))
            count += 1
            #time.sleep(2)

    print('running end ...')
    '''

'''  '''


''' 提取json文件信息，转换为txt格式 '''
def extract_json_all():
    out_dir = './zhengjian/label/'
    json_dir = './zhengjian/json/'
    count = 1
    for f in os.listdir(json_dir):
        json_path = os.path.join(json_dir, f)
        print('开始处理{}文件'.format(json_path))
        extract_json(json_path, out_dir)
        print('当前处理完成,共完成{}个'.format(count))
        count += 1

if __name__ == "__main__":
    #baidu_ocr_process()
    #extract_json_all()




