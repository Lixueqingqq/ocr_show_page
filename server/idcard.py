# -*- coding: utf-8 -*-
# ---
# @File: idcard.py.py
# @Author: Lixueqing
# @Time: 7月 25, 2022
# ---
import re

class idcard:
    """
    身份证结构化识别
    """

    def __init__(self, text_info):
        self.text_info = text_info
        self.res = {
            '姓名': '',
            '性别': '',
            '民族': '',
            '出生年月': '',
            '住址': '',
            '公民身份号码': ''
        }
        # self.anchor_0 = 0.26*text_info['h'] #姓名之上，
        # self.anchor_1 = 0.36*text_info['h'] #性别之上，
        # self.anchor_2 = 0.46*text_info['h'] #出生之上，
        # self.anchor_3 = 0.82*text_info['h'] #号码之上
        self.anchor_0 = text_info['h'] #姓名之上，
        self.anchor_1 = text_info['h'] #性别之上，
        self.anchor_2 = text_info['h'] #出生之上，
        self.anchor_3 = text_info['h'] #号码之上
        self.get_anchor()
        self.nationality = ['汉','壮','维吾尔','回','苗','满','彝','土家','藏','蒙古','布依',\
                            '侗','瑶','白','哈尼','朝鲜','黎','哈萨克','傣','傈僳','佤',\
                            '畲','高山','拉祜','水','东乡','纳西','景颇','柯尔克孜','土', \
                            '达斡尔','仫佬','羌','布朗','撒拉','毛南','仡佬','锡伯','阿昌',\
                            '普米','塔吉克','怒','乌孜别克','俄罗斯','鄂温克','德昂','保安',\
                            '裕固','京','塔塔尔','独龙','鄂伦春','赫哲','门巴','珞巴','基诺'\
                            ]

    def groupbox(self,text_list,c,r,type='0'):
        tbox = []
        if r == self.text_info['h']:
            type = '0'
        if type == '1': #地址特殊处理
            r = r - (self.text_info['text_img_pos'][c][3]-self.text_info['text_img_pos'][c][1])
        for i, t in enumerate(text_list):
            if (self.text_info['text_img_pos'][i+c][1] + self.text_info['text_img_pos'][i+c][3]) / 2 < r:
                tbox.append(t)
            else:
                c = i + c
                break
        return c, tbox

    def get_anchor(self):
        for i, t in enumerate(self.text_info['text']):
            if ('性别' in t or '男' in t or '女' in t) and self.anchor_0 == self.text_info['h']:
                self.anchor_0 = self.text_info['text_img_pos'][i][1]
            if '出生' in t and self.anchor_1 == self.text_info['h']:
                self.anchor_1 = self.text_info['text_img_pos'][i][1]
            if '住址' in t and self.anchor_2 == self.text_info['h']:
                self.anchor_2 = self.text_info['text_img_pos'][i][1]
            if ('公民' in t or '身份' in t) and self.anchor_3 == self.text_info['h']:
                self.anchor_3 = self.text_info['text_img_pos'][i][1]

    def parse_strcture(self):
        c = 0
        # 姓名
        c, tbox = self.groupbox(self.text_info['text'], c, self.anchor_0)
        txt = ''.join(tbox).replace(' ', '')
        res = re.findall("姓名[\u4e00-\u9fa5]{1,4}", txt)
        if len(res) > 0:
            self.res['姓名'] = res[0].replace('姓名', '')

        # 性别/民族
        c, tbox = self.groupbox(self.text_info['text'][c:], c, self.anchor_1)
        txt = ''.join(tbox).replace(' ', '')
        if '男' in txt:
            self.res['性别'] = '男'
        elif '女' in txt:
            self.res['性别'] = '女'

        res = re.findall(".*民族[\u4e00-\u9fa5]+", txt)
        if len(res) > 0:
            self.res['民族'] = res[0].split('民族')[-1]
        else:
            for zz in self.nationality:
                if zz in txt:
                    self.res['民族'] = zz

        # 出生年月
        c, tbox = self.groupbox(self.text_info['text'][c:], c, self.anchor_2)
        txt = ''.join(tbox).replace(' ', '')
        res = re.findall('\d*年\d*月\d*日', txt)
        if len(res) > 0:
            self.res['出生年月'] = res[0].replace('出生', '')
        # 地址
        c, tbox = self.groupbox(self.text_info['text'][c:], c, self.anchor_3,type='1')
        txt = ''.join(tbox).replace(' ', '')
        if '住址' in txt:
            self.res['住址'] = txt.replace('住址','')
        # 身份证号码
        txt = ''.join(self.text_info['text'][c:]).replace(' ', '')
        res = re.findall('号码\d*[X|x]', txt)
        res += re.findall('号码\d*', txt)
        res += re.findall('\d{16,18}', txt)
        if len(res) > 0:
            self.res['公民身份号码'] = res[0].replace('号码', '')

        return self.res


if __name__ == '__main__':
    from ocr_sdk.image_to_text.img2text import img2text
    temp_file_path = r'D:\tmp\ocr_sdk'
    imgpath = r'C:\Users\admin\Desktop\images (1).jpg'
    content_info, tab_info, boder_table_info = img2text(imgpath, temp_file_path, imi=0, Image_enhancement=False,
                                                     Image_direction=False, Image_deseal=False, \
                                                     Tab_detect=False, BorderlessTab_detect=False, \
                                                     Qrcode_detect=False, Clear_tmp=False, fan2jian=True)
    if content_info:
        IDparse = idcard(content_info)
        result = IDparse.parse_strcture()
        print(result)