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

    <router-view></router-view>
  </div>
</template>

<script>
// import Modal from '@/components/Modal.vue'

export default {
  name: 'CookbookBuild',
  data () {
    return {
      searchTerm: null
    }
  },
  components: {
    // Modal,
  },
  methods: {
    goToSearch () {
      const q = this.searchTerm
      this.searchTerm = null
      this.$router.push({ path: '/cookbook/build/search', query: { q } })
    }
  }
}
</script>

<style lang="scss" scoped></style>
