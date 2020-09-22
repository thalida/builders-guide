<template>
  <Modal class="freeform">
    <header class="freeform__header">
      <div class="freeform__header__inner">
        <plaintext-input-icon />
        <h1>Bulk Enter Build Requirements</h1>
      </div>
    </header>

    <section class="freeform__content">
      <p>
        Got a list of resources required for a build from a YouTube comment?
        <span class="font-weight--medium">
          Enter the list below to quickly get started!
        </span>
      </p>
      <textarea
        v-model="textareaInput"
        :placeholder="'30 Torches\n5 glass panes'">
      </textarea>
    </section>

    <section class="freeform__action-bar">
      <div class="freeform__action-bar__inner">
        <button class="button button--secondary" v-on:click="cancel">Cancel</button>
        <button class="button button--primary" v-on:click="submit">Continue</button>
      </div>
    </section>
  </Modal>
</template>

<script>
import axios from 'axios'
import Modal from '@/components/Modal.vue'
import plaintextInputIcon from '../../../components/icons/plaintext-input.vue'

export default {
  name: 'CookbookBuildFreeform',
  components: {
    Modal,
    plaintextInputIcon,
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

  &__content,
  &__header__inner,
  &__action-bar__inner {
    width: 80%;
    max-width: 600px;
    margin: 0 auto;
  }

  &__header {
    z-index: 2;
    position: fixed;
    width: 100%;
    top: 0;
    left: 0;
    padding: 3.0em 0 0 0;
    background-image: linear-gradient(180deg, #FFFFFF 0%, rgba(255,255,255,0.00) 100%);

    &__inner {
      display: flex;
      flex-flow: row nowrap;
      align-items: center;
    }

    h1 {
      text-align: left;
    }

    .icon {
      width: 3.2em;
      height: 3.2em;
      margin-right: 1.6em;
    }
  }

  &__content {
    margin: 70px auto 100px;
    padding: 3em 0;
    z-index: 1;

    p {
      font-size: 1.6em;
    }

    textarea {
      width: 100%;
      height: calc(100vh - 400px);
      margin: 3em 0 0 0;
      padding: 1em;
      font: 1.6em 'Jost', Arial, sans-serif;
      border: 1px solid #DBDCDD;
      border-radius: 0.8em;
      resize: none;
    }
  }

  &__action-bar {
    display: flex;
    flex-flow: row nowrap;
    align-items: center;
    justify-content: center;
    z-index: 2;
    position: fixed;
    width: 100%;
    bottom: 0;
    left: 0;
    text-align: center;
    background-image: linear-gradient(180deg, rgba(255,255,255,0.00) 0%, #FFFFFF 99%);

    &__inner {
      display: flex;
      flex-flow: row nowrap;
      align-items: center;
      justify-content: space-between;
    }
  }
}
</style>
