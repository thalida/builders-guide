import Vue from 'vue'
import VueRouter from 'vue-router'
import Splash from '../views/Splash.vue'
import Cookbook from '../views/Cookbook/Index.vue'
import CookbookBuild from '../views/Cookbook/Build/Index.vue'
import CookbookBuildSearch from '../views/Cookbook/Build/Search.vue'
import CookbookBuildLibrary from '../views/Cookbook/Build/Library.vue'
import CookbookBuildFreeform from '../views/Cookbook/Build/Freeform.vue'
import CookbookRecipes from '../views/Cookbook/Recipes.vue'
import CookbookShoppingList from '../views/Cookbook/ShoppingList.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Home',
    redirect: to => {
      const skipSplash = Vue.localStorage.get('skipSplash', false, Boolean)
      let nextRoute = ''

      if (skipSplash) {
        nextRoute = '/cookbook'
      } else {
        nextRoute = '/splash'
      }

      return nextRoute
    },
  },
  {
    path: '/splash',
    name: 'Splash',
    component: Splash
  },
  {
    path: '/cookbook',
    component: Cookbook,
    children: [
      {
        name: 'Cookbook',
        path: '',
        redirect: 'build'
      },
      {
        name: 'CookbookBuild',
        path: 'build',
        component: CookbookBuild,
        children: [
          {
            path: 'search',
            component: CookbookBuildSearch,
            props: (route) => ({ query: route.query.q }),
          },
          {
            path: 'library',
            component: CookbookBuildLibrary
          },
          {
            path: 'freeform',
            component: CookbookBuildFreeform
          },
        ],
      },
      {
        name: 'CookbookRecipes',
        path: 'recipes',
        component: CookbookRecipes
      },
      {
        name: 'CookbookShoppingList',
        path: 'shopping-list',
        component: CookbookShoppingList
      }
    ],
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
