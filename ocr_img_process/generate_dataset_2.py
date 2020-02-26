# 导入库
import pickle
import os
import random
from PIL import Image
import re

# 读取汉字索引对应关系字典
f=open('char_dict', 'rb')
char_dict=pickle.load(f)
f.close()

# 手写文字对应路径
hand_dir="../trn_imgs/"
# 手写数字对应路径
num_dir="../mnist/mnist_imgs/"

## 设定数据保存路径
#dir_rec = './dataset/recognition/'
#dir_det = './dataset/detection/'
dir_rec = './dataset_total/chinese_dataset/'
dir_det = './dataset_total/mlt_raw/'

# 待识别汉字
#hand_str=u"亚信科技中国有限公司通信人工智能实验室"  ## 字符串格式设定为Unicode，每个汉字或数字都占一个字符
#hand_str2=u"我的电话是:18706764872"

# 图像尺寸设置
img_width = 30
img_height = 30


## 获取图像
def getImg(char):
    if char in char_dict:
        img_dir = hand_dir + '%0.5d'%char_dict[char] + '/'
    elif char.isdigit():
        img_dir = num_dir + '%0.2d'%int(char) + '/'
    else :
        img_dir = None
    
    if img_dir != None :
        file_list = os.listdir(img_dir)
        idx = random.randint(0,len(file_list)-1)
        #print("len of file_list:",len(file_list))
        #print('img_idx:',idx)
        img = Image.open(img_dir+file_list[idx]).resize((img_width, img_height))
        return img
    else:
        return Image.new('RGB',(img_width,img_height),(255,255,255))

## 图像拼接
def pasteImg(hand_list):
    #hand_list=[ch for ch in hand_str]
    to_img = Image.new('RGB',(img_width*(len(hand_list)),img_height),(255,255,255)) #创建一个新图
    i = 0 # 定义当前行所含文字或数字的个数
    for char in hand_list:
        #print(char)
        from_img = getImg(char)
        to_img.paste(from_img,box=(i * img_width, 0))
        i += 1
    return to_img,i

## 获取文件中的文字，返回list形式
def getChars(file_path):
    f = open(file_path)
    hw_str = f.read().replace(' ','').replace('\n','') # 去掉空格和换行符
    return hw_str

## 得到坐标信息，以字符串形式返回
def getLocinfo(min_x,min_y,char_str):
    nums = len(char_str)
    x2 = min_x+nums*img_width
    y3 = min_y+img_height
    return str(min_x)+','+str(min_y)+','+str(x2)+','+str(min_y)+','+str(x2)+','+str(y3)+','+str(min_x)+','+str(y3)+','+'HW,'+char_str

## 根据文字内容生成图像数据集
def getDataset(file_dir):
    file_list = os.listdir(file_dir)
    ## 创建文件夹
    if not os.path.exists(dir_rec+'images/'):
        os.makedirs(dir_rec+'images/')
    if not os.path.exists(dir_det+'image/'):
        os.makedirs(dir_det+'image/')
    if not os.path.exists(dir_det+'label/'):
        os.makedirs(dir_det+'label/')

    file_rec = dir_rec + 'annotation.txt' # 识别环节结果文件
    f_rec = open(file_rec,'a')
    for file in file_list:
        print("file:",file)
        hw_str = getChars(file_dir+'/'+file)
        chars_len = len(list(hw_str))
        print("chars_len:",chars_len)
        start_idx = 0
        count = 1
        
        #file_rec = dir_rec + file[:-4] + '_labels.txt' # 识别环节结果文件
        #f_rec = open(file_rec,'a')
        # 判断当前剩余字数
        while chars_len > 10 :
            # 设定当前完整图片包含的行数
            for i in range(2,10):
                #print("i:",i)
                if chars_len < 10:
                    break
                to_img = Image.new('RGB',(img_width*13,(img_height)*i*2+img_height),(255,255,255)) #创建一个新图
                img_name_det = file[:-4]+'_'+str(count)+'.jpg' # 检测图片名称
                file_detect = dir_det + 'label/gt_'+file[:-4]+'_'+str(count)+'.txt' # 检测图片对应标签名称
                f_detect = open(file_detect,'a')
                
                # 设定每一行的数字
                for j in range(i):
                    if chars_len < 5 :
                        break
                    rand_len = random.randint(3,min(chars_len,10))+1
                    #print("rand_len:",rand_len)
                    chars = re.sub(r'[^\w\s]','',hw_str[start_idx:start_idx+rand_len])
                    #print(hw_str[start_idx:start_idx+rand_len])
                    #print(chars)
                    if chars == '' :
                        continue
                    from_img, nums = pasteImg(chars)
                    rand2 = random.randint(1,12-rand_len)
                    min_x = rand2 * img_width
                    min_y = 2*j*img_height+30
                    to_img.paste(from_img,(min_x, min_y)) #rand2 * img_width
                    img_name_rec = file[:-4]+'_'+str(count)+'_'+str(j)+'.jpg'
                    file_name_rec = dir_rec + 'images/'+img_name_rec
                    f_rec.write(img_name_rec+' '+ chars+'\n') #将文件名与内容存入文件中
                    from_img.save(file_name_rec)
                    ## 坐标
                    loc_info = getLocinfo(min_x, min_y,chars)
                    f_detect.write(loc_info+'\n')                    
                    start_idx += rand_len                    
                    chars_len -= rand_len
                    #print("chars_len:",chars_len)
                    
                to_img.save(dir_det+ 'image/'+img_name_det)
                count += 1
                f_detect.close()
    f_rec.close()



file_dir = './files/'
getDataset(file_dir)



