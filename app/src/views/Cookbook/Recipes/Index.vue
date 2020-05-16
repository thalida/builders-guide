<template>
  <div id="cookbook__recipes">
    <recipe-tree
      :tree="recipeTree"
      :option-group="false"
      @update="handleTreeUpdate"></recipe-tree>
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
    recipeTree: {
      get () {
        return this.$store.state.recipeTree
      },
      set (newTree) {
        this.$store.commit('setRecipeTree', newTree)
      }
    },
  },
  mounted () {
    this.$store.dispatch('calculateResources')
  },
  methods: {
    handleTreeUpdate ({ tree }) {
      this.recipeTree = tree
    }
  }
}
</script>
