<template>
  <Modal id="cookbook__build__freeform">
    Build Freeform

    <button v-on:click="goBack">Cancel</button>
  </Modal>
</template>

<script>
import Modal from '@/components/Modal.vue'

export default {
  name: 'CookbookBuildFreeform',
  components: {
    Modal,
  },
  data () {
    return {}
  },
  methods: {
    goBack () {
      window.history.length > 1 ? this.$router.go(-1) : this.$router.push('/cookbook')
    }
  }
}
</script>
