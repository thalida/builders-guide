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
      <div v-if="showItems">
        <ol class="search__content" v-if="renderData.length > 0">
          <li
            class="search__content__row"
            v-for="(item, index) in renderData"
            :key="item.name">

            <a
              v-if="item.type === 'header'"
              class="search__letter-row"
              :class="[{ 'is-first': index===0 }]"
              :id="item.letter">
              <h2>{{ item.letter }}</h2>
            </a>

            <div
              v-if="item.type === 'item'"
              class="search__item-row">
              <label class="checkbox" tabindex="0">
                <span class="search__item-row__input">
                  <input
                    class="checkbox__input"
                    type="checkbox"
                    name="checkbox"
                    :value="item.name"
                    v-model="tmpSelectedItems">
                  <check-icon v-once class="checkbox__checkmark" />
                </span>
                <span class="search__item-row__details">
                  <img
                    v-once
                    class="search__item-row__icon"
                    :src="getItemImage(item.name)" />
                  <span v-once class="search__item-row__name">
                    {{ getTitle(item.name) }}
                  </span>
                </span>
              </label>
            </div>
          </li>
        </ol>
        <div class="search__content search__content--status" v-else>
          No items found matching <span class="font-weight--medium">{{inputQuery}}</span>
        </div>
      </div>
      <div class="search__content search__content--status" v-else>
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
      if (
        typeof this.$store.state.gameData[this.$store.state.selectedVersion] === 'undefined' ||
        typeof this.$store.state.gameData[this.$store.state.selectedVersion].items === 'undefined'
      ) {
        return []
      }

      return this.$store.state.gameData[this.$store.state.selectedVersion].items
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
  },
  mounted () {
    this.$store.dispatch('setupSearchStore')
    setTimeout(() => {
      this.showItems = true
    }, 0)
  },
  methods: {
    getRenderDataByQuery (query) {
      // if (typeof this.renderDataByQuery[query] !== 'undefined') {
      //   return this.renderDataByQuery[query]
      // }

      const renderData = []
      const foundLetters = {}

      for (let i = 0, l = this.items.length; i < l; i += 1) {
        const name = this.items[i]
        const letter = name[0]
        const queryParts = query.split(/\s/)
        let matching = true

        for (let j = 0; j < queryParts.length; j += 1) {
          if (!name.includes(queryParts[j])) {
            matching = false
            break
          }
        }

        if (!matching) {
          continue
        }

        if (typeof foundLetters[letter] === 'undefined') {
          renderData.push({
            id: letter,
            letter,
            type: 'header',
            size: 35,
          })
          foundLetters[letter] = true
        }

        renderData.push({
          id: name,
          name,
          letter,
          type: 'item',
          size: 40,
        })
      }

      // this.renderDataByQuery[query] = renderData
      return renderData
    },
    getItemImage (item) {
      const images = require.context('../../../assets/minecraft/1.15/32x32/', false, /\.png$/)
      try {
        return images(`./${item}.png`)
      } catch (error) {
        return images('./air.png')
      }
    },
    getTitle (item) {
      return item.split('_').join(' ')
    },
    onScroll () {
      if (this.navi.fromUserClick && !this.navi.arrivedAtLetter) {
        return
      }
      this.navi.fromUserClick = false
      this.navi.arrivedAtLetter = false
    },
    onLetterClick (letter) {
      this.navi.selected = letter
      this.navi.fromUserClick = true
      this.navi.arrivedAtLetter = this.focusedLetterInView === letter
    },
    onVisibilityChanged (isVisible, e) {
      const elem = e.target
      const letter = elem.dataset.letter

      if (isVisible || letter in this.navi.inViewport) {
        let count = this.navi.inViewport[letter] || 0

        if (isVisible) {
          count += 1
        } else {
          count -= 1
        }

        if (count > 0) {
          this.$set(this.navi.inViewport, letter, count)
        } else {
          this.$delete(this.navi.inViewport, letter)
        }
      }

      if (this.navi.fromUserClick) {
        this.navi.arrivedAtLetter = (
          letter === this.navi.selected || letter in this.navi.inViewport
        )
        return
      }

      this.navi.selected = this.focusedLetterInView
      this.navi.fromUserClick = false
      this.navi.arrivedAtLetter = true
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
  &__content__row,
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

  &__letter-row {
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

  &__item-row {
    display: flex;
    margin: 1.0em 0;
    align-items: center;

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
