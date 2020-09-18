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

const buildRecipePath = (recipeTree, isGroup) => {
  const path = []

  for (let i = 0, l = recipeTree.length; i < l; i += 1) {
    const node = recipeTree[i]

    if (Array.isArray(node)) {
      const chosenNode = buildRecipePath(node.slice(0), true)
      path.push(chosenNode[0])
      continue
    }

    if (!node.selected) {
      continue
    }

    const nodeCopy = Object.assign({}, node)

    if (nodeCopy.num_recipes >= 1) {
      nodeCopy.recipes = buildRecipePath(nodeCopy.recipes, true)
    } else if (nodeCopy.ingredients && nodeCopy.ingredients.length > 0) {
      nodeCopy.ingredients = buildRecipePath(nodeCopy.ingredients)
    }

    path.push(nodeCopy)

    if (isGroup) {
      break
    }
  }

  return path
}

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
    shoppingList: {},
  },
  getters: {
    selectedByKey (state) {
      const selectedByKey = {}
      for (let i = 0, l = state.selectedItems.length; i < l; i += 1) {
        const item = state.selectedItems[i]
        selectedByKey[item.key] = item
      }

      return selectedByKey
    }
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
      gameData[state.selectedVersion].numItems = itemsArr.length
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
    setupSplashStore ({ state, commit }) {
      return new Promise((resolve, reject) => {
        if (
          typeof state.gameData[state.selectedVersion] === 'undefined' ||
          typeof state.gameData[state.selectedVersion].items === 'undefined' ||
          typeof state.gameData[state.selectedVersion].items[0] === 'undefined'
        ) {
          axios
            .get(`http://0.0.0.0:5000/api/${state.selectedVersion}/items`)
            .then(response => {
              commit('setItems', response.data)
              resolve()
            })
            .catch(err => reject(err))
        } else {
          resolve()
        }
      })
    },
    setupSearchStore ({ state, commit }) {
      if (
        typeof state.gameData[state.selectedVersion] === 'undefined' ||
        typeof state.gameData[state.selectedVersion].items === 'undefined' ||
        typeof state.gameData[state.selectedVersion].items[0] === 'undefined'
      ) {
        axios
          .get(`http://0.0.0.0:5000/api/${state.selectedVersion}/items`)
          .then(response => {
            commit('setItems', response.data)
          })
      }

      if (state.tmpSelectedItems === null) {
        const selectedItemNames = []
        for (let i = 0, l = state.selectedItems.length; i < l; i += 1) {
          selectedItemNames.push(state.selectedItems[i].key)
        }
        commit('setTmpSelectedItems', selectedItemNames)
      }
    },
    setSelectedFromTmp ({ state, commit, getters }, tmpItems) {
      const selectedByKey = getters.selectedByKey
      const selectedItems = []

      for (let i = 0, l = tmpItems.length; i < l; i += 1) {
        const itemName = tmpItems[i]
        if (typeof selectedByKey[itemName] !== 'undefined') {
          selectedItems.push(selectedByKey[itemName])
        } else {
          selectedItems.push({
            key: itemName,
            name: itemName,
            amount_required: 1
          })
        }
      }

      commit('setSelectedItems', selectedItems)
      commit('setTmpSelectedItems', null)
    },
    mergeSelectedItems ({ state, commit, getters }, items) {
      const selectedItems = state.selectedItems
      for (let i = 0, l = items.length; i < l; i += 1) {
        const item = items[i]
        const itemKey = item.name || item.tag
        const itemAmount = item.amount_required

        let found = false

        for (let j = 0, k = selectedItems.length; j < k; j += 1) {
          if (itemKey === selectedItems[j].key) {
            found = true
            selectedItems[j].amount_required += itemAmount
            break
          }
        }

        if (!found) {
          const newItem = {
            key: itemKey,
            amount_required: itemAmount,
          }

          if (typeof item.tag !== 'undefined') {
            newItem.tag = itemKey
          } else {
            newItem.name = itemKey
          }

          selectedItems.push(newItem)
        }
      }

      commit('setSelectedItems', selectedItems)
    },
    setupRecipeTree ({ state, commit, dispatch }) {
      const numSelectedItems = state.selectedItems.length
      if (numSelectedItems === 0) {
        dispatch('updateRecipeTree', [])
        return
      }

      axios
        .post(`http://0.0.0.0:5000/api/${state.selectedVersion}/recipe_tree`, { items: state.selectedItems })
        .then(response => {
          commit('setRecipeTree', response.data)
          dispatch('setupShoppingList')
        })
    },
    setupShoppingList ({ state, commit }) {
      if (state.recipeTree.length === 0) {
        commit('setShoppingList', [])
        return
      }

      const recipeTreeCopy = state.recipeTree.slice(0)
      const recipePath = buildRecipePath(recipeTreeCopy)

      const haveAlready = {}
      const shoppingListItems = Object.keys(state.shoppingList)
      const numItems = shoppingListItems.length
      if (numItems > 0) {
        for (let i = 0; i < numItems; i += 1) {
          const itemName = shoppingListItems[i]
          const item = state.shoppingList[itemName]
          haveAlready[itemName] = item.have
        }
      }

      axios
        .post(`http://0.0.0.0:5000/api/${state.selectedVersion}/shopping_list`, {
          recipe_path: recipePath,
          have_already: haveAlready,
        })
        .then(response => {
          commit('setShoppingList', response.data)
        })
    },
    updateSelectedItems ({ commit, dispatch }, newItems) {
      commit('setSelectedItems', newItems)
      dispatch('setupRecipeTree')
    },
    updateRecipeTree ({ commit, dispatch }, newTree) {
      commit('setRecipeTree', newTree)
      dispatch('setupShoppingList')
    },
    updateShoppingList ({ commit, dispatch }, newList) {
      commit('setShoppingList', newList)
      dispatch('setupShoppingList')
    },
  },
  modules: {
  }
})
