<template>
  <Modal
    id="search"
    :modal-aria-label="modalAriaLabel">
    <header class="search__header">
      <input
        v-model="inputQuery"
        placeholder="What do you need?"
        v-on:keyup="onInputChange" />
    </header>
    <ol class="search__items">
      <li
        v-for="(letter, index) in navi.alpha"
        v-show="itemAlpha.indexOf(letter) >= 0"
        v-observe-visibility="{
          callback: onVisibilityChanged,
          intersection: navi.intersectionOptions
        }"
        :key="index"
        :data-letter="letter">
        <a :id="letter"></a>
        <h2>{{ letter }}</h2>
        <ol>
          <li
            v-for="(item, itemIndex) in groupedItems[letter]"
            :key="itemIndex">
            <label>
              <input
                type="checkbox"
                :value="item"
                v-model="tmpSelectedItems" />
              <img :src="getItemImage(item)" />
              {{item}}
            </label>
          </li>
        </ol>
      </li>
    </ol>

    <ol class="search__alpha">
        <li
          v-for="(letter, index) in navi.alpha"
          :key="index">

          <a
            v-if="itemAlpha.indexOf(letter) >= 0"
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
    ...mapState({
      items: state => state.gameData[state.selectedVersion].items,
    }),
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
    filteredItems () {
      return this.items.filter(item => {
        return item.indexOf(this.inputQuery) >= 0
      })
    },
    groupedItems () {
      var groupedItems = {}
      for (let i = 0, l = this.filteredItems.length; i < l; i += 1) {
        const itemName = this.filteredItems[i]
        const firstChar = itemName[0]

        if (typeof groupedItems[firstChar] === 'undefined') {
          groupedItems[firstChar] = []
        }

        groupedItems[firstChar].push(itemName)
      }

      const alphaLabels = Object.keys(groupedItems)
      for (let i = 0, l = alphaLabels.length; i < l; i += 1) {
        const label = alphaLabels[i]
        groupedItems[label].sort()
      }

      return groupedItems
    },
    itemAlpha () {
      const alpha = Object.keys(this.groupedItems)
      alpha.sort()
      return alpha
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
      // this.$store.commit('setTmpSelectedItems', newVal)
      this.selectedItems = this.tmpSelectedItems.splice(0)
      this.tmpSelectedItems = null
      console.log('Handle:', this.selectedItems)
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
    position: fixed;
    width: 100%;
    top: 0;
    left: 0;
    background: white;
    text-align: center;
  }

  &__action-bar {
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
}
</style>
