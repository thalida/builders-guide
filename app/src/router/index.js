import Vue from 'vue'
import VueRouter from 'vue-router'
import Index from '../views/Index.vue'
import Splash from '../views/Splash/Index.vue'
import Cookbook from '../views/Cookbook/Index.vue'
import CookbookBuild from '../views/Cookbook/Build/Index.vue'
import CookbookBuildSearch from '../views/Cookbook/Build/Search.vue'
import CookbookBuildLibrary from '../views/Cookbook/Build/Library.vue'
import CookbookBuildFreeform from '../views/Cookbook/Build/Freeform.vue'
import CookbookRecipes from '../views/Cookbook/Recipes/Index.vue'
import CookbookShoppingList from '../views/Cookbook/ShoppingList/Index.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '',
    component: Index,
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
    component: () =>
      import(/* webpackChunkName: "about" */ '../views/About/Index.vue')
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes,
})

export default router
