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
    selectedVersion: supportedVersions[0],
    supportedVersions,
    skipSplash: false,
    selectedItems: [],
    tmpSelectedItems: null,
    gameData: {}
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
        commit('setTmpSelectedItems', state.selectedItems)
      }
    }
  },
  modules: {
  }
})
