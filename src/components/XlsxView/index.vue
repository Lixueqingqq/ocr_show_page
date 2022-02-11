<template>
  <div class="xlsx-view-container">
    <div v-html="tableHtml"></div>
  </div>
</template>

<script>
import XLSX from 'xlsx'
export default {
  name: 'XlsxView',
  components: {},
  data() {
    return {
      tableHtml: ''
    }
  },
  props: {
    url: {
      type: String
    },
    sheetName: {
      type: String
    }
  },
  computed: {},
  watch: {
    url: function(val) {
      if (val !== '') {
        this.init(val)
      }
    }
  },
  created() {},
  mounted() {
    if (this.url !== '') {
      this.init(this.url)
    }
  },
  methods: {
    init(url) {
      let activeSheetIndex = this.sheetName.split('_')[1]
      this.$axios
        .get(url, {
          responseType: 'arraybuffer'
        })
        .then(res => {
          var data = new Uint8Array(res.data)
          var wb = XLSX.read(data, { type: 'array' })
          // 获取需要显示的工作表
          var wsname = wb.SheetNames[activeSheetIndex]
          var ws = wb.Sheets[wsname]
          /* 生成HTML输出 */
          var data2 = XLSX.utils.sheet_to_html(ws)
          this.tableHtml = data2
          console.log(data2)
        })
    }
  }
}
</script>
<style>
.xlsx-view-container table {
  border: 1px solid #000;
  border-collapse: collapse;
}
.xlsx-view-container table tr {
  border: 1px solid #000;
  height: 20px;
}
.xlsx-view-container table tr td {
  border: 1px solid #000;
}
.xlsx-view-container table tr th {
  border: 1px solid #000;
}
</style>
