<template>
  <div class="main">
    <div class="left">
      <el-row style="height:80px;">
        <el-upload
          class="upload-demo"
          action="http://127.0.0.1:3555/api/upload"
          :multiple="multiple"
          :on-success="handleAvatarSuccess"
          :file-list="fileList">
          <el-button type="primary">点击上传</el-button>
          <!-- <div slot="tip" class="el-upload__tip">只能上传jpg/png文件，且不超过500kb</div> -->
        </el-upload>
      </el-row>
      <el-row>
        <el-button type="success"  @click="changeImage('image')">原图</el-button>
        <el-button type="success"  @click="changeImage('text_detect_image')">文字检测结果</el-button>
        <el-button type="warning"  @click="changeImage('tabel_detect_image')">表格检测结果</el-button>
      </el-row>
      <el-card class="box-card">
        <el-image v-if="imgSrC" :src="imgSrC" alt="" :preview-src-list="[imgSrC]" fit="contain"></el-image>
      </el-card>
    </div>
    <div class="right">
      <el-row style="height:80px;">
        <el-button type="primary" >检测准确</el-button>
        <el-button type="success" >检测失误</el-button>
      </el-row>
      <el-row>
        <el-button type="success" @click="changeResult(1)">text</el-button>
        <el-button type="warning" @click="changeResult(2)">table</el-button>
      </el-row>
      <el-card class="box-card" ref="card">
        <p v-show="resultShowType == 1" v-for="(item, index) in resultText" :key="index">{{item}}</p>
        <excel-view :height="height" :width="width" v-show="resultShowType == 2" ref="excel" />
      </el-card>
    </div>
  </div>
</template>

<script>
  import ExcelView from '@/components/ExcelView'
  export default {
    components: {ExcelView},
    data() {
      return {
        multiple: false,
        fileList: [],
        imgSrC: '',
        resultShowType: 1,
        resultText: [],
        checkResult: {},
        excelData: null,
        height: '',
        width: ''
      }
    },
    mounted() {
      this.height = this.$refs.card.$el.clientHeight - 40 + 'px'
      this.width = this.$refs.card.$el.clientWidth - 40 + 'px'
    },
    methods: {
      handleAvatarSuccess(response, file, fileList) {
        if(response.code == 0) {
          this.checkResult = response;
          this.resultText = this.checkResult.content;
          this.fileList = [file];
          this.changeImage('image')
          this.$refs.excel.setExcelData(this.checkResult.table)
        }
      },
      changeImage(filed) {
        this.imgSrC = this.checkResult[filed]
      },
      changeResult(type) {
        this.resultShowType = type
      }
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
  overflow: auto;
}
.el-image {
  width: 100%;
  height: 100%;
}
/deep/ .el-card__body {
  height: 100%;
  box-sizing: border-box
}
</style>