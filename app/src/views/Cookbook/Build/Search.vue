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
        <ol class="search__content" v-if="renderData.hasItems">
          <li
            class="search__content__row"
            v-for="(item, index) in renderData.items"
            v-observe-visibility="{
              callback: onVisibilityChanged,
              intersection: navi.intersectionOptions,
            }"
            :key="item.name"
            :data-letter="item.letter">

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
                  <check-icon class="checkbox__checkmark" />
                </span>
                <span class="search__item-row__details">
                  <img
                    class="search__item-row__icon"
                    :src="getItemImage(item.name)" />
                  <span class="search__item-row__name">
                    <span
                      v-for="(stringPart, spi) in getItemNameParts(item.name)"
                      :key="spi"
                      :class="[{
                        'font-weight--bold': stringPart.isBold
                      }]">{{stringPart.value}}</span>
                    </span>
                  </span>
              </label>
            </div>
          </li>
        </ol>
        <div class="search__content" v-else>
          No results
        </div>
      </div>
      <div class="search__content" v-else>
        loading...
      </div>
    </div>

    <ol class="search__alpha">
       <li
         v-for="letter in navi.alpha"
         :key="letter">
         <a
           v-if="renderData.letters[letter]"
           :href="`#${letter}`"
           :class="{'is-selected': navi.selected === letter}"
           v-on:click="onLetterClick(letter)"
           v-on:keyup.enter="onLetterClick(letter)">
           {{letter}}
         </a>
         <span v-else>{{letter}}</span>
       </li>
   </ol>

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
import 'intersection-observer'
import Modal from '@/components/Modal.vue'
import searchIcon from '../../../components/icons/search.vue'
import checkIcon from '../../../components/icons/check.vue'

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
    const alpha = 'abcdefghijklmnopqrstuvwxyz'.split('')
    const inputQuery = (typeof this.query === 'string' && this.query.length > 0) ? this.query : ''
    return {
      $scrollContainer: null,
      modalAriaLabel: 'Search Modal',
      inputQuery,
      renderDataByQuery: {},
      showItems: false,
      navi: {
        show: false,
        alpha,
        inViewport: {},
        selected: null,
        fromUserClick: false,
        arrivedAtLetter: false,
        // https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API
        intersectionOptions: {
          root: null,
          rootMargin: '0px 0px 0px 0px',
          threshold: 0,
        },
      },
    }
  },
  computed: {
    formattedInputQuery () {
      return this.inputQuery.toLowerCase()
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
      return this.getRenderDataByQuery(this.inputQuery)
    },
    focusedLetterInView () {
      const letters = Object.keys(this.navi.inViewport)

      if (letters.length === 0) {
        return null
      }

      letters.sort()
      const focusedLetter = letters[0]

      if (this.$route.hash.indexOf(focusedLetter) < 0) {
        this.$router.replace({
          path: this.$route.path,
          query: { q: this.inputQuery },
          hash: focusedLetter
        })
      }

      return focusedLetter
    },
  },
  mounted () {
    this.$scrollContainer = this.$el.querySelector('.search__scroll-container')
    this.$store.dispatch('setupSearchStore')
    this.navi.intersectionOptions.root = this.$scrollContainer
    this.$scrollContainer.addEventListener('scroll', this.onScroll)
    setTimeout(() => {
      this.showItems = true
      this.scrollToHash()
    }, 0)
  },
  destroyed () {
    document.removeEventListener('scroll', this.onScroll)
  },
  methods: {
    getRenderDataByQuery (query) {
      // if (typeof this.renderDataByQuery[query] !== 'undefined') {
      //   return this.renderDataByQuery[query]
      // }

      const renderItems = []
      const letterHasItems = {}

      for (let i = 0, l = this.items.length; i < l; i += 1) {
        const name = this.items[i]
        const letter = name[0]

        if (!name.includes(query)) {
          continue
        }

        if (typeof letterHasItems[letter] === 'undefined') {
          renderItems.push({
            id: letter,
            letter,
            type: 'header',
            size: 35,
          })
          letterHasItems[letter] = false
        }

        renderItems.push({
          id: name,
          name,
          letter,
          type: 'item',
          size: 40,
        })

        letterHasItems[letter] = true
      }

      const renderData = {
        items: renderItems,
        hasItems: renderItems.length > 0,
        letters: letterHasItems
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
    getItemNameParts (item) {
      const itemName = item
        .split('_')
        .map((str) => {
          return str.charAt(0).toUpperCase() + str.slice(1)
        })
        .join(' ')
      const boldStart = itemName.toLowerCase().indexOf(this.formattedInputQuery)
      const boldEnd = boldStart + this.formattedInputQuery.length

      return [
        { isBold: false, value: itemName.substring(0, boldStart) },
        { isBold: true, value: itemName.substring(boldStart, boldEnd) },
        { isBold: false, value: itemName.substring(boldEnd) },
      ]
    },
    scrollToHash () {
      const hash = this.$route.hash

      if (typeof hash !== 'string' || hash.length === 0) {
        return
      }

      const element = this.$scrollContainer.querySelector(hash)
      if (typeof element === 'undefined' || element === null) {
        return
      }
      const top = element.offsetTop

      if (this.$scrollContainer.scrollTop === top) {
        this.navi.selected = this.focusedLetterInView
        this.navi.fromUserClick = false
        this.navi.arrivedAtLetter = true
      } else {
        setTimeout(() => (this.$scrollContainer.scrollTo(0, top)), 0)
      }
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
        query: { q: this.inputQuery },
        hash: this.focusedLetterInView
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
  &__action-bar__inner {
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
    font-size: 3.2em;
    color: #E6CE51;
    text-transform: uppercase;

    h2 {
      font-weight: 500;
    }

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
  }

  .checkbox {
    display: flex;
    flex-flow: row nowrap;
    font-size: 1.6em;
    align-items: center;

    &--disabled {
      color: pink;
    }

    &__checkmark .icon__check__path {
      stroke: #DBDCDD;
    }

    &__input {
      display: none;

      &:focus + .checkbox__checkmark {
        stroke: darken(rgba(12, 136, 68, 1), 10)
      }

      &:checked + .checkbox__checkmark {
        .icon__check__path {
          stroke: rgba(12, 136, 68, 1);
        }
      }

      &:disabled + .checkbox__checkmark {
        stroke: pink;
      }
    }
  }

  .button {
    font-size: 1.6em;
    border-radius: 2.4em;
    margin: 1.2em 0;
    padding: 0.8em 1em;
    text-decoration: none;
    cursor: pointer;

    transition: background 300ms;

    &--primary {
      color: #fff;
      background: rgba(12, 136, 68, 1);
      border: 0;

      &:hover,
      &:focus {
        background: darken(rgba(12, 136, 68, 1), 10);
      }
    }

    &--secondary {
      background: #F1F1F1;
      border: 1px solid #DBDCDD;
      color: #1D1007;

      &:hover,
      &:focus {
        background: darken(#F1F1F1, 10);
        border: 1px solid darken(#DBDCDD, 10);
      }
    }
  }

  @media screen and (max-width: 400px) {
    .button {
      font-size: 1.4em;
    }
  }
}
</style>
