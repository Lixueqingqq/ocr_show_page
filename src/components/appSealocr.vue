<template>
  <div class="main">
    <div class="left">
      <el-row style="height:100px; margin-left:0">
        <el-upload
          class="upload-demo"
          action="/api/sealocr"
          :multiple="multiple"
          :on-success="handleAvatarSuccess"
          :file-list="fileList"
        >
          <el-button type="primary">点击上传</el-button>
          <!-- <div slot="tip" class="el-upload__tip">只能上传jpg/png文件，且不超过500kb</div> -->
        </el-upload>
      </el-row>
      <el-row>
        <el-button type="success"  @click="changeImage('image')">原图</el-button>
        <el-button type="success"  @click="changeImage('text_detect_image')">文字检测结果</el-button>
        <!-- <el-button type="warning"  @click="changeImage('tabel_detect_image')">表格检测结果</el-button> -->
      </el-row>
      <el-card class="box-card">
        <el-image v-if="imgSrC" :src="imgSrC" alt="" :preview-src-list="[imgSrC]" fit="contain"></el-image>
      </el-card>
    </div>
    <div class="right">
      <el-card class="box-card">
        <p v-show="resultShowType == 1" v-for="(item, index) in resultText" :key="index">{{item.content}}</p>
      </el-card>
    </div>
  </div>
</template>

<script>
// import XlsxView from './XlsxView/index.vue'
export default {
  // components: { XlsxView },
   data() {
      return {
        multiple: false,
        fileList: [],
        imgSrC: '',
        resultShowType: 1,
        resultText: [],
        checkResult: {},
        // excelData: null
      }
    },
  mounted() {},
  methods: {
    handleAvatarSuccess(response, file, fileList) {
      if(response.code == 0) {
        this.checkResult = response;
        // console.log('response',this.checkResult) 输出结果，用于中间debug
        this.resultText = this.checkResult.content;
        this.fileList = [file];
        this.changeImage('image')
        // this.getExcelData(this.checkResult.table)
      }
    },
    changeImage(filed) {
      this.imgSrC = this.checkResult[filed]
    },
    changeResult(type) {
      this.resultShowType = type
    },
    // getExcelData(url) {
    //   this.$axios.get(url, {
    //     responseType: 'arraybuffer'
    //   })
    //   .then((res) => {
    //     this.excelData = res.data
    //   })
    // }
  }
}
</script>

<style scoped>
.main {
  padding: 20px;
  display: flex;
}
.left {
  width: 50%;
}
.right {
  width: 50%;
}
.el-row {
  margin: 20px;
}
.el-card {
  width: 90%;
  height: 600px;
  border: 1px solid #f1f1f1;
  overflow: scroll;
}
.el-image {
  width: 100%;
  height: 100%;
}
</style>