# -*- coding: utf-8 -*-
# ---
# @File: busilicense.py
# @Author: Lixueqing
# @Time: 7月 25, 2022
# ---
import re
import numpy as np
import collections

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
    #     '组成形式': '',
    #     '实收资本': '',
    #     '核准日期': '',
    #     '税务登记号': ''
    # }
    self.key = ['名称', '类型', '住所', '主要经营场所', '经营场所', '营业场所', \
                '执行事务合伙人','法定代表人', '经营者','投资人','负责人',\
                '注册资本', '成员出资总额','注册日期','成立日期', \
                '合伙期限','营业期限', '经营范围','业务范围', '组成形式'\
                ]
    self.a_0, self.a_1, self.a_1r, self.a_2, self.type, self.info_sorted = self.get_anchor()

  def group_RowBox(self, boxid_list):
    texts = []
    pos = []
    line = [self.text_info['text_img_pos'][boxid_list[0]]]
    tt = [self.text_info['text'][boxid_list[0]]]
    for box_id in boxid_list[1:]:
      box = self.text_info['text_img_pos'][box_id]
      # 如果两行中心高低差低于行高的0.1倍，则认为是同一行
      if abs((box[1] + box[3]) / 2 - (line[-1][1] + line[-1][3]) / 2) < \
        min(box[3] - box[1], line[-1][3] - line[-1][1]) * 0.3 :
        line.append(box)
        tt.append(self.text_info['text'][box_id])
      else:
        xline = np.array([x[0] for x in line])
        sort_index = np.argsort(xline)
        texts.append(''.join([tt[i] for i in sort_index]))
        pos.append([line[sort_index[0]][0],line[sort_index[0]][1],line[sort_index[-1]][2],line[sort_index[-1]][3]])
        line = [box]
        tt = [self.text_info['text'][box_id]]
    if len(line) > 0:
      xline = np.array([x[0] for x in line])
      sort_index = np.argsort(xline)
      texts.append(''.join([tt[i] for i in sort_index]))
      pos.append([line[sort_index[0]][0], line[sort_index[0]][1], line[sort_index[-1]][2], line[sort_index[-1]][3]])
    return texts,pos

  def get_anchor(self):
    a_0 = []
    a_1 = []
    a_1r = []
    a_1_l = []
    a_1_r = []
    a_2 = []
    info_left = {}
    info_right = {}
    for i, t in enumerate(self.text_info['text']):
      if '营业执照' in t:
        a_0 = self.text_info['text_img_pos'][i]
      if '登记机关' in t:
        a_2 = self.text_info['text_img_pos'][i]
      if len(a_0) > 0 and len(a_2) > 0:
        break

    if len(a_0)==0 or len(a_2)==0:
      type = 2 #不支持的类型
      return a_0, a_1, a_1r, a_2, type, {}

    for i, t in enumerate(self.text_info['text']):
      box = self.text_info['text_img_pos'][i]
      if box[1]>a_0[3] and box[3]<a_2[1]:
        if box[0]<(a_0[0]+a_0[2])/2:
          a_1_l.append(i)
        else:
          a_1_r.append(i)
    if len(a_1_r) > 0:
      type = '1'  # 竖排一栏营业执照
      text_l,pos_l = self.group_RowBox(a_1_l)
      text_r,pos_r = self.group_RowBox(a_1_r)
      for i,t in enumerate(text_l):
        for k in self.key:
          if k in t:
            info_left[k] = pos_l[i]
            break
      for i,t in enumerate(text_r):
        for k in self.key:
          if k in t:
            info_right[k] = pos_r[i]
            type = '0'  # 横排两栏营业执照
            break
    else:
      type = '1'
      text_l,pos_l = self.group_RowBox(a_1_l)
      for i,t in enumerate(text_l):
        for k in self.key:
          if k in t:
            info_left[k] = pos_l[i]
            break

    kk = list(info_left.keys())
    xline = np.array([info_left[x][1] for x in kk])
    sort_index = np.argsort(xline)
    info_sorted = collections.OrderedDict()
    for ki in sort_index:
      info_sorted[kk[ki]] = {'location':info_left[kk[ki]],'words':''}
      a_1.append(info_left[kk[ki]])

    if type == '0':
      kk = list(info_right.keys())
      xline = np.array([info_right[x][1] for x in kk])
      sort_index = np.argsort(xline)
      for ki in sort_index:
        info_sorted[kk[ki]] = {'location': info_right[kk[ki]],'words':''}
        a_1r.append(info_right[kk[ki]])

    if len(info_sorted) == 0:
      type = '2'

    if len(a_1)==0 or (type == '0' and len(a_1r)==0):
      type = '2'

    return a_0, a_1, a_1r, a_2, type, info_sorted

  def get_vertical_info(self):
    txtb_bianhao = []
    txtb = []
    a_k = []
    for i,t in enumerate(self.text_info['text']):
      box = self.text_info['text_img_pos'][i]
      if box[1] > self.a_2[1] - 2 * (self.a_2[3] - self.a_2[1]): #去掉登记机关，登记机关的值可能会在登记机关之上，干扰到其它内容
        break
      if box[1] < self.a_1[0][1]:
        if '统一社会信用代码' in t or '注册号' in t:
          a_k = self.text_info['text_img_pos'][i]
        txtb_bianhao.append(i)
      if box[3] > self.a_1[0][1]:
        txtb.append(i)

    for id in txtb_bianhao:
      box = self.text_info['text_img_pos'][id]
      t = self.text_info['text'][id]
      if len(a_k) > 0:
        if ('编号' not in t) and \
          ((box[1] + box[3]) / 2 > a_k[1] and (box[1] + box[3]) / 2 < a_k[3]):
          res = re.findall('[0-9A-Za-z]{6,24}', t)
          if len(res) > 0:
            self.res['社会信用代码'] = res[0]
        else:
          res = re.findall('[0-9A-Za-z\(\)\-)]{6,24}', t)
          if len(res) > 0:
            self.res['编号'] = res[0]

    textlist,poslist = self.group_RowBox(txtb)
    ia = 1
    ki = 0
    sortkey = list(self.info_sorted.keys())
    self.a_1.append(self.a_2)
    achr = self.a_1[ia][1]+(self.a_1[ia][3]-self.a_1[ia][1])/5
    t_c = ''
    for i,tt in enumerate(textlist):
      if poslist[i][3]<achr:
        t_c = t_c + tt
      else:
        if sortkey[ki] in t_c:
          self.info_sorted[sortkey[ki]]["words"] = t_c.replace(sortkey[ki],'')
          ki += 1
          ia = min(ia+1,len(self.a_1)-1)
          achr = self.a_1[ia][1]+(self.a_1[ia][3]-self.a_1[ia][1])/5
          t_c = tt
    if len(t_c)>0:
      if sortkey[ki] in t_c:
        self.info_sorted[sortkey[ki]]["words"] = t_c.replace(sortkey[ki], '')
    return self.info_sorted


  def get_horizontal_info(self):
    txtb_bianhao = []
    txtb_left = []
    txtb_right = []
    a_k = []
    right_k = min([x[0] for x in self.a_1r])
    for i, t in enumerate(self.text_info['text']):
      box = self.text_info['text_img_pos'][i]
      if box[1] > self.a_2[1] - 2 * (self.a_2[3] - self.a_2[1]):
        break
      if box[3] < self.a_1[0][1]:
        if '统一社会信用代码' in t or '注册号' in t:
          a_k = self.text_info['text_img_pos'][i]
        txtb_bianhao.append(i)
      if box[3] > self.a_1[0][1] and box[0] < right_k:
        if box[2] >= self.a_1r[0][0] and len(self.text_info['text'][i])>0:
          if self.text_info['text'][i][-1] == '住':
            self.text_info['text'][i] = self.text_info['text'][i][:-1]
        txtb_left.append(i)
      if box[3] > self.a_1r[0][1] and box[0] >= right_k:
        txtb_right.append(i)

    for id in txtb_bianhao:
      box = self.text_info['text_img_pos'][id]
      t = self.text_info['text'][id]
      if len(a_k) > 0:
        if ('编号' not in t) and \
          (box[1] > a_k[3] or \
           ((box[1] + box[3]) / 2 > a_k[1] and (box[1] + box[3]) / 2 < a_k[3])):
          res = re.findall('[0-9A-Za-z]{6,24}', t)
          if len(res) > 0:
            self.res['社会信用代码'] = res[0]
        else:
          res = re.findall('[0-9A-Za-z\(\)\-)]{6,24}', t)
          if len(res) > 0:
            self.res['编号'] = res[0]

    textlist, poslist = self.group_RowBox(txtb_left)
    ia = 1
    ki = 0
    sortkey = list(self.info_sorted.keys())
    self.a_1.append(self.a_2)
    achr = self.a_1[ia][1]+(self.a_1[ia][3]-self.a_1[ia][1])/5
    t_c = ''
    for i, tt in enumerate(textlist):
      if poslist[i][3] < achr:
        t_c = t_c + tt
      else:
        if sortkey[ki] in t_c:
          self.info_sorted[sortkey[ki]]["words"] = t_c.replace(sortkey[ki], '')
          ki += 1
          ia = min(ia + 1, len(self.a_1) - 1)
          achr = self.a_1[ia][1]+(self.a_1[ia][3]-self.a_1[ia][1])/5
          t_c = tt
    if len(t_c) > 0:
      if sortkey[ki] in t_c:
        self.info_sorted[sortkey[ki]]["words"] = t_c.replace(sortkey[ki], '')
        ki += 1


    textlist,poslist = self.group_RowBox(txtb_right)
    ia = 1
    self.a_1r.append(self.a_2)
    achr = self.a_1r[ia]
    t_c = ''
    for i, tt in enumerate(textlist):
      if poslist[i][3] < achr[1]+(achr[3]-achr[1])/5:
        t_c = t_c + tt
      else:
        if sortkey[ki] in t_c:
          self.info_sorted[sortkey[ki]]["words"] = t_c.replace(sortkey[ki], '')
          ki += 1
          ia = min(ia + 1, len(self.a_1r) - 1)
          achr = self.a_1r[ia]
          t_c = tt
    if len(t_c) > 0:
      if sortkey[ki] in t_c:
        self.info_sorted[sortkey[ki]]["words"] = t_c.replace(sortkey[ki], '')

    return self.info_sorted



      # self.res['住所'] = ''.join(textlist[3:]).replace('住所', '')
      # res = re.search('[所]', self.res['住所'])
      # if res is not None and res.span()[-1] < 4:
      #   self.res['住所'] = self.res['住所'][res.span()[-1]:]


  def parse_strcture(self):
    if self.type == '0':
      self.info_sorted = self.get_horizontal_info()
    if self.type == '1':
      self.info_sorted = self.get_vertical_info()
    result = self.res
    if '名称' in self.info_sorted:
      result['名称'] = self.info_sorted['名称']["words"]
    if '类型' in self.info_sorted:
      result['类型'] = self.info_sorted['类型']["words"]
    if '住所' in self.info_sorted:
      result['住所'] = self.info_sorted['住所']["words"]
    if '主要经营场所' in self.info_sorted:
      result['住所'] = self.info_sorted['主要经营场所']["words"]
    if '营业场所' in self.info_sorted:
      result['住所'] = self.info_sorted['营业场所']["words"]
    if '经营场所' in self.info_sorted:
      result['住所'] = self.info_sorted['经营场所']["words"]
    if '法定代表人' in self.info_sorted:
      result['法定代表人'] = self.info_sorted['法定代表人']["words"]
    if '执行事务合伙人' in self.info_sorted:
      result['法定代表人'] = self.info_sorted['执行事务合伙人']["words"]
    if '经营者' in self.info_sorted:
      result['法定代表人'] = self.info_sorted['经营者']["words"]
    if '负责人' in self.info_sorted:
      result['法定代表人'] = self.info_sorted['负责人']["words"]
    if '投资人' in self.info_sorted:
      result['法定代表人'] = self.info_sorted['投资人']["words"]
    if '注册资本' in self.info_sorted:
      result['注册资本'] = self.info_sorted['注册资本']["words"]
    if '成员出资总额' in self.info_sorted:
      result['注册资本'] = self.info_sorted['成员出资总额']["words"]
    if '注册日期' in self.info_sorted:
      result['成立日期'] = self.info_sorted['注册日期']["words"]
    if '成立日期' in self.info_sorted:
      result['成立日期'] = self.info_sorted['成立日期']["words"]
    if '合伙期限' in self.info_sorted:
      result['有效日期至'] = self.info_sorted['合伙期限']["words"]
    if '营业期限' in self.info_sorted:
      result['有效日期至'] = self.info_sorted['营业期限']["words"]
    if '业务范围' in self.info_sorted:
      result['经营范围'] = self.info_sorted['业务范围']["words"]
    if '经营范围' in self.info_sorted:
      result['经营范围'] = self.info_sorted['经营范围']["words"]

    res = re.findall("\d*年\d*月\d*日", result['成立日期'])
    if len(res) > 0:
      result['成立日期'] = res[0]

    res = re.findall("\d*年\d*月\d*日至", result['有效日期至'])
    if len(res) > 0:
      result['有效日期至'] = result['有效日期至'].replace(res[0], '')
    return result


if __name__ == '__main__':
  import os
  from ocr_sdk.image_to_text.img2text import img2text

  temp_file_path = r'D:\tmp\ocr_sdk'
  imgpaths = r'C:\Users\admin\Desktop\apply_test\bls'
  for imgn in os.listdir(imgpaths):
    imgn='微信图片_20220801150308.jpg'
    #imgn='F718623161A741C287683480BFDD962B.png'
    #imgn='ebd0d8c1757a9c563baed8615c0b2a7d.jpg'
    #imgn='e9c4dec9d4104e60058f5338e2dc0e90.jpg'
    #imgn = '591eae156bc7a2502803dbde5034df1f.jpg'
    #imgn = '8c93c650719af8dec96da437a8aef015.png'
    #imgn='B4DD2ADE6CDD4496BAE2376954635CFD.png'
    #imgn='b58be676197a40cd6db55285ceda7bd8.png'
    imgpath = os.path.join(imgpaths, imgn)
    print('***:', imgn)
    content_info, tab_info, boder_table_info = img2text(imgpath, temp_file_path, imi=0, Image_enhancement=False,
                                                        Image_direction=False, Image_deseal=False, \
                                                        Tab_detect=False, BorderlessTab_detect=False, \
                                                        Qrcode_detect=False, Clear_tmp=False, fan2jian=True)
    if content_info:
      IDparse = BusiLicense(content_info)
      result = IDparse.parse_strcture()
      for kk in result:
        print(kk + ': ' + result[kk])
