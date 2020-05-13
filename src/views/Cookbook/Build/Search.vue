<template>
  <Modal :modal-aria-label="modalAriaLabel">
    <div id="cookbook__build__search">
      Build Search
      <input v-model="inputQuery" placeholder="What do you need?" />
      <button v-on:click="goBack">Cancel</button>
    </div>
  </Modal>
</template>

<script>
import Modal from '@/components/Modal.vue'

export default {
  name: 'CookbookBuildSearch',
  props: {
    query: String,
  },
  data () {
    return {
      modalAriaLabel: 'Search Modal',
      inputQuery: this.query,
    }
  },
  components: {
    Modal,
  },
  methods: {
    goBack () {
      this.$router.push('/cookbook/build')
      // console.log('here?', this.$router)
      // window.history.length > 1 ? this.$router.go(-1) : this.$router.push('/cookbook')
    }
  }
}
</script>
