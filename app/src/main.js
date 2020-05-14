import Vue from 'vue'
import VueObserveVisibility from 'vue-observe-visibility'
import VueVirtualScroller from 'vue-virtual-scroller'

import App from './App.vue'
import router from './router'
import store from './store'
import './registerServiceWorker'

import 'vue-virtual-scroller/dist/vue-virtual-scroller.css'

Vue.config.productionTip = false
Vue.use(VueObserveVisibility)
Vue.use(VueVirtualScroller)

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
