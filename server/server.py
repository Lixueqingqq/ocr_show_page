from flask import Flask, jsonify, request, send_file, render_template
# from werkzeug.utils import secure_filename
from util import dict2xls, secure_filename,MyEncoder
from flask_cors import CORS
import time
import os
from ocr_sdk.files2image.file2img import file2img, tif2jpgs
from ocr_sdk.image_to_text.img2text import img2text
from ocr_sdk import face_detect
import urllib
import shutil
from idcard import idcard,idcard_b
from bls import BusiLicense
import json

FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'files')
os.makedirs(FILE_PATH, exist_ok=True)
GOOD_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "good_case")
os.makedirs(GOOD_PATH, exist_ok=True)
BAD_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bad_case")
os.makedirs(BAD_PATH, exist_ok=True)
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'),
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dist'))
# app.config["JSON_AS_ASCII"]=False
CORS(app, supports_credetials=True)


@app.route('/api/upload', methods=['POST'])
def upload():
  file = request.files['file']
  uni_id = str(time.time())
  temp_file_path = os.path.join(FILE_PATH, uni_id)
  if not os.path.exists(temp_file_path):
    os.makedirs(temp_file_path)
  aa = urllib.parse.urlparse(request.url)
  org_file_path = os.path.join(temp_file_path, 'orgfile')
  if not os.path.exists(org_file_path):
    os.makedirs(org_file_path)

  process_path = os.path.join(temp_file_path, 'process')
  if not os.path.exists(process_path):
    os.makedirs(process_path)

  filename = secure_filename(file.filename)
  # print('fiiii:',filename)
  file.save(os.path.join(org_file_path, filename))
  if filename.endswith('.pdf') or filename.endswith('.PDF'):
    file_folder = file2img(os.path.join(org_file_path, filename), temp_file_path)[0]
    imglist = [os.path.join(file_folder, 'image', page) for page in os.listdir(os.path.join(file_folder, 'image'))]
  elif filename.endswith('.tif') or filename.endswith('.tiff'):
    tifpath = os.path.join(temp_file_path, 'image')
    if not os.path.exists(tifpath):
      os.makedirs(tifpath)
    if tif2jpgs(os.path.join(org_file_path, filename), tifpath):
      print('convert tif success')
      imglist = [os.path.join(tifpath, tif) for tif in os.listdir(tifpath)]
  else:
    imglist = [os.path.join(org_file_path, filename)]
  try:
    imglist.sort(key=lambda x: int(os.path.splitext(x)[0].split('_')[-1]))
  except:
    imglist.sort()
    pass
  # print('imglisttttt:',imglist)
  content = []
  table_ = []
  SrcImg = []
  TextImg = []
  TabImg = []
  content = []
  for imi, img_name in enumerate(imglist):
    content_info, tab_info, boder_table_info = img2text(img_name, temp_file_path, imi=imi, Image_enhancement=False,
                                                        Image_direction=False, Image_deseal=False, \
                                                        Tab_detect=True, BorderlessTab_detect=False, \
                                                        Qrcode_detect=False, Clear_tmp=False, fan2jian=True)

    content_ = []
    page_line_list = []
    if tab_info:
      xlspath = os.path.join(process_path, str(imi) + '.xlsx')
      dict2xls(tab_info, xlspath)
      for itt, tab_info_ in enumerate(tab_info):
        page_line_flag = False
        for row_k in tab_info_:
          for c_i, col_info in enumerate(tab_info_[row_k]):
            if len(col_info['page_line']) > 0:
              page_line_list.append(int(tab_info_[row_k][c_i]['page_line'][0].split('_')[-1]))
              page_line_flag = True
              break
          if page_line_flag:
            break
        content_.append({"type": 1, "content": f'//{aa.netloc}/files/{uni_id}/process/' + os.path.split(xlspath)[-1],
                         "name": 'Tab_' + str(itt)})

    if boder_table_info:
      for ittb, bodertab_info in enumerate(boder_table_info):
        boder_content_ = []
        boder_content_.append(bodertab_info['col_left']['text'])
        boder_content_.append(bodertab_info['col_right']['text'])
        page_line_list.append(int(bodertab_info['col_left']['page_line'][0].split('_')[-1]))
        content_.append({"type": 0, "content": '\n'.join(boder_content_), "name": ''})

    if content_info:
      page_line_index = [int(x.split('_')[-1]) for x in content_info['page_line']]
      page_line_list.extend(page_line_index)
      for ii in range(len(content_info['text'])):
        content_.append({"type": 0, "content": content_info['text'][ii], "name": ''})

    index = sorted(range(0, len(page_line_list)), key=lambda k: page_line_list[k])
    content_ = [content_[id] for id in index]

    content.append(content_)

    shutil.move(img_name, os.path.join(process_path, os.path.split(img_name)[-1]))
    SrcImg.append(f'//{aa.netloc}/files/{uni_id}/process/' + os.path.split(img_name)[-1])
    TextImg.append(f'//{aa.netloc}/files/{uni_id}/process/' + str(imi) + '_result.jpg')

    if tab_info or boder_table_info:
      table_.append(f'//{aa.netloc}/files/{uni_id}/process/' + os.path.split(xlspath)[-1])
      TabImg.append(f'//{aa.netloc}/files/{uni_id}/process/' + str(imi) + '_tabcell.jpg')

  return jsonify({"code": 0,
                  "msg": 'success',
                  "content": content,
                  "table": table_,
                  "image": SrcImg,
                  "text_detect_image": TextImg,
                  "tabel_detect_image": TabImg
                  })


@app.route('/api/upload_ocr', methods=['POST'])
def uploadOCR():
  file = request.files['file']
  filename = secure_filename(file.filename)
  if os.path.splitext(filename)[-1].lower() not in ['.jpg','.jpeg','.bmp','.png']:
    return jsonify({"code": 406, "result": "image format is not supported"})
  uni_id = str(time.time())
  temp_file_path = os.path.join(FILE_PATH, uni_id)
  if not os.path.exists(temp_file_path):
    os.makedirs(temp_file_path)
  img = file.read()
  imi = 0
  result = {}
  content_info, _, _ = img2text(img, temp_file_path, imi=imi, Image_enhancement=False,
                                                      Image_direction=False, Image_deseal=False, \
                                                      Tab_detect=False, BorderlessTab_detect=False, \
                                                      Qrcode_detect=False, Clear_tmp=True, fan2jian=False)

  if content_info:
    if len(content_info['text'])>0:
      result["text"] = content_info['text']
      result["text_img_pos"] = content_info["text_img_pos"]
      result["w"] = content_info["w"]
      result["h"] = content_info["h"]

  json_str = json.dumps({"code": 0, "result": result}, cls=MyEncoder, ensure_ascii=False)
  return json_str


@app.route('/api/upload_IDapp', methods=['POST'])
def uploadId():
    file = request.files['file']
    filename = secure_filename(file.filename)
    if os.path.splitext(filename)[-1].lower() not in ['.jpg', '.jpeg', '.bmp', '.png']:
      return jsonify({"code": 406, "result": "image format is not supported"})
    uni_id = str(time.time())
    temp_file_path = os.path.join(FILE_PATH, uni_id)
    if not os.path.exists(temp_file_path):
        os.makedirs(temp_file_path)
    aa = urllib.parse.urlparse(request.url)
    org_file_path = os.path.join(temp_file_path, 'orgfile')
    if not os.path.exists(org_file_path):
        os.makedirs(org_file_path)
    #
    # process_path = os.path.join(temp_file_path, 'process')
    # if not os.path.exists(process_path):
    #     os.makedirs(process_path)
    imgpath = os.path.join(org_file_path, filename)
    # print('fiiii:',filename)
    ###################去掉透明边操作#####################
    # image_encode = file.read()
    # image_buff = np.frombuffer(image_encode, np.uint8)
    # image = cv2.imdecode(image_buff, -1)
    # y, x = np.where(image[:, :, -1] > 0)
    # xmin = np.min(x)
    # xmax = np.max(x)
    # ymin = np.min(y)
    # ymax = np.max(y)
    # cv2.imwrite(imgpath, image[ymin:ymax,xmin:xmax,:])
    #################################################################
    file.save(imgpath)
    boxes,_,_ = face_detect(imgpath)
    content_info, tab_info, boder_table_info = img2text(imgpath, temp_file_path, imi=0, Image_enhancement=False,
                                                        Image_direction=False, Image_deseal=False, \
                                                        Tab_detect=False, BorderlessTab_detect=False, \
                                                        Qrcode_detect=False, Clear_tmp=True, fan2jian=False)
    if content_info:
      if len(boxes)>0:
        IDparse = idcard(content_info)
        result = IDparse.parse_strcture()
      else:
        IDparse = idcard_b(content_info)
        result = IDparse.parse_strcture()
    # content = []
    # for kk in result:
    #     content.append(kk+': '+result[kk])

    #shutil.move(imgpath, os.path.join(process_path, os.path.split(imgpath)[-1]))
    SrcImg = f'//{aa.netloc}/files/{uni_id}/process/' + os.path.split(imgpath)[-1]
    #TextImg = f'//{aa.netloc}/files/{uni_id}/process/' + '0_result.jpg'

    return jsonify({"code": 0,
                    # "msg": 'success',
                    "result": result,
                    "image": SrcImg,
                    # "text_detect_image": TextImg
                    })


@app.route('/api/upload_BISapp', methods=['POST'])
def uploadBis():
    file = request.files['file']
    filename = secure_filename(file.filename)
    if os.path.splitext(filename)[-1].lower() not in ['.jpg', '.jpeg', '.bmp', '.png']:
      return jsonify({"code": 406, "result": "image format is not supported"})
    uni_id = str(time.time())
    temp_file_path = os.path.join(FILE_PATH, uni_id)
    if not os.path.exists(temp_file_path):
        os.makedirs(temp_file_path)
    aa = urllib.parse.urlparse(request.url)
    org_file_path = os.path.join(temp_file_path, 'orgfile')
    if not os.path.exists(org_file_path):
        os.makedirs(org_file_path)
    #
    # process_path = os.path.join(temp_file_path, 'process')
    # if not os.path.exists(process_path):
    #     os.makedirs(process_path)
    imgpath = os.path.join(org_file_path, filename)
    # print('fiiii:',filename)
    ###################去掉透明边操作#####################
    # image_encode = file.read()
    # image_buff = np.frombuffer(image_encode, np.uint8)
    # image = cv2.imdecode(image_buff, -1)
    # y, x = np.where(image[:, :, -1] > 0)
    # xmin = np.min(x)
    # xmax = np.max(x)
    # ymin = np.min(y)
    # ymax = np.max(y)
    # cv2.imwrite(imgpath, image[ymin:ymax, xmin:xmax, :])
    #################################################################
    file.save(imgpath)
    content_info, tab_info, boder_table_info = img2text(imgpath, temp_file_path, imi=0, Image_enhancement=False,
                                                        Image_direction=False, Image_deseal=False, \
                                                        Tab_detect=False, BorderlessTab_detect=False, \
                                                        Qrcode_detect=False, Clear_tmp=True, fan2jian=False)
    if content_info:
      IDparse = BusiLicense(content_info)
      result = IDparse.parse_strcture()
    # content = []
    # for kk in result:
    #   if kk == '经营范围' or kk == '编号':
    #     continue
    #   content.append(kk+': '+result[kk])
    result_ = {}
    for kk in result:
      if kk == '经营范围' or kk == '编号':
        continue
      result_[kk] = result[kk]

    #shutil.move(imgpath, os.path.join(process_path, os.path.split(imgpath)[-1]))
    SrcImg = f'//{aa.netloc}/files/{uni_id}/process/' + os.path.split(imgpath)[-1]
    #TextImg = f'//{aa.netloc}/files/{uni_id}/process/' + '0_result.jpg'

    return jsonify({"code": 0,
                    "result": result_,
                    "image": SrcImg,
                    })


@app.route("/files/<uni_id>/process/<file>")
def files(uni_id, file):
  # import ipdb;ipdb.set_trace()
  abs_file = os.path.join(FILE_PATH, uni_id, "process", file)
  return send_file(abs_file, as_attachment=True)


@app.route('/api/download', methods=['POST'])
def download():
  data = request.json
  if data["type"] == 1:
    # print(data["file"].split('files/')[-1])
    shutil.copy(os.path.join(FILE_PATH, data["file"].split('files/')[-1]),
                os.path.join(GOOD_PATH, str(len(os.listdir(GOOD_PATH))) + "g_" + os.path.split(data["file"])[-1]))
  if data["type"] == 2:
    # print(data["file"].split('files/')[-1])
    shutil.copy(os.path.join(FILE_PATH, data["file"].split('files/')[-1]),
                os.path.join(BAD_PATH, str(len(os.listdir(BAD_PATH))) + "b_" + os.path.split(data["file"])[-1]))
  return jsonify({"code": 0})


@app.route('/')
def index():
  return render_template('index.html')

# @app.route('/appid')
# def index_appid():
#   return render_template('index.html')
# #
# @app.route('/appbis')
# def index_appbis():
#   return render_template('index.html')

@app.route('/CameraH5')
def index_appCAM():
  return render_template('cam_index.html')


# @app.route('/static/css/<file>')
# def css_file(file):
#     return send_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'css', file),as_attachment=True)
# @app.route('/static/js/<file>')
# def js_file(file):
#     return send_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'js', file),as_attachment=True)
# @app.route('/static/fonts/<file>')
# def fonts_file(file):
#     return send_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'fonts', file),as_attachment=True)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3555, debug=True)
