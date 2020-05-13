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
    }
  },
  methods: {
    goBack () {
      window.history.length > 1 ? this.$router.go(-1) : this.$router.push('/cookbook')
    }
  }
}
</script>
