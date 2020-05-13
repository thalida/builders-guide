<template>
  <Modal
    id="cookbook__build__search"
    :modal-aria-label="modalAriaLabel">
    Build Search
    <input v-model="inputQuery" placeholder="What do you need?" />
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
      allItems: [],
    }
  },
  mounted () {
    axios
      .get('http://0.0.0.0:5000/api/1.15/items')
      .then(response => {
        this.res = response
        const keys = Object.keys(this.res.data)
        console.log(keys)
      })
  },
  methods: {
    goBack () {
      window.history.length > 1 ? this.$router.go(-1) : this.$router.push('/cookbook')
    }
  }
}
</script>
