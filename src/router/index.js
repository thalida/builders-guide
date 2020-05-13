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
    component: Splash
  },
  {
    path: '/cookbook',
    component: Cookbook,
    children: [
      {
        path: '',
        redirect: 'build'
      },
      {
        path: 'build',
        component: CookbookBuild,
        children: [
          {
            path: 'search',
            component: CookbookBuildSearch,
            meta: {
              modal: true,
              returnFocusOnDeactivate: false
            },
            props: (route) => ({ query: route.query.q }),
          },
          {
            path: 'library',
            component: CookbookBuildLibrary,
            meta: {
              modal: true,
            },
          },
          {
            path: 'freeform',
            component: CookbookBuildFreeform,
            meta: {
              modal: true,
            },
          },
        ],
      },
      {
        path: 'recipes',
        component: CookbookRecipes
      },
      {
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
  routes,
})

export default router
