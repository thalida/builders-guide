import Vue from 'vue'
import VueRouter from 'vue-router'
import Index from '../views/Index.vue'
import Splash from '../views/Splash/Index.vue'
import Cookbook from '../views/Cookbook/Index.vue'
// import CookbookBuild from '../views/Cookbook/Build/Index.vue'
// import CookbookBuildSearch from '../views/Cookbook/Build/Search.vue'
// import CookbookBuildFreeform from '../views/Cookbook/Build/Freeform.vue'
// import CookbookRecipes from '../views/Cookbook/Recipes/Index.vue'
// import CookbookShoppingList from '../views/Cookbook/ShoppingList/Index.vue'

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
        name: 'build',
        path: 'build',
        component: () => import(/* webpackPrefetch: true */ '../views/Cookbook/Build/Index.vue'),
        children: [
          {
            path: 'search',
            component: () => import(/* webpackPrefetch: true */ '../views/Cookbook/Build/Search.vue'),
            meta: {
              modal: true,
              returnFocusOnDeactivate: true
            },
            props: (route) => ({ query: route.query.q }),
          },
          {
            path: 'freeform',
            component: () => import('../views/Cookbook/Build/Freeform.vue'),
            meta: {
              modal: true,
            },
          },
        ],
      },
      {
        name: 'recipes',
        path: 'recipes',
        component: () => import('../views/Cookbook/Recipes/Index.vue'),
      },
      {
        name: 'shoppingList',
        path: 'shopping-list',
        component: () => import('../views/Cookbook/ShoppingList/Index.vue'),
      }
    ],
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/About/Index.vue')
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes,
})

export default router
