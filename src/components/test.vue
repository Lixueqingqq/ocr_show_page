<template>
  <div class="main">
    <div class="left">
      <el-row style="height:100px;">
        <el-upload
          class="upload-demo"
          action="/api/upload"
          :multiple="multiple"
          :on-success="handleAvatarSuccess"
          :file-list="fileList">
          <el-button type="primary">点击上传</el-button>
          <!-- <div slot="tip" class="el-upload__tip">只能上传jpg/png文件，且不超过500kb</div> -->
        </el-upload>
      </el-row>
      <el-row>
        <el-button type="primary" @click="changeImage(1)">原图</el-button>
        <el-button type="success"  @click="changeImage(2)">文字检测结果</el-button>
        <el-button type="warning"  @click="changeImage(3)">表格检测结果</el-button>
      </el-row>
      <el-card class="box-card">
        <el-carousel :interval="5000" arrow="always" v-show="imgSrcType == 1" trigger="click" :autoplay=false>
          <el-carousel-item v-for="(item,index) in imgSrc" :key="index">
            <div style="text-align:right">
              <el-button v-if="!item.suc" type="primary" @click="checkResultComment(item.src,1,index)">检测准确</el-button>
              <el-button v-if="!item.err" type="success" @click="checkResultComment(item.src,2, index)">检测失误</el-button>
            </div>
            <el-image :src="item.src" alt="" :preview-src-list="imgSource" fit="contain"></el-image>
          </el-carousel-item>
        </el-carousel>

        <el-carousel :interval="5000" arrow="always"  v-show="imgSrcType == 2" trigger="click" :autoplay=false>
          <el-carousel-item v-for="(item,index) in imgText" :key="index">
            <el-image :src="item" alt="" :preview-src-list="imgText" fit="contain"></el-image>
          </el-carousel-item>
        </el-carousel>

        <el-carousel :interval="5000" arrow="always"  v-show="imgSrcType == 3" trigger="click" :autoplay=false>
          <el-carousel-item v-for="(item,index) in imgTable" :key="index">
            <el-image :src="item" alt="" :preview-src-list="imgTable" fit="contain"></el-image>
          </el-carousel-item>
        </el-carousel>
      </el-card>
    </div>
    <div class="right">
      <el-row>
        <el-button type="success" @click="changeResult(1)">text</el-button>
        <el-button type="warning" @click="changeResult(2)">table</el-button>
      </el-row>
      <el-card class="box-card">
        <div v-show="resultShowType == 1">
          <p v-for="(item, index) in resultText" :key="index">{{item}}</p>
        </div>
        
        <el-carousel v-if="checkResult.table" v-show="resultShowType == 2" :interval="5000" arrow="always" trigger="click" :autoplay=false>
          <el-carousel-item v-for="(item,index) in checkResult.table.length" :key="index">
            <!-- <excelview :datas="excelData[index]" /> -->
            <lucky-excel v-if="resultShowType == 2" :url="excelData[index]"/>
          </el-carousel-item>
        </el-carousel>
      </el-card>
    </div>
  </div>
</template>

<script>
  // import excelview from 'vue-excelview'
  import LuckyExcel from './LuckyExcel.vue';
  export default {
    // components: {excelview, LuckyExcel},
    components: { LuckyExcel},
    data() {
      return {
        multiple: false,
        fileList: [],
        imgSrc: [],
        imgSrcType:1,
        imgText: [],
        imgSource: [],
        imgTable: [],
        resultShowType: 1,
        resultText: [],
        checkResult: {},
        excelData: []
      }
    },
    mounted() {

    },
    methods: {
      handleAvatarSuccess(response, file, fileList) {
        if(response.code == 0) {
          this.checkResult = response;
          this.resultText = response.content;
          this.fileList = [file];
          this.imgText = response.text_detect_image
          this.imgSource = response.image
          this.imgSrc = []
          for(let i=0;i<response.image.length;i++){
            this.imgSrc.push({
              src: response.image[i],
              suc:false,
              err:false
            })
          }
          this.imgTable = response.tabel_detect_image
          console.log(response.table);
          this.getExcel(response.table)
        }
      },
      changeImage(type) {
        this.imgSrcType = type
      },
      changeResult(type) {
        this.resultShowType = type
      },
      getExcel(list) {
        this.excelData = []
        for(let i=0; i < list.length; i++) {
          this.excelData.push(list[i])
          // this.getExcelData(list[i])
        }
      },
      getExcelData(url) {
        this.$axios.get(url, {
          responseType: 'arraybuffer'
        })
        .then((res) => {
           this.excelData.push(res.data)
        })
      },
      checkResultComment(src,type, index) {
        this.$axios.post("/api/download", {
          type: type,
          file: src
        })
        .then((res) => {
          console.log(res)
          if (res.code == 0) {
            if(type == 1) {
              this.imgSrc[index].suc = true
            } else {
              this.imgSrc[index].err = true
            }
          }
        })
      }
    }
  }
</script>

<style scoped>
.main {
  padding: 0 20px;
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
  height: calc(100vh - 250px);
  border: 1px solid #f1f1f1;
  overflow: auto;
}
.right .el-card {
  height: calc(100vh - 130px);
}
/deep/ .right .el-carousel__item {
  overflow: auto;
}
.el-image {
  width: 100%;
}
/deep/ .el-card__body {
  height: 100%;
  box-sizing: border-box
}
/deep/ .el-carousel,/deep/ .el-carousel__container {
  height: 100%;
}
</style>