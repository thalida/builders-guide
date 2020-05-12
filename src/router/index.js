import Vue from 'vue'
import VueRouter from 'vue-router'
import Splash from '../views/Splash.vue'
import Cookbook from '../views/Cookbook.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Home',
    beforeEnter: (to, from, next) => {
      const skipSplash = Vue.localStorage.get('skipSplash', false, Boolean)
      let nextRoute = ''

      if (skipSplash) {
        nextRoute = '/cookbook'
      } else {
        nextRoute = '/splash'
      }

      next(nextRoute)
    }
  },
  {
    path: '/splash',
    name: 'Splash',
    component: Splash
  },
  {
    path: '/cookbook',
    name: 'Cookbook',
    component: Cookbook
  },
  {
    path: '/about',
    name: 'About',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () =>
      import(/* webpackChunkName: "about" */ '../views/About.vue')
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
