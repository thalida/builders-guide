<template>
  <Modal
    id="search"
    :modal-aria-label="modalAriaLabel">
    <header class="search__header">
      <input v-model="inputQuery" placeholder="What do you need?" />
    </header>

    <section class="search__body">
    <ol class="search__items">
      <li
        v-for="(letter, index) in itemAlpha"
        :key="index">
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
          {{letter}}
        </li>
    </ol>
    </section>

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
    return {
      modalAriaLabel: 'Search Modal',
      inputQuery: this.query,
      alpha: 'abcdefghijklmnopqrstuvwxyz'.split(''),
      items: [],
      selectedItems: [],
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
    axios
      .get('http://0.0.0.0:5000/api/1.15/items')
      .then(response => (this.items = response.data))
  },
  methods: {
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
  }

  &__body {

  }
}
</style>
