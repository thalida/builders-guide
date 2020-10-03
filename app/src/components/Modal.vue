<template>
  <div
    class="modal"
    role="dialog"
    :aria-label="modalAriaLabel">
    <div class="modal__main content-frame">
      <slot></slot>
    </div>
  </div>
</template>

<script>
// https://github.com/davidtheclark/focus-trap
import createFocusTrap from 'focus-trap'

export default {
  name: 'modal',
  props: {
    modalAriaLabel: String
  },
  data () {
    return {
      focusTrap: null,
      returnFocusOnDeactivate: (
        this.$route.meta.returnFocusOnDeactivate
          ? this.$route.meta.returnFocusOnDeactivate
          : false
      )
    }
  },
  mounted () {
    const $body = document.getElementsByTagName('body')[0]
    $body.classList.add('body--with-modal')

    this.focusTrap = createFocusTrap(this.$el, {
      returnFocusOnDeactivate: this.returnFocusOnDeactivate,
    })
    this.focusTrap.activate()
  },
  beforeDestroy () {
    this.focusTrap.deactivate()

    const $body = document.getElementsByTagName('body')[0]
    $body.classList.remove('body--with-modal')
  }
}
</script>

<style lang="scss">
// TODO: I don't have these yet, but I wil...
// @import '~@/assets/css/_variables';

.modal {
  display: none;
  position: fixed;
  flex-flow: column nowrap;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: white;

  .body--with-modal & {
    display: flex;
    overflow: auto;
    z-index: 9;
  }
}
</style>
