<template>
  <Modal
    class="search"
    :modal-aria-label="modalAriaLabel">
    <header class="search__header">
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

    <div class="search__scroll-container">
      <div
        class="search__results"
        v-if="showItems && visibleAlpha.length > 0">
        <section
          class="search__results__section"
          v-for="letter in visibleAlpha"
          :key="letter">
          <a class="search__results__header" :id="letter">
            <h2>{{ letter }}</h2>
          </a>
          <ol
            class="search__results__items"
            v-for="itemKey in renderData[letter].order"
            :key="itemKey">
            <li class="search__results__row">
              <label class="checkbox" tabindex="0">
                <span class="search__results__input">
                  <input
                    class="checkbox__input"
                    type="checkbox"
                    name="checkbox"
                    :value="renderData[letter].items[itemKey].name"
                    v-model="tmpSelectedItems">
                  <check-icon v-once class="checkbox__checkmark" />
                </span>
                <span class="search__results__details">
                  <img
                    v-once
                    class="search__results__icon"
                    :src="getItemImage(renderData[letter].items[itemKey].name)" />

                  <span v-once class="search__results__name">
                    {{ getItemLabel(renderData[letter].items[itemKey].renderKey) }}
                    <span v-once v-if="renderData[letter].items[itemKey].alias">
                      ({{ getItemLabel(renderData[letter].items[itemKey].name, false) }})
                    </span>
                  </span>
                </span>
              </label>
            </li>
          </ol>
        </section>
      </div>

      <div
        class="search__content search__content--status"
        v-else-if="showItems && visibleAlpha.length === 0">
        No items found matching <span class="font-weight--medium">{{inputQuery}}</span>
      </div>

      <div
        class="search__content search__content--status"
        v-else>
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
import { ITEM_ALIASES, getItemImage, getItemLabel } from '@/helpers.js'
import Modal from '@/components/Modal.vue'
import searchIcon from '@/components/icons/search.vue'
import checkIcon from '@/components/icons/check.vue'

export default {
  name: 'CookbookBuildSearch',
  props: {
    query: String,
  },
  components: {
    Modal,
    searchIcon,
    checkIcon,
  },
  data () {
    const inputQuery = (typeof this.query === 'string' && this.query.length > 0) ? this.query : ''
    return {
      alpha: ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'],
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
      // if (
      //   typeof this.$store.state.gameData[this.$store.state.selectedVersion] === 'undefined' ||
      //   typeof this.$store.state.gameData[this.$store.state.selectedVersion].items === 'undefined'
      // ) {
      //   return []
      // }

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
      const alpha = Object.keys(this.renderData)
      alpha.sort()
      return alpha
    },
  },
  mounted () {
    this.$store.dispatch('initSearchStore')
    setTimeout(() => {
      this.showItems = true
    }, 0)
  },
  methods: {
    getItemImage,
    getItemLabel,
    getRenderDataByQuery (query) {
      // if (typeof this.renderDataByQuery[query] !== 'undefined') {
      //   return this.renderDataByQuery[query]
      // }

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

        if (!matching) {
          continue
        }

        if (typeof renderData[letter] === 'undefined') {
          renderData[letter] = {
            order: [],
            items: {},
          }
        }

        renderData[letter].order.push(renderKey)
        renderData[letter].items[renderKey] = {
          renderKey,
          name,
          alias,
          letter
        }

        renderData[letter].order.sort()
      }

      // this.renderDataByQuery[query] = renderData
      return renderData
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
  &__results__section,
  &__action-bar__inner,
  &__content--status {
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
    align-items: center;
    width: 100%;

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
    &__section {}

    &__header {
      display: flex;
      margin-top: 30px;
      align-items: center;
      font-size: 2.0em;
      color: #E6CE51;
      text-transform: uppercase;

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
