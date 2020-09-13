<template>
  <Modal class="freeform">
    <header class="freeform__header">
      Build Freeform
    </header>

    <section class="freeform__content">
      <p>
        Got a list of resources required for a build from a YouTube comment?
        Enter the list to quickly get started!
      </p>
      <textarea
        v-model="textareaInput"
        :placeholder="'30 Torches\n5 glass panes'">
      </textarea>
    </section>

    <section class="freeform__action-bar">
      <button v-on:click="cancel">Cancel</button>
      <button v-on:click="submit">Continue</button>
    </section>
  </Modal>
</template>

<script>
import axios from 'axios'
import Modal from '@/components/Modal.vue'

export default {
  name: 'CookbookBuildFreeform',
  components: {
    Modal,
  },
  data () {
    return {
      textareaInput: ''
    }
  },
  methods: {
    submit () {
      const textareaStrArray = this.textareaInput.split(/\r?\n/)
      const selectedVersion = this.$store.state.selectedVersion
      axios
        .post(`http://0.0.0.0:5000/api/${selectedVersion}/parse_items_from_string`, {
          parse_strings: textareaStrArray
        })
        .then(response => {
          const res = response.data
          if (!res.has_errors) {
            this.$store.dispatch('mergeSelectedItems', res.items)
            this.$router.push('/cookbook/build')
            return
          }

          console.log(res)
        })
    },
    cancel () {
      this.tmpSelectedItems = null
      this.$router.push('/cookbook/build')
    },
  }
}
</script>

<style lang="scss" scoped>
.freeform {
  &__header {
    z-index: 2;
    position: fixed;
    width: 100%;
    top: 0;
    left: 0;
    background: white;
    text-align: center;
  }

  &__content {
    margin: 30px 0;
    z-index: 1;
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
}
</style>
