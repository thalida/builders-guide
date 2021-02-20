<template>
  <div
    class="cookbook-build"
    :class="[{
      'cookbook-build--is-empty': !hasSelectedItems
    }]">

    <label class="cookbook-build__version">
      <select
        class="cookbook-build__version__select"
        v-model="selectedVersion">
        <option
          v-for="version in supportedVersions"
          :key="version"
          :value="version">
          Version {{ version }}
        </option>
      </select>
    </label>

    <div class="cookbook-build__menu">
      <label class="searchbox">
        <search-icon class="searchbox__icon" />
        <input
          class="searchbox__field"
          type="text"
          v-model="searchTerm"
          placeholder="What do you need?"
          @click="goToSearch"
          @keyup.enter="goToSearch" />
      </label>

      <router-link
        class="cookbook-build__menu__btn"
        to="/cookbook/build/freeform">
        <plaintext-input-icon alt="Freeform Input" />
      </router-link>
    </div>

    <div v-if="!hasSelectedItems" class="cookbook-build__empty">
      <blob />
      <p class="font-weight--medium">Search for something to create</p>
      <p>or</p>
      <a
        class="link"
        tabindex="0"
        @click="selectRandomItems()"
        @keyup.enter="selectRandomItems()">
        Randomly Select Items
      </a>
      <p v-if="isDebugMode">or</p>
      <a
        v-if="isDebugMode"
        class="link"
        tabindex="0"
        @click="selectAllItems()"
        @keyup.enter="selectAllItems()">
        Break the site
      </a>
    </div>

    <div v-if="hasSelectedItems" class="cookbook-build__content">
      <div
        class="cookbook-build__item-group"
        v-for="(item, i) in selectedItems"
        :key="item.key">
        <input
          v-if="!item.incompatible"
          class="cookbook-build__item-group__input"
          :id="`item-amount-input--${item.key}`"
          type="number"
          min="0"
          v-model.number="selectedItems[i].amount_required"
          @change="updateAmountRequired(i, $event)" />

        <item-image
          v-if="!item.incompatible"
          :item="(item.tag) ? recipeTree[i] : item"
          :size="32"
          class="cookbook-build__item-group__icon" />

        <div class="cookbook-build__item-group__text">
          <label
            v-once
            :for="`item-amount-input--${item.key}`"
            class="item-title">
            {{ getItemLabel(item) }}
          </label>
          <span class="item-subtext">
            <span
              v-if="item.incompatible"
              class="item-warning">
              Item unavailable in Minecraft {{selectedVersion}}
            </span>
            <a
              v-once
              class="link"
              :href="`https://minecraft.gamepedia.com/${item.name}`"
              target="_blank">
              Minecraft Wiki
            </a>
          </span>
        </div>
        <button
          class="cookbook-build__item-group__remove-btn"
          aria-label="Remove Item"
          @click="removeSelectedItem(i)">
          <cross-icon />
        </button>
      </div>
    </div>

    <div v-if="hasSelectedItems" class="cookbook-build__actions">
      <a
        class="link"
        tabindex="0"
        @click="removeAllItems()"
        @keyup.enter="removeAllItems()">
        Remove all items
      </a>
    </div>

    <!-- Router view for modals -->
    <router-view></router-view>
  </div>
</template>

<script>
import debounce from 'lodash.debounce'
import { getItemLabel } from '@/helpers.js'
import blob from '@/components/blob.vue'
import searchIcon from '@/components/icons/search.vue'
import plaintextInputIcon from '@/components/icons/plaintext-input.vue'
import crossIcon from '@/components/icons/cross.vue'
import ItemImage from '@/components/ItemImage.vue'

export default {
  name: 'CookbookBuild',
  components: {
    blob,
    ItemImage,
    searchIcon,
    plaintextInputIcon,
    crossIcon,
  },
  data () {
    const isDevelopment = process.env.NODE_ENV === 'development'
    const enableDebug = true
    return {
      isDebugMode: enableDebug && isDevelopment,
      searchTerm: null
    }
  },
  computed: {
    items () {
      return this.$store.state.gameData[this.$store.state.selectedVersion].items
    },
    selectedVersion: {
      get () {
        return this.$store.state.selectedVersion
      },
      set (version) {
        this.$store.dispatch('updateSelectedVersion', version)
      }
    },
    supportedVersions () {
      return this.$store.state.supportedVersions
    },
    selectedItems () {
      return this.$store.state.selectedItems
    },
    recipeTree () {
      return this.$store.state.recipeTree
    },
    hasSelectedItems () {
      return this.selectedItems.length > 0
    },
  },
  created () {
    this.debouncedUpdateSelected = debounce(this.updateSelectedItems, 300)
  },
  methods: {
    getItemLabel,
    updateSelectedItems (items) {
      this.$store.dispatch('updateSelectedItems', items)
    },
    removeAllItems () {
      const itemsCopy = this.selectedItems.slice(0)
      itemsCopy.splice(0, itemsCopy.length)
      this.updateSelectedItems(itemsCopy)
    },
    removeSelectedItem (i) {
      const itemsCopy = this.selectedItems.slice(0)
      itemsCopy.splice(i, 1)
      this.updateSelectedItems(itemsCopy)
    },
    updateAmountRequired (i, event) {
      const itemsCopy = this.selectedItems.slice(0)
      this.debouncedUpdateSelected(itemsCopy)
    },
    selectAllItems () {
      this.$store.dispatch('setSelectedFromTmp', this.items.slice(0))
    },
    selectRandomItems () {
      const minItems = 3
      const maxItems = 7
      const numItems = Math.floor(Math.random() * (maxItems - minItems + 1) + minItems)
      const items = this.items.slice(0)
      const tmpSelectedItems = []

      for (let i = 0; i < numItems; i += 1) {
        const randItem = this.selectRandomItem(items)
        tmpSelectedItems.push(randItem.item)
        items.splice(randItem.index, 1)
      }

      this.$store.dispatch('setSelectedFromTmp', tmpSelectedItems)
    },
    selectRandomItem (items) {
      const len = items.length
      const randIdx = Math.floor(Math.random() * Math.floor(len))
      const item = items[randIdx]

      return { index: randIdx, item }
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

  &--is-empty {
    min-height: calc(100vh - 6.4em - 6.4em);
  }

  &__version {
    margin-top: 0.5em;
    align-self: center;

    &__select {
      padding: 0.4em;
      font-size: 1.2em;
      background: #F1F1F1;
      border: 1px solid #E9E9E9;
      border-radius: 1.4em;
    }
  }

  &__menu {
    display: flex;
    flex-flow: row nowrap;
    align-items: center;
    margin: 3.0em auto 0;
    width: 80%;
    max-width: 600px;

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
    margin: 0 auto;
    width: 100%;
    flex: 1;
    overflow: auto;
  }

  &__empty {
    align-self: center;
    justify-self: center;

    display: flex;
    position: relative;
    flex-flow: column nowrap;
    align-items: center;
    justify-content: center;
    height: 100%;
    width: 100%;
    min-height: 400px;
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
    width: 80%;
    max-width: 600px;
    margin: 2.0em auto;
    flex-flow: row nowrap;
    justify-content: space-between;

    &__input {
      width: 64px;
      height: 32px;
      padding: 0;
      border: 0;
      border-bottom: 1px solid #918C88;
      text-align: right;
      font-size: 1.6em;
      font-weight: 500;
    }

    &__icon {
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

      .item-warning {
        margin-right: 5px;
        font-size: 1.4em;
        color: #d45953;
        font-weight: 700;
      }

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

  &__actions {
    display: flex;
    width: 100%;
    height: 3.4em;
    justify-content: center;
    align-items: center;
    background: #F1F1F1;
  }
}
</style>
