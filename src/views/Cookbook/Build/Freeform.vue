<template>
  <div id="cookbook__build__freeform">
    Build Freeform

    <button v-on:click="goBack">Cancel</button>
  </div>
</template>

<script>
// @ is an alias to /src
export default {
  name: 'CookbookBuildFreeform',
  data () {
    return {}
  },
  components: {},
  methods: {
    goBack () {
      window.history.length > 1 ? this.$router.go(-1) : this.$router.push('/cookbook')
    }
  }
}
</script>
