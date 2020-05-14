<template>
  <div id="cookbook__build">
    <select>
      <option>v1.15.2</option>
    </select>

    <div class="build-menu">
      <input
        type="text"
        v-model="searchTerm"
        placeholder="What do you need?"
        v-on:focus="goToSearch" />

      <router-link to="/cookbook/build/library">L</router-link>
      <router-link to="/cookbook/build/freeform">F</router-link>
    </div>

    {{selectedItems}}

    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'CookbookBuild',
  components: {},
  data () {
    return {
      searchTerm: null
    }
  },
  computed: {
    selectedItems () {
      return this.$store.state.selectedItems
    }
  },
  methods: {
    goToSearch () {
      const q = this.searchTerm
      this.searchTerm = null

      let query = {}
      if (typeof q === 'string' && q.length > 0) {
        query = { q }
      }

      this.$router.push({ path: '/cookbook/build/search', query })
    }
  }
}
</script>

<style lang="scss" scoped></style>
