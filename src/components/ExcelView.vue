<template>
  <div
    id="luckysheet"
    style="width:400px;height:400px"
  ></div>
</template>

<script>
// import LuckyExcel from 'luckyexcel'
import ('@/assets/luckysheet/plugins/plugins.css');
import ('@/assets/luckysheet/plugins/css/pluginsCss.css');
import ('@/assets/luckysheet/assets/iconfont/iconfont.css');
import ('@/assets/luckysheet/css/luckysheet.css');
import '@/assets/luckysheet/plugins/js/plugin.js';
import '@/assets/luckysheet/luckysheet.umd.js';

export default {
  name: 'ExcelView',
  props: {
    msg: String
  },
  data(){
    return {

    }
  },
  mounted() {
    // $(function () {
    //   luckysheet.create({
    //     container: "luckysheet",
    //   });
    // });
  },
  methods: {
    setExcelData(url) {
      url = 'https://minio.cnbabylon.com/public/luckysheet/money-manager-2.xlsx'
      LuckyExcel.transformExcelToLuckyByUrl(url, ' ', (exportJson, luckysheetfile) => {

        if(exportJson.sheets==null || exportJson.sheets.length==0){
            alert("Failed to read the content of the excel file, currently does not support xls files!");
            return;
        }

        this.isMaskShow = false;
        window.luckysheet.destroy();

        window.luckysheet.create({
            container: 'luckysheet', //luckysheet is the container id
            showinfobar:false,
            data:exportJson.sheets,
            title:exportJson.info.name,
            userInfo:exportJson.info.name.creator
        });
      });
    }
  }
}
</script>
<style scoped>

</style>
