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
      </p>
      <p class="font-weight--medium">
        Enter the list below to quickly get started!
      </p>
      <div class="freeform__errors" v-if="hasErrors">
        <p>{{errorData.numErrors}} error{{errorData.numErrors == 1 ? '' : 's'}} found parsing the following lines:</p>
        <div
          class="freeform__error"
           v-for="(error, index) in errorData.errors"
           :key="index">
          {{error.line}}
          <!-- <div class="freeform__error__details">
            <span class="font-weight--medium">count:</span> {{error.amount_required}}
            <span class="font-weight--medium">item:</span> {{error.name}}
          </div> -->
        </div>
      </div>
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
import plaintextInputIcon from '@/components/icons/plaintext-input.vue'

export default {
  name: 'CookbookBuildFreeform',
  components: {
    Modal,
    plaintextInputIcon,
  },
  data () {
    return {
      textareaInput: '',
      errorData: [],
      hasErrors: false,
    }
  },
  methods: {
    submit () {
      if (this.textareaInput.length === 0) {
        this.$router.push('/cookbook/build')
        return
      }

      const textareaStrArray = this.textareaInput.trim().split(/\r?\n/)
      axios
        .post(`${this.$store.getters.apiURL}/parse_items_from_string`, {
          parse_strings: textareaStrArray
        })
        .then(response => {
          const res = response.data
          this.hasErrors = res.has_errors

          if (!this.hasErrors) {
            this.$store.dispatch('mergeSelectedItems', res.items)
            this.$router.push('/cookbook/build')
            return
          }

          this.errorData = {
            errors: res.errors,
            numErrors: res.num_errors,
            numProcessedLines: res.num_processed_lines,
            successRate: res.success_rate,
          }
        })
    },
    cancel () {
      this.$router.push('/cookbook/build')
    },
  }
}
</script>

<style lang="scss">
.freeform {
  display: flex;
  flex-flow: column nowrap;

  .modal__main {
    display: flex;
    flex-flow: column nowrap;
    height: 100%;
  }

  &__content,
  &__header__inner,
  &__action-bar__inner {
    width: 80%;
    max-width: 600px;
    margin: 0 auto;
  }

  &__header {
    width: 100%;
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
    flex: 1;
    overflow: auto;
    padding: 3em 0;

    p {
      font-size: 1.6em;
    }

    textarea {
      width: 100%;
      height: 75%;
      margin: 2em 0 0 0;
      padding: 1em;
      font: 1.6em 'Jost', Arial, sans-serif;
      border: 1px solid #DBDCDD;
      border-radius: 0.8em;
      resize: none;
    }
  }

  &__errors {
    margin-top: 3em;
    background: #D45953;
    border-radius: 0.8em;
    padding: 2em;

    p {
      font-size: 1.6em;
      color: #fff;
      font-weight: 500;
    }
  }

  &__error {
    font-size: 1.6em;
    color: #fff;
    margin: 0.5em 0;

    &__details {
      font-size: 0.8em;
    }
  }

  &__action-bar {
    display: flex;
    flex-flow: row nowrap;
    align-items: center;
    justify-content: center;
    width: 100%;
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
