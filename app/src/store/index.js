import Vue from 'vue'
import Vuex from 'vuex'
import VuexPersistence from 'vuex-persist'
import axios from 'axios'

Vue.use(Vuex)

const vuexLocal = new VuexPersistence({
  key: 'bg-vuex',
  storage: window.localStorage
})

const supportedVersions = [
  '1.15'
]

export default new Vuex.Store({
  plugins: [vuexLocal.plugin],
  state: {
    gameData: {},
    selectedVersion: supportedVersions[0],
    supportedVersions,
    skipSplash: false,
    selectedItems: [],
    tmpSelectedItems: null,
    recipeTree: [],
    shoppingList: [],
  },
  mutations: {
    setSkipSplash (state, bool) {
      state.skipSplash = bool
    },
    setItems (state, itemsArr) {
      const gameData = state.gameData
      if (typeof gameData[state.selectedVersion] === 'undefined') {
        gameData[state.selectedVersion] = {}
      }
      gameData[state.selectedVersion].items = itemsArr
      state.gameData = Object.assign({}, state.gameData, gameData)
    },
    setSelectedItems (state, itemsArr) {
      state.selectedItems = itemsArr
    },
    setTmpSelectedItems (state, itemsArr) {
      state.tmpSelectedItems = itemsArr
    },
    setRecipeTree (state, tree) {
      state.recipeTree = tree
    },
    setShoppingList (state, shoppingList) {
      state.shoppingList = shoppingList
    },
  },
  actions: {
    setupSearchStore ({ state, commit }) {
      if (
        typeof state.gameData[state.selectedVersion] === 'undefined' ||
        typeof state.gameData[state.selectedVersion].items === 'undefined'
      ) {
        axios
          .get('http://0.0.0.0:5000/api/1.15/items')
          .then(response => {
            commit('setItems', response.data)
          })
      }

      if (state.tmpSelectedItems === null) {
        const selectedItemNames = []
        for (let i = 0, l = state.selectedItems.length; i < l; i += 1) {
          selectedItemNames.push(state.selectedItems[i].name)
        }
        commit('setTmpSelectedItems', selectedItemNames)
      }
    },
    setSelectedFromTmp ({ state, commit }, tmpItems) {
      const selectedByName = {}
      for (let i = 0, l = state.selectedItems.length; i < l; i += 1) {
        const item = state.selectedItems[i]
        selectedByName[item.name] = item
      }

      const selectedItems = []
      for (let i = 0, l = tmpItems.length; i < l; i += 1) {
        const itemName = tmpItems[i]
        const amount = (selectedByName[itemName]) ? selectedByName[itemName].amount : 1
        selectedItems.push({
          name: itemName,
          amount
        })
      }

      commit('setSelectedItems', selectedItems)
      commit('setTmpSelectedItems', null)
    },
    calculateResources ({ state, commit }) {
      const numSelectedItems = state.selectedItems.length
      if (numSelectedItems === 0) {
        return
      }

      const items = []
      for (let i = 0; i < numSelectedItems; i += 1) {
        const item = state.selectedItems[i]
        items.push({
          name: item.name,
          amount_required: item.amount
        })
      }

      axios
        .post('http://0.0.0.0:5000/api/1.15/calculate_resources', { items })
        .then(response => {
          commit('setRecipeTree', response.data.recipe_tree)
          commit('setShoppingList', response.data.shopping_list)
        })
    }
  },
  modules: {
  }
})
