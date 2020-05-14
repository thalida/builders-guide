<template>
  <Modal
    class="search"
    :modal-aria-label="modalAriaLabel">
    <header class="search__header">
      <input
        v-model="inputQuery"
        placeholder="What do you need?"
        v-on:keyup="onInputChange" />
    </header>

    <ol class="search__items">
      <RecycleScroller
        class="scroller"
        :items="renderData.items"
        v-slot="{ item }">
        <li v-if="item.type === 'header'" class="item-group">
          <a :id="item.letter"></a>
          <h2>{{ item.letter }}</h2>
        </li>
        <li v-if="item.type === 'item'" class="item-row">
          <label>
            <input
              type="checkbox"
              :value="item.name"
              v-model="tmpSelectedItems" />
            <img :src="item.src" />
            <span
              v-for="(stringPart, spi) in item.nameParts"
              :key="spi"
              :class="[`is-${stringPart.style}`]">{{stringPart.value}}</span>
          </label>
        </li>
      </RecycleScroller>
    </ol>

    <ol class="search__alpha">
        <li
          v-for="(letter, index) in navi.alpha"
          :key="index">

          <a
            v-if="renderData.letters[letter]"
            :href="`#${letter}`"
            :class="{'is-selected': navi.selected === letter}"
            v-on:click="onLetterClick(letter)">
            {{letter}}
          </a>
          <span v-else>{{letter}}</span>
        </li>
    </ol>

    <section class="search__action-bar">
      <button v-on:click="cancel">Cancel</button>
      <button v-on:click="submit">Continue with {{numSelected}} items</button>
    </section>
  </Modal>
</template>

<script>
import 'intersection-observer'
import { mapState } from 'vuex'

import Modal from '@/components/Modal.vue'

export default {
  name: 'CookbookBuildSearch',
  props: {
    query: String,
  },
  components: {
    Modal,
  },
  data () {
    const alpha = 'abcdefghijklmnopqrstuvwxyz'.split('')
    const inputQuery = (typeof this.query === 'string' && this.query.length > 0) ? this.query : ''
    return {
      modalAriaLabel: 'Search Modal',
      inputQuery,
      navi: {
        alpha,
        inViewport: [],
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
    ...mapState({}),
    items () {
      if (
        typeof this.$store.state.gameData[this.$store.state.selectedVersion] === 'undefined' ||
        typeof this.$store.state.gameData[this.$store.state.selectedVersion].items === 'undefined'
      ) {
        return []
      }

      return this.$store.state.gameData[this.$store.state.selectedVersion].items
    },
    selectedItems: {
      get () {
        return this.$store.state.selectedItems
      },
      set (newVal) {
        return this.$store.commit('setSelectedItems', newVal)
      }
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
      const renderItems = []
      const letterHasItems = {}

      for (let i = 0, l = this.items.length; i < l; i += 1) {
        const name = this.items[i]
        const letter = name[0]

        if (!name.includes(this.inputQuery)) {
          continue
        }

        if (typeof letterHasItems[letter] === 'undefined') {
          renderItems.push({ id: letter, letter, type: 'header', size: 35 })
          letterHasItems[letter] = false
        }

        renderItems.push({
          id: name,
          name,
          src: this.getItemImage(name),
          nameParts: this.getItemNameParts(name),
          type: 'item',
          size: 40
        })

        letterHasItems[letter] = true
      }

      return {
        items: renderItems,
        letters: letterHasItems
      }
    },
  },
  mounted () {
    this.$store.dispatch('setupSearchStore')
    this.navi.intersectionOptions.root = this.$elem
    this.$el.addEventListener('scroll', this.onScroll)
    this.scrollToHash()
  },
  destroyed () {
    document.removeEventListener('scroll', this.onScroll)
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
    getItemNameParts (item) {
      const boldStart = item.indexOf(this.inputQuery)
      const boldEnd = boldStart + this.inputQuery.length

      return [
        { style: 'normal', value: item.substring(0, boldStart) },
        { style: 'bold', value: item.substring(boldStart, boldEnd) },
        { style: 'normal', value: item.substring(boldEnd) },
      ]
    },
    scrollToHash () {
      const hash = this.$route.hash

      if (typeof hash !== 'string' || hash.length === 0) {
        return
      }

      const element = this.$el.querySelector(hash)
      if (typeof element === 'undefined' || element === null) {
        return
      }
      const top = element.offsetTop
      setTimeout(() => (this.$el.scrollTo(0, top)), 0)
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
      this.navi.arrivedAtLetter = this.navi.inViewport.indexOf(this.navi.selected) === 0
    },
    onVisibilityChanged (isVisible, e) {
      const elem = e.target
      const letter = elem.dataset.letter
      const visibleIndex = this.navi.inViewport.indexOf(letter)

      if (isVisible && visibleIndex === -1) {
        this.navi.inViewport.push(letter)
      } else if (!isVisible && visibleIndex >= 0) {
        this.navi.inViewport.splice(visibleIndex, 1)
      }

      this.navi.inViewport = this.navi.inViewport.filter((letter) => {
        return this.itemAlpha.indexOf(letter) >= 0
      })

      this.navi.inViewport.sort()

      if (this.navi.fromUserClick) {
        this.navi.arrivedAtLetter = (
          letter === this.navi.selected ||
          this.navi.inViewport.indexOf(this.navi.selected) >= 0
        )
        return
      }

      this.navi.selected = this.navi.inViewport[0]
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
      this.selectedItems = this.tmpSelectedItems.splice(0)
      this.tmpSelectedItems = null
      this.$router.push('/cookbook/build')
    },
    cancel () {
      this.tmpSelectedItems = null
      this.$router.push('/cookbook/build')
    }
  }
}
</script>

<style lang="scss" scoped>
.search {
  &__header {
    z-index: 2;
    position: fixed;
    width: 100%;
    top: 0;
    left: 0;
    background: white;
    text-align: center;
  }

  &__action-bar {
    z-index: 2;
    position: fixed;
    width: 100%;
    bottom: 0;
    left: 0;
    background: white;
    text-align: center;
  }

  &__alpha {
    position: fixed;
    height: 80%;
    top: 10%;
    right:10%;
    background: white;
    text-align: center;

    a {
      font-weight: bold;
    }

    .is-selected {
      color: red;
    }
  }

  &__items {
    margin: 60px 0;
    z-index: 1;
  }

  .is-bold {
    font-weight: bold;
  }

  .scroller {
    height: 100%;
  }

  .item-group {
    height: 35px;
    display: flex;
    align-items: center;
  }

  .item-row {
    height: 40px;
    display: flex;
    align-items: center;
  }
}
</style>
