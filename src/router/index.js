// import Vue from 'vue'
// import Router from 'vue-router'
// import Test from '@/components/test'

// Vue.use(Router)

// export default new Router({
//   routes: [
//     {
//       path: '/',
//       name: 'Test',
//       component: Test
//     }
//   ]
// })

import Vue from 'vue'
import Router from 'vue-router'
import Test from '@/components/test'
import appID from '@/components/appID'
import appBIS from '@/components/appBIS'
import appSealocr from '@/components/appSealocr'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/appid',
      name: 'APPTest1',
      component: appID
    },
    {
      path: '/',
      name: 'Test',
      component: Test
    },
    {
      path: '/appbis',
      name: 'APPTest2',
      component: appBIS
    },
    {
      path: '/sealocr',
      name: 'APPTest3',
      component: appSealocr
    }

  ]
})
    