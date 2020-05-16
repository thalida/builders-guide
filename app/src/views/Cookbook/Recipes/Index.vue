<template>
  <div id="cookbook__recipes">
    <recipe-tree :tree="recipeTree" :option-group="false"></recipe-tree>
  </div>
</template>

<script>
import RecipeTree from '@/components/RecipeTree.vue'

export default {
  name: 'CookbookRecipes',
  components: {
    RecipeTree,
  },
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
