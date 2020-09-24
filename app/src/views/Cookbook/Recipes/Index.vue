<template>
  <div class="cookbook-recipes">
    <div class="cookbook-recipes__description">
      <p class="text text--primary">
        Select the recipes and ingredients which match your world and inventory.
      </p>
      <p class="text text--secondary">
        (Find your shoping list on the next screen.)
      </p>
    </div>

    <recipe-tree
      class="cookbook-recipes__tree"
      ref="tree"
      :node="recipeTree"
      :option-group="false"
      :level="0"
      @update="handleTreeUpdate">
    </recipe-tree>

    <div class="cookbook-recipes__actions">
      <a
        class="link"
        tabindex="0"
        @click="collapseAll"
        @keyup.enter="collapseAll">
        Collapse All
      </a>
      <a
        class="link"
        tabindex="0"
        @click="expandAll"
        @keyup.enter="expandAll">
        Expand All
      </a>
    </div>
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

<style lang="scss">
.cookbook-recipes {
  display: flex;
  flex-flow: column nowrap;
  width: 100%;
  max-width: 100%;

  &__description {
    width: 80%;
    max-width: 600px;
    margin: 3.0em auto 2.0em;

    .text {
      text-align: center;
    }
  }

  &__tree.recipe {
    padding: 0 0 3.6em 0;

    & > .recipe__tree {
      overflow: hidden;
    }
  }

  &__actions {
    position: fixed;
    display: flex;
    width: 100%;
    height: 3.4em;
    left: 0;
    bottom: 6.4em;
    justify-content: center;
    align-items: center;

    background: #F1F1F1;

    .link {
      margin: 0 1em;
    }
  }
}
</style>
