import Vue from 'vue'
import Vuex from 'vuex'
import VuexPersistence from 'vuex-persist'
import axios from 'axios'
import { clone, createBuildPaths } from '@/helpers.js'
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
      selectedBuildPaths: state.selectedBuildPaths,
      visibleBuildPath: state.visibleBuildPath,
      haveAlready: state.haveAlready,
    }
  }
})

const supportedVersions = [
  '1.15',
  '1.16'
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
    defaultRecipeTree: [],
    selectedBuildPaths: {},
    visibleBuildPath: [],
    shoppingList: {},
    defaultShoppingList: {},
    haveAlready: {},
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
    setSelectedVersion (state, version) {
      if (!state.supportedVersions.includes(version)) {
        state.selectedVersion = state.supportedVersions[0]
      } else {
        state.selectedVersion = version
      }
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
    setDefaultRecipeTree (state, tree) {
      state.defaultRecipeTree = tree
    },
    setVisibleBuildPath (state, visiblePath) {
      state.visibleBuildPath = visiblePath
    },
    setSelectedBuildPaths (state) {
      const buildPaths = createBuildPaths(state.recipeTree)
      state.selectedBuildPaths = clone(buildPaths)
    },
    setShoppingList (state, shoppingList) {
      state.shoppingList = shoppingList
    },
    setDefaultShoppingList (state, shoppingList) {
      state.defaultShoppingList = shoppingList
    },
    setHaveAlready (state) {
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

      state.haveAlready = haveAlready
    },
    setRequest (state, { requestName, cancelToken }) {
      const isLoading = cancelToken !== null
      const requestData = {
        isLoading,
        cancelToken
      }

      Vue.set(state.requests, requestName, requestData)
    },
    setIsLoading (state, { requestName, isLoading }) {
      const requestData = Object.assign({}, state.requests[requestName])
      requestData.isLoading = isLoading
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
          commit('setDefaultRecipeTree', [])
          commit('setRecipeTree', [])
          resolve()
          return
        }

        const hostname = window.location.hostname
        axios
          .post(
            `http://${hostname}:5000/api/${state.selectedVersion}/recipe_tree`,
            {
              items: state.selectedItems,
              selected_build_paths: state.selectedBuildPaths
            },
            { cancelToken: cancelToken.token }
          )
          .then(response => {
            commit('setRequest', { requestName, cancelToken: null })
            commit('setDefaultRecipeTree', clone(response.data))
            commit('setRecipeTree', response.data)
            commit('setSelectedBuildPaths')
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
          commit('setRequest', { requestName, cancelToken: null })
          commit('setDefaultShoppingList', [])
          commit('setShoppingList', [])
          commit('setHaveAlready')
          resolve()
          return
        }

        const hostname = window.location.hostname
        axios
          .post(
            `http://${hostname}:5000/api/${state.selectedVersion}/shopping_list`,
            {
              recipe_path: state.selectedBuildPaths,
              have_already: state.haveAlready,
            },
            { cancelToken: cancelToken.token }
          )
          .then(response => {
            commit('setRequest', { requestName, cancelToken: null })
            commit('setDefaultShoppingList', clone(response.data))
            commit('setShoppingList', response.data)
            commit('setHaveAlready')
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
      const selectedItems = clone(state.selectedItems)
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
      const numPrevItems = state.selectedItems.length
      const numNewItems = newItems.length

      let fetchTree = numPrevItems !== numNewItems

      if (!fetchTree) {
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
      commit('setSelectedBuildPaths')
      return dispatch('fetchShoppingList')
    },
    resetRecipeTree ({ commit, dispatch, state }) {
      return new Promise((resolve, reject) => {
        const origTree = clone(state.defaultRecipeTree)
        commit('setRecipeTree', origTree)
        commit('setVisibleBuildPath', [])
        commit('setSelectedBuildPaths')
        dispatch('fetchShoppingList')
        resolve()
      })
    },
    updateShoppingList ({ commit, dispatch }, newList) {
      commit('setShoppingList', newList)
      commit('setHaveAlready')
      return dispatch('fetchShoppingList')
    },
    resetShoppingList ({ commit, dispatch, state }) {
      return new Promise((resolve, reject) => {
        const origList = clone(state.defaultShoppingList)
        commit('setShoppingList', origList)
        commit('setHaveAlready')
        dispatch('fetchShoppingList')
        resolve()
      })
    },
    updateVisibleBuildPath ({ commit }, newPath) {
      commit('setVisibleBuildPath', newPath)
    },
    updateSelectedVersion ({ state, commit, dispatch }, version) {
      commit('setSelectedVersion', version)
      dispatch('init')
    },
  },
  modules: {
  }
})
