<template>
  <div :id="id" :style="{width: width, height: height}"></div>
</template>

<script>
import LuckyExcel from "luckyexcel";
import("@/assets/luckysheet/plugins/plugins.css");
import("@/assets/luckysheet/plugins/css/pluginsCss.css");
import("@/assets/luckysheet/assets/iconfont/iconfont.css");
import("@/assets/luckysheet/css/luckysheet.css");
import "@/assets/luckysheet/plugins/js/plugin.js";
import "@/assets/luckysheet/luckysheet.umd.js";

export default {
  name: "ExcelView",
  props: {
    id: {
      type: String,
      default: "luckysheet"
    },
    url: {
      type: String,
      default: ""
    },
    height: {
      type: String,
      default: "100%"
    },
    width: {
      type: String,
      default: "100%"
    },
  },
  data() {
    return {};
  },
  mounted() {
    if(this.url){
      this.setExcelData(this.url)
    }
  },
  methods: {
    setExcelData(url) {
      // url = "https://minio.cnbabylon.com/public/luckysheet/money-manager-2.xlsx";
      let id = this.id;
      LuckyExcel.transformExcelToLuckyByUrl(url, " ", (exportJson, luckysheetfile) => {
        if (exportJson.sheets == null || exportJson.sheets.length == 0) {
          alert(
            "Failed to read the content of the excel file, currently does not support xls files!"
          );
          return;
        }
        let lucky = luckysheet
        lucky.destroy();

        lucky.create({
          container: id, //luckysheet is the container id
          lang: "zh",
          allowEdit: false, // 是否允许编辑
          showinfobar: false, // 是否显示信息栏
          showtoolbar: false, // 是否显示工具栏
          showsheetbar: true, // 是否显示底部sheet栏
          showstatisticBar: false, // 底部计数栏
          showsheetbarConfig: {
            add: false, //新增sheet
            menu: false, //sheet管理菜单
          },
          sheetRightClickConfig: {
            delete: false, // 删除
            copy: false, // 复制
            rename: false, //重命名
            color: false, //更改颜色
            hide: false, //隐藏，取消隐藏
            move: false, //向左移，向右移
          },
          cellRightClickConfig: {
            copy: true, // 复制
            copyAs: false, // 复制为
            paste: false, // 粘贴
            insertRow: false, // 插入行
            insertColumn: false, // 插入列
            deleteRow: false, // 删除选中行
            deleteColumn: false, // 删除选中列
            deleteCell: false, // 删除单元格
            hideRow: false, // 隐藏选中行和显示选中行
            hideColumn: false, // 隐藏选中列和显示选中列
            rowHeight: false, // 行高
            columnWidth: false, // 列宽
            clear: false, // 清除内容
            matrix: false, // 矩阵操作选区
            sort: false, // 排序选区
            filter: false, // 筛选选区
            chart: false, // 图表生成
            image: false, // 插入图片
            link: false, // 插入链接
            data: false, // 数据验证
            cellFormat: false, // 设置单元格格式
          },
          enableAddRow: false,
          sheetFormulaBar: false,
          data: exportJson.sheets,
          title: exportJson.info.name,
          userInfo: exportJson.info.name.creator,
        });
      });
    },
  },
};
</script>