
#### MRO数据xml文件指定内容解析
##   gz : 待提取的xml文件名称
def mro_extract(gz):
	## 导入库
	import os,gzip,io
	import xml.etree.cElementTree as ET

	file_io = io.StringIO()
	xm = gzip.open(gz,'rb')
	print("已读入：%s.\n解析中：" % (os.path.abspath(gz)))	
	
	str_s = '' # 存储xml文件中提取的指定内容
	d_obj = {} # 存储object中的内容为字典形式
	i = 0 # 计数值初始化
	object_flag = False ## object标志
	nc_rspr_max = 0 ##记录最强邻区的电平
	list_rspr = [] ## 存储邻区电平值
	list_str = [] ## 存储字符串
	for event,elem in ET.iterparse(xm,events=('start','end')):
		if event == 'end' and elem.tag == 'object' and object_flag == True :  ## 当前object有效数据读取解析完，保存最强邻区对应的数据
			v_max_idx = [m for m,x in enumerate(list_rspr) if x == max(list_rspr)]
			for idx in range(len(v_max_idx)):
				file_io.write(list_str[v_max_idx[idx]]) ## 保存最强邻区对应的相关记录
			object_flag = False
			list_rspr = []
			list_str = []
		if i >= 2:
			object_flag = False
			break		
		elif event == 'start':			
			if elem.tag == 'object':
				object_flag = False
				d_obj = elem.attrib
		elif event == 'end' and elem.tag == 'smr':
			object_flag = False
			i += 1		
		elif elem.tag == 'v' and event == 'end':
			object_flag = True 
			if elem.text.split()[0] != 'NIL' and elem.text.split()[1] != 'NIL' : ## 判断主小区和邻小区电平是否为空
				smr = elem.text.split() #smr[0,1,6,7]分别代表LteScRSRP， LteNcRSRP， LteNcEarfcn， LteNcPci
				list_rspr.append(smr[1]) ##保存邻区电平值，用于后续进行比较
				str_tmp = str(d_obj['TimeStamp'])[0:10]+' '+str(d_obj['id'])[0:10]+' '+smr[0]+' '+smr[1]+' '+smr[6]+' '+smr[7]+'\r\n'
				list_str.append(str_tmp)			    
			
	elem.clear()
	str_s = file_io.getvalue().replace(' ',',')	#写入解析后内容
	xm.close()
	file_io.close()
	return str_s
	

#### MRE数据xml文件指定内容解析
##   gz : 待提取的xml文件名称
def mre_extract(gz):
    ## 导入库
	import os,gzip,io
	import xml.etree.cElementTree as ET

	file_io = io.StringIO() 
	xm = gzip.open(gz,'rb')
	print("已读入：%s.\n解析中：" % (os.path.abspath(gz)))	
	
	str_s = '' # 存储xml文件中提取的指定内容
	d_obj = {} # 存储object中的内容为字典形式
	i = 0 # 计数值初始化
	
	for event,elem in ET.iterparse(xm,events=('start','end')):
		if i >= 2:
			break		
		elif event == 'start':
			if elem.tag == 'object':
				d_obj = elem.attrib
		elif event == 'end' and elem.tag == 'smr':
			i += 1
		elif event == 'end' and elem.tag == 'v':
			smr = elem.text.split() #smr[0,1,6,7]分别代表LteScRSRP， LteNcRSRP， LteNcEarfcn， LteNcPci
			if smr[1] != 'NIL':
			    file_io.write(str(d_obj['TimeStamp'])[0:10]+' '+d_obj['EventType']+' ' \
						  +str(d_obj['id'])+' '+smr[0]+' '+smr[1]+' '+smr[6]+' '+smr[7]+'\r\n')
			
	elem.clear()
	str_s = file_io.getvalue().replace(' \n','\r\n').replace(' ',',')	# 写入解析后内容
	xm.close()
	file_io.close()
	return str_s
	

#### 保存提取后的数据为csv格式
##   csv_file_name : 保存的文件名称
##   str_s : 待保存的数据
def save_data_to_csv(csv_file_name,str_s):
	## 导入库
	import os,gzip,io
	
	output = io.StringIO()
	output.write(str_s)
	with open(csv_file_name,'w') as t:		#生成csv文件以写入数据
	    t.write(output.getvalue())	#写入解析后内容
	output.close()
	

####  统计处理MRO数据
import pandas as pd 
import time

## 文件名称定义
mro_file_name = 'TD-LTE_MRO_HUAWEI_010217007005_178452_20190505000000.xml.gz' ## 待处理的mro文件
mro_data_name = 'mro_data.csv'  ## mr0文件解析后保存的文件名称
mro_result_name = 'mro_result.csv'  ## mr0统计结果文件名称

## MRO数据对应列名定义
columns_mro_1 = ['date','id','LteScRSRP','LteNcRSRP','LteNcEarfcn','LteNcPci'] ## 第一阶段数据对应的列名，即从原始的xml中提取的数据
columns_mro_2 = ['date','id','LteNcEarfcn','LteNcPci','LteScRSRP','Sc_Nc_RSPR','COUNT'] ## 第二阶段数据对应的列名，即统计处理完后要保存的统计结果数据

## 第一阶段：解析xml文件，并将所提取的数据保存为csv格式
start_time = time.time()
str_s = mro_extract(mro_file_name) ## 解析并提取所需字段的数据
save_data_to_csv(mro_data_name,str_s) ## 保存提取结果
end_time = time.time()
process_time_1 = end_time - start_time
print("第一阶段完毕")
print("处理时间：", process_time_1)

## 第二阶段：统计mro数据的电平差
start_time = time.time()
df_1 = pd.read_csv(mro_data_name)
df_1.columns = columns_mro_1
df_1['Sc_Nc_RSPR'] = df_1['LteScRSRP'].map(int) - df_1['LteNcRSRP'].map(int) #求出主小区和邻区的电平差
#print(df_1.head(5))
df_1.loc[df_1['LteScRSRP']>65,'LteScRSRP'] =  100 # 'more_65'
df_1.loc[df_1['Sc_Nc_RSPR']>6,'Sc_Nc_RSPR'] = 10   # 'more_6'
#print(df_1.head(5))
#print(df_1.columns)
df_2 = df_1.groupby([df_1['date'],df_1['id'],df_1['LteNcEarfcn'],df_1['LteNcPci'],df_1['LteScRSRP'],df_1['Sc_Nc_RSPR']]).count()
df_2 = df_2.reset_index()
#print(df_2.head(5))
df_2.rename(columns={'LteNcRSRP':'COUNT'}, inplace = True)
df_2 = df_2[columns_mro_2]
#print(df_2.head(5))
end_time = time.time()
process_time_2 = end_time - start_time
print("第二阶段完毕")
print("处理时间：", process_time_2)
print("总处理时间：", process_time_1+process_time_2)

## 保存统计结果
df_2.to_csv(mro_result_name)


####  统计处理MRE数据
import pandas as pd 
import time

## 文件名称定义
mre_file_name = 'TD-LTE_MRE_HUAWEI_100092251069_652803_20190424100000.xml.gz' ## 待处理的mre文件
mre_data_name = 'mre_data.csv'  ## mre文件解析后保存的文件名称
mre_result_name = 'mre_result.csv'  ## mre统计结果文件名称
## MRO数据对应列名定义
columns_mre_1 = ['date','EventType','id','LteScRSRP','LteNcRSRP','LteNcEarfcn','LteNcPci'] ## 第一阶段数据对应的列名
columns_mre_2 = ['date','id','LteNcEarfcn','LteNcPci','LteScRSRP','Sc_Nc_RSPR','EventType','COUNT'] ## 第二阶段数据对应的列名

## 第一阶段：解析xml文件，并将所提取的数据保存为csv格式
start_time = time.time()
str_s = mre_extract(mre_file_name) ## 解析并提取所需字段的数据
save_data_to_csv(mre_data_name,str_s) ## 保存提取结果
end_time = time.time()
process_time_1 = end_time - start_time
print("第一阶段完毕")
print("处理时间：", process_time_1)

## 第二阶段：统计mro数据的电平差
start_time = time.time()
df_1 = pd.read_csv(mre_data_name)
df_1.columns = columns_mre_1
df_1['Sc_Nc_RSPR'] = df_1['LteScRSRP'].map(int) - df_1['LteNcRSRP'].map(int) #求出主小区和邻区的电平差
#print(df_1.head(5))
df_1.loc[df_1['LteScRSRP']>65,'LteScRSRP'] =  100 # 'more_65'
df_1.loc[df_1['Sc_Nc_RSPR']>6,'Sc_Nc_RSPR'] = 10   # 'more_6'
#print(df_1.head(5))
#print(df_1.columns)
df_2 = df_1.groupby([df_1['date'],df_1['id'],df_1['LteNcEarfcn'],df_1['LteNcPci'],df_1['LteScRSRP'],df_1['Sc_Nc_RSPR'],df_1['EventType']]).count()
df_2 = df_2.reset_index()
#print(df_2.head(5))
df_2.rename(columns={'LteNcRSRP':'COUNT'}, inplace = True)
df_2 = df_2[columns_mre_2]
#print(df_2.head(5))
end_time = time.time()
process_time_2 = end_time - start_time
print("第二阶段完毕")
print("处理时间：", process_time_2)
print("总处理时间：", process_time_1+process_time_2)

## 保存统计结果
df_2.to_csv(mre_result_name)
