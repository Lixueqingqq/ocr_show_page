from flask import Flask, jsonify, request, send_file,render_template
#from werkzeug.utils import secure_filename
from util import  dict2xls,secure_filename
from flask_cors import CORS
import numpy as np
import time
import os
from ocr_sdk.files2image.file2img import file2img
from ocr_sdk.image_to_text.img2text import img2text
import urllib
import shutil

FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'files')
os.makedirs(FILE_PATH, exist_ok=True)
GOOD_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"good_case")
os.makedirs(GOOD_PATH, exist_ok=True)
BAD_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"bad_case")
os.makedirs(BAD_PATH, exist_ok=True)
app = Flask(__name__, static_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)),'static'),template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)),'dist'))
#app.config["JSON_AS_ASCII"]=False
CORS(app,supports_credetials=True)

@app.route('/api/upload', methods=['POST'])
def upload():
    file = request.files['file']
    uni_id = str(time.time())
    temp_file_path = os.path.join(FILE_PATH, uni_id)
    if not os.path.exists(temp_file_path):
        os.makedirs(temp_file_path)
    aa = urllib.parse.urlparse(request.url)
    org_file_path = os.path.join(temp_file_path,'orgfile')
    if not os.path.exists(org_file_path):
        os.makedirs(org_file_path)

    process_path = os.path.join(temp_file_path,'process')
    if not os.path.exists(process_path):
        os.makedirs(process_path)

    filename = secure_filename(file.filename)
    #print('fiiii:',filename)
    file.save(os.path.join(org_file_path, filename))
    if filename.endswith('.pdf') or filename.endswith('.PDF'):
        file_folder = file2img(os.path.join(org_file_path, filename),temp_file_path)[0]
        imglist = [os.path.join(file_folder,'image',page) for page in os.listdir(os.path.join(file_folder,'image'))]
    else:
        imglist = [os.path.join(org_file_path, filename)]
    try:
        imglist.sort(key=lambda x:int(os.path.splitext(x)[0].split('_')[-1]))
    except:
        imglist.sort()
        pass
    #print('imglisttttt:',imglist)
    content_ = []
    table_ = []
    SrcImg = []
    TextImg = []
    TabImg = []
    for imi,img_name in enumerate(imglist):
        content_info,tab_info,boder_table_info = img2text(img_name,temp_file_path,imi=imi,Image_enhancement=True,Image_direction=True,Image_deseal=True,\
                                                        Tab_detect=True,BorderlessTab_detect=False,\
                                                        Qrcode_detect=False,Clear_tmp=False,fan2jian=False)
        if content_info:
            page_line_index=[int(x.split('_')[-1]) for x in content_info['page_line']]
            index = np.argsort(page_line_index)
            for ii in index:
                content_.append(content_info['text'][ii])

        if tab_info:
            xlspath = os.path.join(process_path, str(imi) + '.xlsx')
            dict2xls(tab_info, xlspath)
            # for itt,tab_info_ in enumerate(tab_info):
            #     for info_k in tab_info_.keys():
            #         for c_i, col_info in enumerate(tab_info_[info_k]):
            #             content_.append(tab_info_[info_k][c_i]["text"])


        if boder_table_info:
            for ittb,bodertab_info in enumerate(boder_table_info):
                content_.append(bodertab_info['col_left']['text'])
                content_.append(bodertab_info['col_right']['text'])

        shutil.move(img_name,os.path.join(process_path,os.path.split(img_name)[-1]))
        SrcImg.append(f'//{aa.netloc}/files/{uni_id}/process/'+os.path.split(img_name)[-1])
        TextImg.append(f'//{aa.netloc}/files/{uni_id}/process/'+str(imi)+'_result.jpg')

        if tab_info:
            table_.append(f'//{aa.netloc}/files/{uni_id}/process/'+os.path.split(xlspath)[-1])
            TabImg.append(f'//{aa.netloc}/files/{uni_id}/process/'+str(imi)+'_tabcell.jpg')

    return jsonify({"code": 0,
                    "msg": 'success',
                    "content":content_,
                    "table": table_,
                    "image": SrcImg,
                    "text_detect_image":TextImg,
                    "tabel_detect_image":TabImg
                    })

@app.route("/files/<uni_id>/process/<file>")
def files(uni_id, file):
    # import ipdb;ipdb.set_trace()
    abs_file = os.path.join(FILE_PATH,uni_id, "process", file)
    return send_file(abs_file, as_attachment=True)

@app.route('/api/download', methods=['POST'])
def download():
    data = request.json
    if data["type"] == 1:
        #print(data["file"].split('files/')[-1])
        shutil.copy(os.path.join(FILE_PATH,data["file"].split('files/')[-1]),os.path.join(GOOD_PATH,str(len(os.listdir(GOOD_PATH)))+"g_"+os.path.split(data["file"])[-1]))
    if data["type"] == 2:
        #print(data["file"].split('files/')[-1])
        shutil.copy(os.path.join(FILE_PATH,data["file"].split('files/')[-1]),os.path.join(BAD_PATH,str(len(os.listdir(BAD_PATH)))+"b_"+os.path.split(data["file"])[-1]))
    return jsonify({"code": 0})


@app.route('/')
def index():
    return render_template('index.html')

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
