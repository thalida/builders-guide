import Vue from 'vue'
import Vuex from 'vuex'
import VuexPersistence from 'vuex-persist'
import axios from 'axios'
const CancelToken = axios.CancelToken

Vue.use(Vuex)

const vuexLocal = new VuexPersistence({
  key: 'bg-vuex',
  storage: window.localStorage,
  reducer (state) {
    return {
      selectedVersion: state.selectedVersion,
      skipSplash: state.skipSplash,
      selectedItems: state.selectedItems,
      tmpSelectedItems: state.tmpSelectedItems,
      shoppingList: {},
      selectedBuildPaths: [],
    }
  }
})

const supportedVersions = [
  '1.15'
]

const createBuildPaths = (recipeTree, isGroup) => {
  const path = []

  for (let i = 0, l = recipeTree.length; i < l; i += 1) {
    const node = recipeTree[i]

    if (Array.isArray(node)) {
      const chosenNode = createBuildPaths(node.slice(0), true)
      path.push(chosenNode[0])
      continue
    }

    if (!node.selected) {
      continue
    }

    const nodeCopy = Object.assign({}, node)

    if (nodeCopy.num_recipes >= 1) {
      nodeCopy.recipes = createBuildPaths(nodeCopy.recipes, true)
    } else if (nodeCopy.ingredients && nodeCopy.ingredients.length > 0) {
      nodeCopy.ingredients = createBuildPaths(nodeCopy.ingredients)
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
    selectedBuildPaths: [],
    shoppingList: {},
    requests: {
      fetchItems: {
        cancelToken: null,
        isLoading: false
      },
      fetchRecipeTree: {
        cancelToken: null,
        isLoading: false
      },
      fetchShoppingList: {
        cancelToken: null,
        isLoading: false
      },
    }
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
    setSelectedBuildPaths (state, buildPaths) {
      state.selectedBuildPaths = buildPaths
    },
    setShoppingList (state, shoppingList) {
      state.shoppingList = shoppingList
    },
    setRequest (state, { requestName, cancelToken }) {
      const isLoading = cancelToken !== null
      const requestData = {
        isLoading,
        cancelToken
      }

      Vue.set(state.requests, requestName, requestData)
    }
  },
  actions: {
    init ({ state, dispatch }) {
      const fetchItemsPromise = dispatch('fetchItems')
      dispatch('fetchRecipeTree')
        .then(() => dispatch('fetchShoppingList'))

      return fetchItemsPromise
    },
    fetchItems ({ state, commit }) {
      const requestName = 'fetchItems'
      const request = state.requests[requestName]

      if (request.isLoading) {
        request.cancelToken.cancel()
      }

      const cancelToken = CancelToken.source()
      commit('setRequest', { requestName, cancelToken })

      const hostname = window.location.hostname
      return new Promise((resolve, reject) => {
        if (
          typeof state.gameData[state.selectedVersion] === 'undefined' ||
          typeof state.gameData[state.selectedVersion].items === 'undefined' ||
          typeof state.gameData[state.selectedVersion].items[0] === 'undefined'
        ) {
          axios
            .get(
              `http://${hostname}:5000/api/${state.selectedVersion}/items`,
              { cancelToken: cancelToken.token }
            )
            .then(response => {
              commit('setRequest', { requestName, cancelToken: null })
              commit('setItems', response.data)
              resolve()
            })
            .catch((err) => {
              commit('setRequest', { requestName, cancelToken: null })
              reject(err)
            })
        } else {
          commit('setRequest', { requestName, cancelToken: null })
          resolve()
        }
      })
    },
    fetchRecipeTree ({ state, commit, dispatch }) {
      const requestName = 'fetchRecipeTree'
      const request = state.requests[requestName]

      if (request.isLoading) {
        request.cancelToken.cancel()
      }

      const cancelToken = CancelToken.source()
      commit('setRequest', { requestName, cancelToken })

      return new Promise((resolve, reject) => {
        const numSelectedItems = state.selectedItems.length
        if (numSelectedItems === 0) {
          commit('setRequest', { requestName, cancelToken: null })
          commit('setRecipeTree', [])
          resolve()
          return
        }

        const hostname = window.location.hostname
        axios
          .post(
            `http://${hostname}:5000/api/${state.selectedVersion}/recipe_tree`,
            { items: state.selectedItems },
            { cancelToken: cancelToken.token }
          )
          .then(response => {
            commit('setRequest', { requestName, cancelToken: null })

            const tree = response.data
            commit('setRecipeTree', tree)

            const buildPaths = createBuildPaths(state.recipeTree.slice(0))
            commit('setSelectedBuildPaths', buildPaths)
            resolve()
          })
          .catch((err) => {
            commit('setRequest', { requestName, cancelToken: null })
            reject(err)
          })
      })
    },
    fetchShoppingList ({ state, commit, dispatch }) {
      const requestName = 'fetchShoppingList'
      const request = state.requests[requestName]

      if (request.isLoading) {
        request.cancelToken.cancel()
      }

      const cancelToken = CancelToken.source()
      commit('setRequest', { requestName, cancelToken })

      return new Promise((resolve, reject) => {
        if (state.recipeTree.length === 0) {
          commit('setShoppingList', [])
          commit('setRequest', { requestName, cancelToken: null })
          resolve()
          return
        }

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

        const hostname = window.location.hostname
        axios
          .post(
            `http://${hostname}:5000/api/${state.selectedVersion}/shopping_list`,
            {
              recipe_path: state.selectedBuildPaths,
              have_already: haveAlready,
            },
            { cancelToken: cancelToken.token }
          )
          .then(response => {
            commit('setShoppingList', response.data)
            commit('setRequest', { requestName, cancelToken: null })
            resolve()
          })
          .catch((err) => {
            commit('setRequest', { requestName, cancelToken: null })
            reject(err)
          })
      })
    },
    initSearchStore ({ state, commit, dispatch }) {
      if (state.tmpSelectedItems !== null) {
        return
      }

      const selectedItemNames = []
      for (let i = 0, l = state.selectedItems.length; i < l; i += 1) {
        selectedItemNames.push(state.selectedItems[i].key)
      }
      commit('setTmpSelectedItems', selectedItemNames)
    },
    setSelectedFromTmp ({ state, commit, dispatch, getters }, tmpItems) {
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

      dispatch('updateSelectedItems', selectedItems)
      commit('setTmpSelectedItems', null)
    },
    mergeSelectedItems ({ state, commit, dispatch, getters }, items) {
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

      dispatch('updateSelectedItems', selectedItems)
    },
    updateSelectedItems ({ commit, dispatch, state }, newItems) {
      let fetchTree = false
      const numPrevItems = state.selectedItems.length
      const numNewItems = newItems.length
      if (numPrevItems !== numNewItems) {
        fetchTree = true
      } else {
        for (let i = 0; i < numNewItems; i += 1) {
          const newItem = newItems[i].key
          const origItem = state.selectedItems[i].key

          if (newItem !== origItem) {
            fetchTree = true
            break
          }
        }
      }
      commit('setSelectedItems', newItems)

      if (fetchTree) {
        return dispatch('fetchRecipeTree')
          .then(() => dispatch('fetchShoppingList'))
      }

      return dispatch('fetchShoppingList')
    },
    updateRecipeTree ({ commit, dispatch, state }, newTree) {
      commit('setRecipeTree', newTree)

      const buildPaths = createBuildPaths(state.recipeTree.slice(0))
      commit('setSelectedBuildPaths', buildPaths)

      return dispatch('fetchShoppingList')
    },
    updateShoppingList ({ commit, dispatch }, newList) {
      commit('setShoppingList', newList)
      return dispatch('fetchShoppingList')
    },
  },
  modules: {
  }
})
