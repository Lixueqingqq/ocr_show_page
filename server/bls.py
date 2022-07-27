# -*- coding: utf-8 -*-
# ---
# @File: busilicense.py
# @Author: Lixueqing
# @Time: 7月 25, 2022
# ---
import re
import numpy as np
class BusiLicense:
    """
    营业执照结构识别
    """
    def __init__(self, text_info):
        self.text_info = text_info
        self.res = {
            '编号': '',
            '社会信用代码': '',
            '名称': '',
            '类型': '',
            '法定代表人': '',
            '经营范围': '',
            '注册资本': '',
            '成立日期': '',
            '有效日期至': '',
            '住所': ''
        }
        self.a_0,self.a_1,self.a_2,self.type = self.get_anchor()

    def group_RowBox(self,boxid_list):
        texts = []
        line = [self.text_info['text_img_pos'][boxid_list[0]]]
        tt = [self.text_info['text'][boxid_list[0]]]
        for box_id in boxid_list[1:]:
            box = self.text_info['text_img_pos'][box_id]
            #如果两行中心高低差低于行高的0.1倍，则认为是同一行
            if abs((box[1]+box[3])/2-(line[-1][1]+line[-1][3])/2)<\
                    min(box[3]-box[1],line[-1][3]-line[-1][1])*0.3:
                line.append(box)
                tt.append(self.text_info['text'][box_id])
            else:
                xline = np.array([x[0] for x in line])
                sort_index = np.argsort(xline)
                texts.append(''.join([tt[i] for i in sort_index]))
                line = [box]
                tt = [self.text_info['text'][box_id]]
        if len(line)>0:
            xline = np.array([x[0] for x in line])
            sort_index = np.argsort(xline)
            texts.append(''.join([tt[i] for i in sort_index]))
        return texts

    def get_anchor(self):
        a_0 = []
        a_1 = []
        a_2 = []
        for i,t in enumerate(self.text_info['text']):
            if '副本' in t:
                a_0 = self.text_info['text_img_pos'][i]
                a_0[1] = a_0[1]-(a_0[3]-a_0[1])*0.2 #稍微向上拓宽一点阈值
            if '统一社会信用代码' in t or '注册号' in t:
                a_1 = self.text_info['text_img_pos'][i]
            if '登记机关' in t:
                a_2 = self.text_info['text_img_pos'][i]
            if len(a_0)>0 and len(a_1)>0 and len(a_2)>0:
                break
        if len(a_0)==0 or len(a_1)==0 or len(a_2)==0:
          type = '2'  #如果没有找到三个锚点就不解析
        else:
          if a_1[3]<a_0[1] and a_1[2]<a_0[0]:
            type = '0'   #横排两栏营业执照
          else:
            type = '1' #竖排一栏营业执照
        return a_0,a_1,a_2,type

    def get_vertical_info(self):
        txtb_bianhao = []
        txtb = []
        for i,t in enumerate(self.text_info['text']):
            box = self.text_info['text_img_pos'][i]
            if box[1] > self.a_2[1] - 2 * (self.a_2[3] - self.a_2[1]):
                break
            if box[1] >= self.a_0[1] and box[2] > self.a_0[0] and box[1]<self.a_1[3]:
                txtb_bianhao.append(i)
            if box[1] > self.a_1[3]:
                txtb.append(i)

        for id in txtb_bianhao:
            box = self.text_info['text_img_pos'][id]
            t = self.text_info['text'][id]
            if ('编号' not in t) and \
                     ((box[1]+box[3])/2>self.a_1[1] and(box[1]+box[3])/2<self.a_1[3]):
                res = re.findall('[0-9A-Za-z]{6,24}',t)
                if len(res)>0:
                    self.res['社会信用代码'] = res[0]
            else:
                res = re.findall('[0-9A-Za-z\(\)\-)]{6,24}',t)
                if len(res)>0:
                    self.res['编号'] = res[0]

        textlist = self.group_RowBox(txtb)
        if len(textlist) >= 8:
            if '名称' in textlist[0]:
                self.res['名称'] = textlist[0].replace('名称','')
            else:
                self.res['名称'] = ''
            if '类型' in textlist[1]:
                self.res['类型'] = textlist[1].replace('类型','')
            else:
                self.res['类型'] = ''
            if '住所' in textlist[2]:
                self.res['住所'] = textlist[2].replace('住所','')
            else:
                self.res['住所'] = ''
            if '法定代表人' in textlist[3]:
                self.res['法定代表人'] = textlist[3].replace('法定代表人','')
            else:
                self.res['法定代表人'] = ''
            if '注册资本' in textlist[4]:
                self.res['注册资本'] = textlist[4].replace('注册资本', '')
            else:
                self.res['注册资本'] = ''
            if '成立日期' in textlist[5]:
                res = re.findall("\d*年\d*月\d*日",textlist[5].replace('成立日期', ''))
                if len(res)>0:
                    self.res['成立日期'] = res[0]
                else:
                    self.res['成立日期'] = ''
            else:
                self.res['成立日期'] = ''
            if '营业期限' in textlist[6]:
                res = re.findall("\d*年\d*月\d*日至", textlist[6].replace('营业期限', ''))
                if len(res)>0:
                    self.res['有效日期至'] = textlist[6].replace('营业期限', '').replace(res[0], '')
                else:
                    self.res['有效日期至'] = textlist[6].replace('营业期限', '')
            else:
                self.res['有效日期至'] = ''
            self.res['经营范围'] = ''.join(textlist[7:]).replace('经营范围','')
        else:
            print('the business license information is incomplete')
        return self.res

    def get_horizontal_info(self):
        txtb_bianhao = []
        txtb_left = []
        txtb_right = []
        for i, t in enumerate(self.text_info['text']):
            if self.text_info['text_img_pos'][i][0] > self.a_0[0]:
                if '注册资本' in t:
                    self.a_0[2] = min(self.a_0[2],self.text_info['text_img_pos'][i][0])
                if '成立日期' in t:
                    self.a_0[2] = min(self.a_0[2],self.text_info['text_img_pos'][i][0])
                if '营业期限' in t:
                    self.a_0[2] = min(self.a_0[2],self.text_info['text_img_pos'][i][0])
                if '住' in t:
                    self.a_0[2] = min(self.a_0[2],self.text_info['text_img_pos'][i][0])
        for i,t in enumerate(self.text_info['text']):
            if i==0 and '编号' in t:
                res = re.findall('[0-9A-Za-z\(\)\-)]{6,24}', t)
                if len(res) > 0:
                    self.res['编号'] = res[0]
                continue
            box = self.text_info['text_img_pos'][i]
            if box[1] > self.a_2[1] - 2 * (self.a_2[3] - self.a_2[1]):
                break
            if box[3] < self.a_0[3] and box[2] < self.a_0[0]:
                txtb_bianhao.append(i)
            if box[1] > self.a_0[3] and box[0] < self.a_0[2]:
                if box[2]>self.a_0[2]:
                    if self.text_info['text'][i][-1] == '住':
                        self.text_info['text'][i] = self.text_info['text'][i][:-1]
                txtb_left.append(i)
            if box[1] > self.a_0[3] and box[0] >= self.a_0[2]:
                txtb_right.append(i)

        for id in txtb_bianhao:
            box = self.text_info['text_img_pos'][id]
            t = self.text_info['text'][id]
            if ('编号' not in t) and \
                    (box[1]>self.a_1[3] or \
                     ((box[1]+box[3])/2>self.a_1[1] and(box[1]+box[3])/2<self.a_1[3])):
                res = re.findall('[0-9A-Za-z]{6,24}',t)
                if len(res)>0:
                    self.res['社会信用代码'] = res[0]
            else:
                res = re.findall('[0-9A-Za-z\(\)\-)]{6,24}',t)
                if len(res)>0:
                    self.res['编号'] = res[0]

        textlist = self.group_RowBox(txtb_left)
        if len(textlist) >= 4:
            if '名称' in textlist[0]:
                self.res['名称'] = textlist[0].replace('名称','')
            else:
                self.res['名称'] = ''
            if '类型' in textlist[1]:
                self.res['类型'] = textlist[1].replace('类型','')
            else:
                self.res['类型'] = ''
            if '法定代表人' or '负责人' in textlist[2]:
                if '法定代表人' in textlist[2]:
                    self.res['法定代表人'] = textlist[2].replace('法定代表人','')
                if '负责人' in textlist[2]:
                    self.res['法定代表人'] = textlist[2].replace('负责人', '')
            else:
                self.res['法定代表人'] = ''
            self.res['经营范围'] = ''.join(textlist[3:]).replace('经营范围','')
        else:
            print('the business license information is incomplete')

        textlist = self.group_RowBox(txtb_right)
        if len(textlist) >= 4 and '注册资本' in textlist[0]:
            self.res['注册资本'] = textlist[0].replace('注册资本', '')
            if '成立日期' in textlist[1]:
                res = re.findall("\d*年\d*月\d*日",textlist[1].replace('成立日期', ''))
                if len(res)>0:
                    self.res['成立日期'] = res[0]
            else:
                self.res['成立日期'] = ''
            if '营业期限' in textlist[2]:
                res = re.findall("\d*年\d*月\d*日至", textlist[2].replace('营业期限', ''))
                if len(res)>0:
                    self.res['有效日期至'] = textlist[2].replace('营业期限', '').replace(res[0], '')
                else:
                    self.res['有效日期至'] = textlist[2].replace('营业期限', '')
            else:
                self.res['有效日期至'] = ''
            self.res['住所'] = ''.join(textlist[3:]).replace('住所', '')
            res = re.search('[所]',self.res['住所'])
            if res is not None and res.span()[-1]<4:
                self.res['住所'] = self.res['住所'][res.span()[-1]:]
        elif len(textlist) >= 3 and '成立日期' in textlist[0]:
            res = re.findall("\d*年\d*月\d*日",textlist[0].replace('成立日期', ''))
            if len(res)>0:
                self.res['成立日期'] = res[0]
            else:
                self.res['成立日期'] = ''
            if '营业期限' in textlist[1]:
                res = re.findall("\d*年\d*月\d*日至", textlist[1].replace('营业期限', ''))
                if len(res)>0:
                    self.res['有效日期至'] = textlist[1].replace('营业期限', '').replace(res[0], '')
                else:
                    self.res['有效日期至'] = textlist[1].replace('营业期限', '')
            else:
                self.res['有效日期至'] = ''
            self.res['住所'] = ''.join(textlist[2:]).replace('营业场所', '')
        else:
            print('the business license information is incomplete')

        return self.res

    def parse_strcture(self):
        result = self.res
        if self.type == '0':
            result = self.get_horizontal_info()
        if self.type == '1':
            result = self.get_vertical_info()
        return result


if __name__ == '__main__':
    import os
    from ocr_sdk.image_to_text.img2text import img2text
    temp_file_path = r'D:\tmp\ocr_sdk'
    imgpaths = r'C:\Users\admin\Desktop\apply_test\bls'
    for imgn in os.listdir(imgpaths):
        #imgn = 'license-1.7b8bebf8.jpg'
        #imgn = 'F718623161A741C287683480BFDD962B.png'
        #imgn = 'B4DD2ADE6CDD4496BAE2376954635CFD.png'
        imgpath = os.path.join(imgpaths,imgn)
        print('***:',imgn)
        content_info, tab_info, boder_table_info = img2text(imgpath, temp_file_path, imi=0, Image_enhancement=False,
                                                         Image_direction=False, Image_deseal=False, \
                                                         Tab_detect=False, BorderlessTab_detect=False, \
                                                         Qrcode_detect=False, Clear_tmp=False, fan2jian=True)
        if content_info:
            IDparse = BusiLicense(content_info)
            result = IDparse.parse_strcture()
            print(result)


