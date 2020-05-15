<template>
  <div id="cookbook__recipes">
    {{ recipeTree }}
  </div>
</template>

<script>
export default {
  name: 'CookbookRecipes',
  components: {},
  computed: {
    recipeTree () {
      return this.$store.state.recipeTree
    },
  },
  mounted () {
    this.$store.dispatch('calculateResources')
  }
}
</script>
