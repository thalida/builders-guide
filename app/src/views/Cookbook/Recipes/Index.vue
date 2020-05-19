<template>
  <div id="cookbook__recipes">
    <a @click="expandAll">expandAll</a>
    <a @click="collapseAll">collapseAll</a>
    <recipe-tree
      ref="tree"
      :node="recipeTree"
      :option-group="false"
      :level="0"
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
        this.$store.dispatch('updateRecipeTree', newTree)
      }
    },
  },
  mounted () {
    if (this.recipeTree.length === 0) {
      this.$store.dispatch('setupRecipeTree')
    }
  },
  methods: {
    handleTreeUpdate ({ tree }) {
      this.recipeTree = tree
    },
    expandAll () {
      this.$refs.tree.expandTree(true)
    },
    collapseAll () {
      this.$refs.tree.collapseTree(true)
    }
  }
}
</script>
