<template>
  <div class="cookbook__recipes">
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
  beforeRouteEnter (to, from, next) {
    next(vm => {
      if (!vm.hasSelectedItems) {
        vm.$router.replace({ name: 'build' })
      }
    })
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
    selectedItems () {
      return this.$store.state.selectedItems
    },
    hasSelectedItems () {
      return this.selectedItems.length > 0
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
