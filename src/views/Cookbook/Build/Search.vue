<template>
  <Modal
    id="search"
    :modal-aria-label="modalAriaLabel">
    <header class="search__header">
      <input v-model="inputQuery" placeholder="What do you need?" />
    </header>

    <ol class="search__items">
      <li
        v-for="(letter, index) in itemAlpha"
        v-waypoint="{
          active: true,
          callback: onWaypoint,
          options: intersectionOptions
        }"
        :key="index"
        :data-index="index">
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
                v-model="selectedItems" />
              {{item}}
            </label>
          </li>
        </ol>
      </li>
    </ol>

    <ol class="search__alpha">
        <li
          v-for="(letter, index) in alpha"
          :key="index">

          <a
            v-if="itemAlpha.indexOf(letter) >= 0"
            :href="`#${letter}`"
            :class="{'is-selected': activeLetter === letter}">
            {{letter}}
          </a>
          <span v-else>{{letter}}</span>
        </li>
    </ol>

    <section class="search__action-bar">
      <button v-on:click="cancel">Cancel</button>
      <button v-on:click="submit">Continue</button>
    </section>
  </Modal>
</template>

<script>
import axios from 'axios'
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
    return {
      modalAriaLabel: 'Search Modal',
      inputQuery: this.query,
      alpha,
      visibleLetters: [],
      activeLetter: null,
      items: [],
      selectedItems: [],
      // https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API
      intersectionOptions: {
        root: null,
        rootMargin: '0px 0px 0px 0px',
        threshold: [0] // [0.25, 0.75] if you want a 25% offset!
      }
    }
  },
  computed: {
    groupedItems () {
      var groupedItems = {}
      for (let i = 0, l = this.items.length; i < l; i += 1) {
        const itemName = this.items[i]
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
    // TODO: FIGURE OUT HOW TO SCROLL TO THIS POINT
    const hash = this.$route.hash
    console.log(hash)

    if (typeof hash === 'string' && hash.length > 0) {
      const hashParts = hash.split('#')
      const hashLetter = hashParts[1]
      console.log(hashLetter)
    }

    this.intersectionOptions.root = this.$el
    axios
      .get('http://0.0.0.0:5000/api/1.15/items')
      .then(response => (this.items = response.data))
  },
  methods: {
    onWaypoint ({ el, going, direction }) {
      const letterIndex = parseInt(el.dataset.index, 10)

      if (going === this.$waypointMap.GOING_IN) {
        this.visibleLetters.push(letterIndex)
      } else if (going === this.$waypointMap.GOING_OUT) {
        const foundIndex = this.visibleLetters.indexOf(letterIndex)
        if (foundIndex >= 0) {
          this.visibleLetters.splice(foundIndex, 1)
        }
      }

      this.visibleLetters.sort()
      this.activeLetter = this.itemAlpha[this.visibleLetters[0]]
    },
    submit () {
      // TODO: add submit logic!!!
      console.log('TODO!')
      console.log('Handle:', this.selectedItems)
    },
    cancel () {
      window.history.length > 1 ? this.$router.go(-1) : this.$router.push('/cookbook')
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
    z-index: 1;
  }
}
</style>
