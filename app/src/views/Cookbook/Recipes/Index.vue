<template>
  <div class="cookbook-recipes">
    <div class="cookbook-recipes__description">
      <p class="text text--primary">
        Customise the recipes and ingredients which match your world and inventory.
      </p>
      <p class="text text--secondary">
        (Find your
          <router-link to="/cookbook/shopping-list" class="link">
          shopping list
          </router-link>
          on the next step.)
      </p>
    </div>

    <div class="cookbook-recipes__content">
      <recipe-tree ref="recipeTree"></recipe-tree>
    </div>

    <div v-if="hasSelectedItems" class="cookbook-recipes__actions">
      <a
        class="link"
        tabindex="0"
        @click="resetAllSelections()"
        @keyup.enter="resetAllSelections()">
        Reset all selections
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
    selectedItems () {
      return this.$store.state.selectedItems
    },
    hasSelectedItems () {
      return this.selectedItems.length > 0
    },
  },
  methods: {
    resetAllSelections () {
      this.$refs.recipeTree.reset()
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

    .link {
      font-size: 1em;
    }
  }

  &__content {
    flex: 1;
    width: 100%;
    overflow: auto;
  }

  &__actions {
    display: flex;
    width: 100%;
    height: 3.4em;
    justify-content: center;
    align-items: center;
    background: #F1F1F1;
  }
}
</style>
