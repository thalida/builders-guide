<template>
  <Modal
    id="cookbook__build__search"
    :modal-aria-label="modalAriaLabel">
    Build Search
    <input v-model="inputQuery" placeholder="What do you need?" />

    <ol>
      <li
        v-for="(letter, index) in itemAlpha"
        :key="index">
        <h2>{{ letter }}</h2>
        <ol>
          <li
            v-for="(item, itemIndex) in groupedItems[letter]"
            :key="itemIndex">
            {{item}}
          </li>
        </ol>
      </li>
    </ol>

    <button v-on:click="goBack">Cancel</button>
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
    goBack () {
      window.history.length > 1 ? this.$router.go(-1) : this.$router.push('/cookbook')
    }
  }
}
</script>
