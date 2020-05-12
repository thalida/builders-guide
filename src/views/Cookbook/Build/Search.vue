<template>
  <div id="cookbook__build__search">
    Build Search
    <input v-model="inputQuery" placeholder="What do you need?" />
    <button v-on:click="goBack">Cancel</button>
  </div>
</template>

<script>
// @ is an alias to /src
export default {
  name: 'CookbookBuildSearch',
  props: {
    query: String,
  },
  data () {
    return {
      inputQuery: this.query,
    }
  },
  components: {},
  methods: {
    goBack () {
      window.history.length > 1 ? this.$router.go(-1) : this.$router.push('/cookbook')
    }
  }
}
</script>
