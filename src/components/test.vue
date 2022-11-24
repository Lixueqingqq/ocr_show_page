<template>
  <el-tabs v-model="activeName" style="padding: 5px;">
    <el-tab-pane label="OCR图片解析" name="ocr">
      <div class="main">
        <div class="left">
          <el-row style="height:100px; margin-left:0">
            <el-upload
              class="upload-demo"
              action="/api/upload"
              :multiple="multiple"
              :on-success="handleAvatarSuccess"
              :file-list="fileList"
            >
              <el-button type="primary">上传文件</el-button>
              <!-- <div slot="tip" class="el-upload__tip">只能上传jpg/png文件，且不超过500kb</div> -->
            </el-upload>
          </el-row>
          <el-row>
            <el-button type="primary" @click="changeImage(1)">原图</el-button>
            <el-button type="success" @click="changeImage(2)">
              文字检测结果
            </el-button>
            <el-button type="warning" @click="changeImage(3)">
              表格检测结果
            </el-button>
          </el-row>
          <el-card class="box-card">
            <el-carousel
              ref="carousel1"
              :interval="5000"
              arrow="always"
              v-show="imgSrcType == 1"
              trigger="click"
              :autoplay="false"
              @change="onCarouselChange"
            >
              <el-carousel-item
                v-for="(item, index) in imgSrc"
                :key="index"
                :name="index.toString()"
              >
                <div style="text-align:right">
                  <el-button
                    v-if="!item.suc"
                    type="primary"
                    @click="checkResultComment(item.src, 1, index)"
                  >
                    检测准确
                  </el-button>
                  <el-button
                    v-if="!item.err"
                    type="success"
                    @click="checkResultComment(item.src, 2, index)"
                  >
                    检测失误
                  </el-button>
                </div>
                <el-image
                  :src="item.src"
                  alt=""
                  :preview-src-list="[item.src]"
                  fit="contain"
                ></el-image>
              </el-carousel-item>
            </el-carousel>

            <el-carousel
              ref="carousel2"
              :interval="5000"
              arrow="always"
              v-show="imgSrcType == 2"
              trigger="click"
              :autoplay="false"
              @change="onCarouselChange"
            >
              <el-carousel-item
                v-for="(item, index) in imgText"
                :key="index"
                :name="index.toString()"
              >
                <el-image
                  :src="item"
                  alt=""
                  :preview-src-list="[item]"
                  fit="contain"
                ></el-image>
              </el-carousel-item>
            </el-carousel>

            <el-carousel
              ref="carousel3"
              :interval="5000"
              arrow="always"
              v-show="imgSrcType == 3"
              trigger="click"
              :autoplay="false"
              @change="onCarouselChange"
            >
              <el-carousel-item
                v-for="(item, index) in imgTable"
                :key="index"
                :name="index.toString()"
              >
                <el-image
                  :src="item"
                  alt=""
                  :preview-src-list="[item]"
                  fit="contain"
                ></el-image>
              </el-carousel-item>
            </el-carousel>
          </el-card>
        </div>
        <div class="right">
          <el-card class="box-card">
            <div v-for="(item, index) in resultText[activeIndex]" :key="index">
              <p v-if="item.type == 0">{{ item.content }}</p>
              <div v-else-if="item.type == 1">
                <xlsx-view
                  :url="item.content"
                  :sheetName="item.name"
                ></xlsx-view>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </el-tab-pane>
    <el-tab-pane label="双层pdf" name="pdf">
      <div style="padding: 5px;">
        <el-upload
          class="upload-demo"
          action="/api/upload_doublepdf"
          :multiple="multiple"
          :on-success="handlePdfSuccess"
          :on-change="handlePdfChange"
          :file-list="pdfFileList"
        >
          <el-button type="primary">上传文件</el-button>
          <!-- <div slot="tip" class="el-upload__tip">只能上传jpg/png文件，且不超过500kb</div> -->
        </el-upload>
        <el-button v-if="pdfUrl" type="primary" @click="downloadPdf">
          下载pdf
        </el-button>
      </div>
    </el-tab-pane>
  </el-tabs>
</template>

<script>
import XlsxView from './XlsxView/index.vue'
export default {
  components: { XlsxView },
  data() {
    return {
      activeName: 'ocr',
      multiple: false,
      fileList: [],
      imgSrc: [],
      imgSrcType: 1,
      imgText: [],
      imgSource: [],
      imgTable: [],
      resultShowType: 1,
      resultText: [],
      checkResult: {},
      excelData: [],
      activeIndex: 0,

      // pdf
      pdfFileList: [],
      pdfUrl: ''
    }
  },
  methods: {
    handleAvatarSuccess(response, file, fileList) {
      if (response.code == 0) {
        this.checkResult = response
        this.resultText = response.content
        this.fileList = [file]
        this.imgText = response.text_detect_image
        this.imgSource = response.image
        this.imgSrc = []
        for (let i = 0; i < response.image.length; i++) {
          this.imgSrc.push({
            src: response.image[i],
            suc: false,
            err: false
          })
        }
        this.imgTable = response.tabel_detect_image
        console.log(response.table)
        this.getExcel(response.table)
      }
    },
    changeImage(type) {
      this.imgSrcType = type
      this.$refs['carousel' + type].setActiveItem(this.activeIndex)
    },
    changeResult(type) {
      this.resultShowType = type
    },
    getExcel(list) {
      this.excelData = []
      for (let i = 0; i < list.length; i++) {
        this.excelData.push(list[i])
      }
    },
    checkResultComment(src, type, index) {
      this.$axios
        .post('/api/download', {
          type: type,
          file: src
        })
        .then(res => {
          console.log(res)
          if (res.code == 0) {
            if (type == 1) {
              this.imgSrc[index].suc = true
            } else {
              this.imgSrc[index].err = true
            }
          }
        })
    },
    onCarouselChange(index) {
      console.log('当前活跃的走马灯索引值', index)
      this.activeIndex = index
    },

    // pdf
    handlePdfChange(file, fileList) {
      console.log('pdf改变')
    },
    handlePdfSuccess(response, file, fileList) {
      console.log('handlePdfSuccess')
      if (response.code === 0) {
        this.pdfFileList = [file]
        this.pdfUrl = response.npdf
      }
    },
    downloadPdf() {
      window.open(this.pdfUrl)
    }
  }
}
</script>

<style scoped>
.main {
  padding: 5px;
  display: flex;
}
.left {
  width: 50%;
}
.right {
  width: 50%;
}
.el-row {
  margin: 10px 10px 10px 0;
}
.el-card {
  width: 97%;
  height: calc(100vh - 185px);
  border: 1px solid #f1f1f1;
  overflow: auto;
}
.right .el-card {
  height: calc(100vh - 15px);
  width: 100%;
}
/deep/ .right .el-carousel__item {
  overflow: auto;
}
.el-image {
  width: 100%;
  height: 100%;
}
/deep/ .el-card__body {
  height: 100%;
  box-sizing: border-box;
}
/deep/ .el-carousel,
/deep/ .el-carousel__container {
  height: 100%;
}
</style>
