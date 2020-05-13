import Vue from 'vue'
import VueObserveVisibility from 'vue-observe-visibility'

import App from './App.vue'
import router from './router'
import store from './store'
import './registerServiceWorker'

Vue.config.productionTip = false
Vue.use(VueObserveVisibility)

new Vue({
  router,
  store,
  localStorage: {
    skipSplash: {
      type: Boolean,
      default: false
    },
  },
  render: h => h(App)
}).$mount('#app')
