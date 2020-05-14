<template>
  <div id="index"></div>
</template>

<script>
export default {
  name: 'Index',
  computed: {
    skipSplash: {
      get () {
        return this.$store.state.skipSplash
      },
      set (newBool) {
        this.$store.commit('setSkipSplash', newBool)
      }
    },
  },
  mounted () {
    let redirectPath = ''

    if (this.skipSplash) {
      redirectPath = '/cookbook'
    } else {
      redirectPath = '/splash'
    }

    this.$router.replace(redirectPath)
  },
}
</script>
