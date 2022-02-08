import Vue from 'vue'
import Router from 'vue-router'
import Test from '@/components/test'
import Test1 from '@/components/test_single'
import Test2 from '@/components/test_imglist_tabsingle'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Test',
      component: Test
    },
    {
      path: '/test1',
      name: 'Test1',
      component: Test1
    },
    {
      path: '/test2',
      name: 'Test2',
      component: Test2
    }
  ]
})
