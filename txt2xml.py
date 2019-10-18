# -*- coding: utf8 -*-
from xml.etree import ElementTree as ET
from PIL import Image
import re

class VocWriter:
    def __init__(self, 
            databaseSrc,
            localImgPath,
            folderName, 
            fileName, 
            imgSize,
            boxList,
            objectName,
            saveXmlDir
             ):
        self.folderName = folderName
        self.fileName = fileName
        self.databaseSrc = databaseSrc
        self.imgSize = imgSize
        self.boxList = boxList
        self.localImgPath = localImgPath
        self.verified = False
        self.objectName = objectName
        self.saveXmlDir = saveXmlDir

    def genXML(self):
        # 定义xml文件的结构和各个元素的名称
        annotation = ET.Element('annotation')                    # annotation
        folder = ET.SubElement(annotation,'folder')              ## folder
        folder.text = self.folderName
        filename = ET.SubElement(annotation,'filename')          ## filename
        filename.text = self.fileName
        path = ET.SubElement(annotation,'path')                  ## path
        path.text = self.localImgPath
        source = ET.SubElement(annotation,'source')              ## source
        source_database = ET.SubElement(source,'database')       ### database
        source_database.text = self.databaseSrc
        size = ET.SubElement(annotation,'size')                  ## size
        size_width = ET.SubElement(size,'width')                 ### width
        size_width.text = self.imgSize[0]
        size_height = ET.SubElement(size,'height')               ### height
        size_height.text = self.imgSize[1]
        size_depth = ET.SubElement(size,'depth')                 ### depth
        size_depth.text = self.imgSize[2]
        segmented = ET.SubElement(annotation,'segmented')        ## segmented
        segmented.text = '0'
        ob = ET.SubElement(annotation, 'object')                 ## object
        ob_name = ET.SubElement(ob, 'name')                      ### name
        ob_name.text = self.objectName
        ob_pose = ET.SubElement(ob, 'pose')                      ### pose
        ob_pose.text = 'unspecified'
        ob_truncated = ET.SubElement(ob,'truncated')             ### truncated
        ob_truncated.text = '0'
        ob_difficult = ET.SubElement(ob, 'difficult')            ### difficult
        ob_difficult.text = '0'
        ob_bndbox = ET.SubElement(ob, 'bndbox')                  ### bndbox
        ob_bndbox_xmin = ET.SubElement(ob_bndbox, 'xmin')        #### xmin
        ob_bndbox_xmin.text = self.boxList[0]
        ob_bndbox_ymin = ET.SubElement(ob_bndbox, 'ymin')        #### ymin
        ob_bndbox_ymin.text = self.boxList[1]
        ob_bndbox_xmax = ET.SubElement(ob_bndbox, 'xmax')        #### xmax
        ob_bndbox_xmax.text = self.boxList[2]
        ob_bndbox_ymax = ET.SubElement(ob_bndbox, 'ymax')        #### ymax
        ob_bndbox_ymax.text = self.boxList[3]

        return annotation
    
    def saveXML(self,annotation):
        tree = ET.ElementTree(annotation)
        tree.write(self.saveXmlDir + self.fileName[:-4] + '.xml')



def txt2xml(img_dir, txt_path, save_xml_dir):
    txt_file = open(txt_path,'r').readlines() # 按行读取
    for i in range(2, len(txt_file)):
        read_line = re.sub(' +', ' ', txt_file[i])[:-1].split(' ')
        databaseSrc = 'celeba'
        localImgPath = img_dir + read_line[0]
        folderName = img_dir.split('/')[-2]
        fileName = read_line[0]
        img = Image.open(localImgPath)
        width, height = img.size
        imgSize = [str(width),str(height),str(3)]
        boxList = [read_line[1], \
                   read_line[2], \
                   str(int(read_line[1])+int(read_line[3])), \
                   str(int(read_line[2])+int(read_line[4]))]
        objectName = 'face'
        saveXmlDir = save_xml_dir
        voc_writer = VocWriter(databaseSrc,
                                localImgPath,
                                folderName, 
                                fileName, 
                                imgSize,
                                boxList,
                                objectName,
                                saveXmlDir)
        annotation = voc_writer.genXML()
        voc_writer.saveXML(annotation)



#### main ####
img_dir = 'C:/gzw_work/dataset/celebA/CelebA/Img/img_celeba.7z/img_celeba/img_celeba/'
txt_path = 'C:/gzw_work/dataset/celebA/CelebA/Anno/list_bbox_celeba.txt'
save_xml_dir = 'C:/gzw_work/dataset/celebA/CelebA/xml/'
txt2xml(img_dir, txt_path, save_xml_dir)




