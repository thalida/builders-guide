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

    <router-view class="modal"></router-view>
  </div>
</template>

<script>
// @ is an alias to /src
export default {
  name: 'CookbookBuild',
  data () {
    return {
      searchTerm: null
    }
  },
  components: {},
  methods: {
    goToSearch () {
      console.log(this)
      const q = this.searchTerm
      this.searchTerm = null
      this.$router.push({ path: '/cookbook/build/search', query: { q } })
    }
  }
}
</script>

<style lang="scss" scoped>
.modal {
  display: block;
  position: absolute;
  top: 0;
  left: 0;
  background: white;
  width: 100%;
  height: 100%;
}
</style>
