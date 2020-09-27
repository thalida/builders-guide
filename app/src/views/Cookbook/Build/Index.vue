<template>
  <div
    class="cookbook-build"
    :class="[{
      'cookbook-build--is-empty': !hasSelectedItems
    }]">
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

    <div v-if="hasSelectedItems" class="cookbook-build__content">
      <div
        class="cookbook-build__item-group"
        v-for="(item, i) in selectedItems"
        :key="item.key">
        <input
          class="cookbook-build__item-group__input"
          type="number"
          min="0"
          v-model.number="selectedItems[i].amount_required" />
        <img class="cookbook-build__item-group__icon" :src="getItemImage(item.key)" />
        <div class="cookbook-build__item-group__text">
          <span class="item-title">{{getTitle(item.key)}}</span>
          <a class="link" :href="`https://minecraft.gamepedia.com/${item.name}`" target="_blank">Minecraft Wiki</a>
        </div>
        <button
          class="cookbook-build__item-group__remove-btn"
          v-on:click="removeSelectedItem(i)">
          <cross-icon />
        </button>
      </div>

      <div class="cookbook-build__content-actions">
        <a
          class="link"
          tabindex="0"
          v-on:click="removeAllItems()"
          v-on:keyup.enter="removeAllItems()">
          Clear All
        </a>
      </div>
    </div>

    <div v-else class="cookbook-build__empty">
      <blob />
      <p class="font-weight--medium">Search for something to create</p>
      <p>or</p>
      <a
        class="link"
        tabindex="0"
        v-on:click="selectRandomItem()"
        v-on:keyup.enter="selectRandomItem()">
        Randomly Pick an Item
      </a>
    </div>

    <!-- Router view for modals -->
    <router-view></router-view>
  </div>
</template>

<script>
import debounce from 'lodash.debounce'
import blob from '@/components/blob.vue'
import searchIcon from '@/components/icons/search.vue'
import plaintextInputIcon from '@/components/icons/plaintext-input.vue'
import crossIcon from '@/components/icons/cross.vue'

export default {
  name: 'CookbookBuild',
  components: {
    blob,
    searchIcon,
    plaintextInputIcon,
    crossIcon,
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
        this.debouncedUpdateSelected(newVal)
      }
    }
  },
  created () {
    this.debouncedUpdateSelected = debounce(this.updateSelectedItems, 300)
  },
  methods: {
    updateSelectedItems (items) {
      this.$store.commit('setSelectedItems', items)
      this.$store.dispatch('setupRecipeTree')
    },
    getTitle (item) {
      return item.split('_').join(' ')
    },
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

<style lang="scss">
.cookbook-build {
  display: flex;
  flex-flow: column nowrap;
  width: 80%;
  max-width: 600px;

  &--is-empty {
    min-height: calc(100vh - 6.4em - 6.4em);
  }

  &__version {
    margin-top: 0.5em;
    align-self: center;
    padding: 0.4em;
    font-size: 1.2em;
    background: #F1F1F1;
    border: 1px solid #E9E9E9;
    border-radius: 1.4em;
  }

  &__menu {
    display: flex;
    margin-top: 3.0em;
    flex-flow: row nowrap;
    align-items: center;

    &__btn {
      flex: 0 0 4.0em;
      display: flex;
      width: 4.0em;
      height: 4.0em;
      align-items: center;
      justify-content: center;
      border: 1px solid #DBDCDD;
      background: #F1F1F1;
      border-radius: 50%;
      transition: background 300ms;

      &:hover,
      &:focus {
        background: darken(#F1F1F1, 10);
        border: 1px solid darken(#DBDCDD, 10);
      }
    }

    .searchbox {
      flex: 2 1 auto;
      margin-right: 1.0em;
    }
  }

  &__content {
    padding-bottom: 3.6em;
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
    text-align: center;
    line-height: 1.4;
    font-size: 1.8em;

    .blob {
      position: absolute;
      z-index: -1;
      width: 100%;
      max-width: 340px;
    }

    .link {
      font-size: 1.0em;
    }
  }

  &__item-group {
    display: flex;
    position: relative;
    width: 100%;
    margin: 2.0em 0;
    flex-flow: row nowrap;
    justify-content: space-between;

    &__input {
      width: 32px;
      height: 32px;
      padding: 0;
      border: 0;
      border-bottom: 1px solid #918C88;
      text-align: center;
      font-size: 1.6em;
      font-weight: 500;
    }

    &__icon {
      flex: 0 1 32px;
      height: 32px;
      width: 32px;
      margin: 0 1.0em;
    }

    &__text {
      flex: 2 0 auto;
      display: flex;
      flex-flow: column wrap;
      margin: 0 1.0em 0 0;
      width: calc(80% - 96px);

      .item-title {
        line-height: 1.6;
      }

      .link {
        width: fit-content;
      }
    }

    &__remove-btn {
      cursor: pointer;
      flex: 0 1 3.2px;
      height: 32px;
      width: 32px;
      padding: 0;
      margin: 0 0.8em 0 0;
      border: 0;
      background: transparent;

      &:hover,
      &:focus {
        .icon__cross__path {
          fill: #1D1007;
        }
      }
    }
  }

  &__content-actions {
    position: fixed;
    display: flex;
    width: 100%;
    height: 3.4em;
    left: 0;
    bottom: 6.4em;
    justify-content: center;
    align-items: center;

    background: #F1F1F1;
  }
}
</style>
