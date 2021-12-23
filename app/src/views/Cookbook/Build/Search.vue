<template>
  <Modal
    class="search"
    :modal-aria-label="modalAriaLabel">
    <header
      class="search__header"
      aria-label="Search Header">
      <div class="searchbox">
        <search-icon class="searchbox__icon" />
        <input
          class="searchbox__field"
          type="text"
          v-model="inputQuery"
          placeholder="What do you need?"
          v-on:keyup="onInputChange" />
      </div>
    </header>

    <RecycleScroller
      class="search__scroll-container"
      v-if="showItems && flatRenderData.length > 0"
      :items="flatRenderData"
      key-field="renderKey"
      v-slot="{ item }"
    >
      <div class="search__content">
        <a
          v-if="item.type === 'header'"
          class="search__results__header"
          :id="item.letter"
          :href="`#${item.letter}`">
          <h2>{{ item.letter }}</h2>
        </a>
        <div
          v-else-if="item.type === 'item'"
          class="search__results__row">
          <label
            class="checkbox"
            tabindex="0"
            @keyup.enter="handleItemToggle(item)"
            @keyup.space="handleItemToggle(item)"
            :aria-label="getItemLabel(item.renderKey)"
          >
            <span class="search__results__input">
              <input
                class="checkbox__input"
                type="checkbox"
                name="checkbox"
                :value="item.name"
                v-model="tmpSelectedItems">
              <check-icon class="checkbox__checkmark" />
            </span>
            <span class="search__results__details">
              <item-image
                :decorative="true"
                :item="item.name"
                :size="32"
                class="search__results__icon" />
              <span class="search__results__name">
                {{ getItemLabel(item.renderKey) }}
                <span v-if="item.alias">
                  ({{ getItemLabel(item.name, false) }})
                </span>
              </span>
            </span>
          </label>
        </div>
      </div>
    </RecycleScroller>

    <div class="search__scroll-container">
      <div
        class="search__content search__content--status"
        v-if="showItems && flatRenderData.length === 0">
        No items found matching <span class="font-weight--medium">{{inputQuery}}</span>
      </div>

      <div
        class="search__content search__content--status"
        v-else-if="!showItems">
        Loading Minecraft {{this.version}} Items...
      </div>
    </div>

    <section class="search__action-bar">
      <div class="search__action-bar__inner">
        <button
          class="button button--secondary"
          v-on:click="cancel"
          v-on:keyup.enter="cancel">
          Cancel
        </button>
        <button
          class="button button--primary"
          v-on:click="submit"
          v-on:keyup.enter="submit">
          Continue with {{numSelected}} items
        </button>
      </div>
    </section>
  </Modal>
</template>

<script>
import { ITEM_ALIASES, getItemLabel } from '@/helpers.js'
import Modal from '@/components/Modal.vue'
import ItemImage from '@/components/ItemImage.vue'
import checkIcon from '@/components/icons/check.vue'
import searchIcon from '@/components/icons/search.vue'

export default {
  name: 'CookbookBuildSearch',
  props: {
    query: String,
  },
  components: {
    Modal,
    ItemImage,
    checkIcon,
    searchIcon,
  },
  data () {
    const inputQuery = (typeof this.query === 'string' && this.query.length > 0) ? this.query : ''
    return {
      modalAriaLabel: 'Search Modal',
      inputQuery,
      renderDataByQuery: {},
      showItems: false,
    }
  },
  computed: {
    version () {
      return this.$store.state.selectedVersion
    },
    formattedInputQuery () {
      return this.inputQuery.toLowerCase().trim()
    },
    items () {
      return this.$store.state.gameData[this.version].items
    },
    tmpSelectedItems: {
      get () {
        return this.$store.state.tmpSelectedItems
      },
      set (newVal) {
        return this.$store.commit('setTmpSelectedItems', newVal)
      }
    },
    numSelected () {
      return (Array.isArray(this.tmpSelectedItems)) ? this.tmpSelectedItems.length : 0
    },
    renderData () {
      return this.getRenderDataByQuery(this.formattedInputQuery)
    },
    visibleAlpha () {
      const alpha = []
      for (const letter in this.renderData) {
        if (this.renderData[letter].hasMatches) {
          alpha.push(letter)
        }
      }

      alpha.sort()
      return alpha
    },
    flatRenderData () {
      const flattenedRenderData = []
      for (const letter of this.visibleAlpha) {
        if (!this.renderData[letter].hasMatches) {
          continue
        }

        flattenedRenderData.push({
          type: 'header',
          renderKey: `${letter}-header`,
          letter,
          size: 82,
        })

        for (const itemKey of this.renderData[letter].order) {
          if (!this.renderData[letter].items[itemKey].matching) {
            continue
          }

          const item = this.renderData[letter].items[itemKey]
          item.size = 52
          flattenedRenderData.push(item)
        }
      }

      return flattenedRenderData
    },
  },
  mounted () {
    this.$store.dispatch('initSearchStore')
    setTimeout(() => {
      this.showItems = true
    }, 3)
  },
  methods: {
    getItemLabel,
    getRenderDataByQuery (query) {
      if (typeof this.renderDataByQuery[query] !== 'undefined') {
        return this.renderDataByQuery[query]
      }

      const renderData = {}

      for (let i = 0, l = this.items.length; i < l; i += 1) {
        const name = this.items[i]
        const alias = ITEM_ALIASES[name]
        const renderKey = alias || name
        const letter = renderKey[0]
        const queryParts = query.split(/\s/)

        let matching = true
        for (let j = 0; j < queryParts.length; j += 1) {
          const nameMatches = name.includes(queryParts[j])
          const aliasMatches = (alias) ? alias.includes(queryParts[j]) : false
          const hasMatch = nameMatches || aliasMatches
          if (!hasMatch) {
            matching = false
            break
          }
        }

        // if (!matching) {
        //   continue
        // }

        if (typeof renderData[letter] === 'undefined') {
          renderData[letter] = {
            order: [],
            items: {},
            hasMatches: false,
          }
        }

        if (matching) {
          renderData[letter].hasMatches = true
        }

        renderData[letter].order.push(renderKey)
        renderData[letter].items[renderKey] = {
          type: 'item',
          renderKey,
          name,
          alias,
          letter,
          matching,
        }

        //  (!matching) {
        // //   continue
        // // }

        renderData[letter].order.sort()
      }

      this.renderDataByQuery[query] = renderData
      return renderData
    },
    handleItemToggle (item) {
      const index = this.tmpSelectedItems.indexOf(item.name)
      if (index < 0) {
        this.tmpSelectedItems.push(item.name)
      } else {
        this.tmpSelectedItems.splice(index, 1)
      }
    },
    onInputChange () {
      if (this.inputQuery === this.query) {
        return
      }

      this.$router.replace({
        path: this.$route.path,
        query: { q: this.inputQuery }
      })
    },
    submit () {
      this.$store.dispatch('setSelectedFromTmp', this.tmpSelectedItems)
      this.$router.push('/cookbook/build')
    },
    cancel () {
      this.tmpSelectedItems = null
      this.$router.push('/cookbook/build')
    }
  }
}
</script>

<style lang="scss">
.search {
  .modal__main {
    overflow: hidden;
  }

  .searchbox,
  &__action-bar__inner,
  &__content {
    width: 80%;
    max-width: 600px;
    margin: 0 auto;
  }

  &__header {
    z-index: 2;
    position: fixed;
    width: 100%;
    top: 0;
    left: 0;
    text-align: center;
    padding: 3.0em 0 0 0;
    background-image: linear-gradient(180deg, #FFFFFF 0%, rgba(255,255,255,0.00) 100%);
  }

  &__scroll-container {
    height: 100vh;
    padding: 100px 0 80px;
    overflow: auto;
  }

  &__content {
    display: flex;
    position: relative;
    flex-flow: column nowrap;

    &--status {
      display: block;
      text-align: center;
      font-size: 1.6em;
    }
  }

  &__action-bar {
    display: flex;
    flex-flow: row nowrap;
    align-items: center;
    justify-content: center;
    z-index: 2;
    position: fixed;
    width: 100%;
    bottom: 0;
    left: 0;
    text-align: center;
    background-image: linear-gradient(180deg, rgba(255,255,255,0.00) 0%, #FFFFFF 99%);

    &__inner {
      display: flex;
      flex-flow: row nowrap;
      align-items: center;
      justify-content: space-between;
    }
  }

  &__results {
    &__header {
      display: flex;
      margin-top: 30px;
      align-items: center;
      font-size: 2.0em;
      color: #005226;
      text-transform: uppercase;
      text-decoration: none;

      &.is-first {
        margin-top: 0;
      }
    }

    &__row {
      display: flex;
      margin: 1.0em 0;
      align-items: center;
    }

    &__input {
      margin-right: 1em;
    }

    &__details {
      display: flex;
      align-items: center;
    }

    &__icon {
      width: 32px;
      height: 32px;
      margin-right: 0.5em;
    }

    &__name {
      text-transform: capitalize;
    }
  }

  .checkbox {
    display: flex;
    flex-flow: row nowrap;
    font-size: 1.6em;
    align-items: center;
    width: 100%;
    cursor: pointer;

    &--disabled {
      color: pink;
    }

    &__checkmark .icon__check__path {
      stroke: #DBDCDD;
    }

    &__input {
      display: none;

      &:focus + .checkbox__checkmark {
        stroke: darken(#005226, 10)
      }

      &:checked + .checkbox__checkmark {
        .icon__check__path {
          stroke: #005226;
        }
      }

      &:disabled + .checkbox__checkmark {
        stroke: pink;
      }
    }
  }
}
</style>
