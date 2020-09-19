<template>
  <div class="cookbook-build">
    <select class="cookbook-build__version">
      <option>v1.15.2</option>
    </select>

    <div class="cookbook-build__menu">
      <div class="searchbox">
        <search-icon class="searchbox__icon" />
        <input
          class="searchbox__field"
          type="text"
          v-model="searchTerm"
          placeholder="What do you need?"
          v-on:click="goToSearch"
          v-on:keyup.enter="goToSearch" />
      </div>

      <router-link
        class="cookbook-build__menu__btn"
        to="/cookbook/build/freeform">
        <plaintext-input-icon />
      </router-link>
    </div>

    <div v-if="hasSelectedItems">
      <button v-on:click="removeAllItems()">clear all</button>
      <div
        class="item-row"
        v-for="(item, i) in selectedItems"
        :key="item.key">
        <input type="number" min="0" v-model.number="selectedItems[i].amount_required" />
        <img :src="getItemImage(item.key)" />
        {{item.key}}
        <a :href="`https://minecraft.gamepedia.com/${item.name}`" target="_blank">Minecraft Wiki</a>
        <button v-on:click="removeSelectedItem(i)">x</button>
      </div>
    </div>
    <div v-else class="cookbook-build__empty">
      <blob />
      <p class="font-weight--medium">Search for something to create</p>
      <p>or</p>
      <a class="rand-link" v-on:click="selectRandomItem()">Randomly Pick an Item</a>
    </div>

    <!-- Router view for modals -->
    <router-view></router-view>
  </div>
</template>

<script>
import blob from '../../../components/blob.vue'
import searchIcon from '../../../components/icons/search.vue'
import plaintextInputIcon from '../../../components/icons/plaintext-input.vue'

export default {
  name: 'CookbookBuild',
  components: {
    blob,
    searchIcon,
    plaintextInputIcon,
  },
  data () {
    return {
      searchTerm: null
    }
  },
  computed: {
    items () {
      if (
        typeof this.$store.state.gameData[this.$store.state.selectedVersion] === 'undefined' ||
        typeof this.$store.state.gameData[this.$store.state.selectedVersion].items === 'undefined'
      ) {
        return []
      }

      return this.$store.state.gameData[this.$store.state.selectedVersion].items
    },
    selectedItems () {
      return this.$store.state.selectedItems
    },
    hasSelectedItems () {
      return this.selectedItems.length > 0
    },
  },
  watch: {
    selectedItems: {
      deep: true,
      handler (newVal) {
        this.$store.commit('setSelectedItems', newVal)
        this.$store.dispatch('setupRecipeTree')
      }
    }
  },
  methods: {
    getItemImage (item) {
      const images = require.context('../../../assets/minecraft/1.15/32x32/', false, /\.png$/)
      try {
        return images(`./${item}.png`)
      } catch (error) {
        return images('./air.png')
      }
    },
    removeAllItems () {
      this.selectedItems.splice(0, this.selectedItems.length)
    },
    removeSelectedItem (i) {
      this.selectedItems.splice(i, 1)
    },
    selectRandomItem () {
      const len = this.items.length
      const randIdx = Math.floor(Math.random() * Math.floor(len))
      const item = this.items[randIdx]
      this.$store.dispatch('setSelectedFromTmp', [item])
    },
    goToSearch () {
      const q = this.searchTerm
      this.searchTerm = null

      let query = {}
      if (typeof q === 'string' && q.length > 0) {
        query = { q }
      }

      this.$router.push({ path: '/cookbook/build/search', query })
    }
  }
}
</script>

<style lang="scss" scoped>
.cookbook-build {
  display: flex;
  flex-flow: column nowrap;
  width: 80%;
  max-width: 60.0em;
  min-height: calc(100vh - 6.4em - 6.4em);

  &__version {
    margin-top: 0.5em;
    align-self: center;
    padding: 0.4em;
    font-size: 1.2em;
    background: #F1F1F1;
    border: 1px solid #E9E9E9;
    border-radius: 1.4em;
  }

  .searchbox {
    display: flex;
    flex-flow: row nowrap;
    align-items: center;
    height: 4.0em;
    padding: 0 1.0em;
    border-radius: 2.4em;
    border: 1px solid #F5E0BE;
    background: #F5EDE1;

    &__field {
      border: 0;
      padding: 0;
      margin: 0 0 0 0.5em;
      background: transparent;
      height: 100%;
      width: 100%;
    }
  }

  &__menu {
    display: flex;
    margin-top: 3.0em;
    flex-flow: row nowrap;
    align-items: center;

    &__btn {
      display: flex;
      width: 4.0em;
      height: 4.0em;
      align-items: center;
      justify-content: center;
      border: 1px solid #DBDCDD;
      background: #F1F1F1;
      border-radius: 50%;

      &:hover {
        background: darken(#F1F1F1, 10);
        border: 1px solid darken(#DBDCDD, 10);
      }
    }

    .searchbox {
      flex: 2 0 auto;
      margin-right: 1.0em;
    }
  }

  &__empty {
    flex: 3 0 auto;
    align-self: center;
    justify-self: center;

    display: flex;
    position: relative;
    flex-flow: column nowrap;
    align-items: center;
    justify-content: center;
    margin-top: 2.0em;
    height: 100%;
    width: 100%;
    max-width: 34.0em;
    overflow: hidden;

    font-size: 1.8em;

    .blob {
      position: absolute;
      z-index: -1;
    }

    .rand-link {
      cursor: pointer;
      color: rgba(12, 136, 68, 1);
      font-weight: 500;

      &:hover {
        text-decoration: underline;
      }
    }
  }
}
</style>
