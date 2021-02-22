<template>
  <div class="cookbook">
    <header class="cookbook__header">
        <div class="cookbook__header__cell">
          <router-link class="wordmark wordmark--minimal" to="/">bg</router-link>
        </div>
        <div class="cookbook__header__cell">
          <h1>
            <span v-if="currRoute==='build'">Build Selection</span>
            <span v-if="currRoute==='recipes'">Build Recipes</span>
            <span v-if="currRoute==='shoppingList'">Shopping List</span>
          </h1>
        </div>
        <div class="cookbook__header__cell">
          <router-link class="link" to="/about">About</router-link>
        </div>
    </header>

    <router-view class="cookbook__content" v-if="show"></router-view>

    <nav class="cookbook__navbar">
      <div class="cookbook__navbar__inner">
        <router-link
          to="/cookbook/build"
          class="cookbook__navbar__link cookbook__navbar__link--build"
          aria-label="Build Section">
          <build-icon
            :class="[
            {
              'outlined': currRoute!=='build',
              'filled': currRoute==='build' && !hasSelectedItems,
              'highlighted': currRoute==='build' && hasSelectedItems,
            }]" />
        </router-link>

        <arrow-right-icon :class="hasSelectedItems ? 'highlighted' : 'faded'" />

        <component
          :is="hasSelectedItems ? 'router-link' : 'span'"
          to="/cookbook/recipes"
          class="cookbook__navbar__link cookbook__navbar__link--recipes"
          aria-label="Recipes Section">
          <recipes-icon
            :class="[
            {
              'loading': isRecipesLoading,
              'faded': !isRecipesLoading && currRoute!=='recipes' && !hasSelectedItems,
              'outlined': !isRecipesLoading && currRoute!=='recipes' && hasSelectedItems,
              'filled': !isRecipesLoading && currRoute==='recipes',
            }]" />
        </component>

        <arrow-right-icon :class="hasSelectedItems ? 'highlighted' : 'faded'" />

        <component
          :is="hasSelectedItems ? 'router-link' : 'span'"
          to="/cookbook/shopping-list"
          class="cookbook__navbar__link cookbook__navbar__link--shopping"
          aria-label="Shopping List Section">
          <shopping-list-icon
            :class="[
            {
              'loading': isShoppingListLoading,
              'faded': !isShoppingListLoading && currRoute!=='shoppingList' && !hasSelectedItems,
              'outlined': !isShoppingListLoading && currRoute!=='shoppingList' && hasSelectedItems,
              'filled': !isShoppingListLoading && currRoute==='shoppingList',
            }]" />
        </component>
      </div>
    </nav>
  </div>
</template>

<script>
import arrowRightIcon from '@/components/icons/arrow-right.vue'
import buildIcon from '@/components/icons/build.vue'
import recipesIcon from '@/components/icons/recipes.vue'
import shoppingListIcon from '@/components/icons/shopping-list.vue'

export default {
  name: 'Cookbook',
  components: {
    arrowRightIcon,
    buildIcon,
    recipesIcon,
    shoppingListIcon,
  },
  data () {
    return {
      show: true,
    }
  },
  computed: {
    currRoute () {
      return this.$route.name
    },
    selectedItems () {
      return this.$store.state.selectedItems
    },
    hasShoppingList () {
      return Object.keys(this.$store.state.shoppingList).length > 0
    },
    hasSelectedItems () {
      return this.selectedItems.length > 0
    },
    isRecipesLoading () {
      return this.$store.state.requests.fetchRecipeTree.isLoading
    },
    isShoppingListLoading () {
      return (
        (
          this.$store.state.requests.fetchRecipeTree.isLoading &&
          this.$store.state.requests.fetchShoppingList.isLoading
        ) || (
          this.hasSelectedItems && !this.hasShoppingList
        )
      )
    }
  }
}
</script>

<style lang="scss">
.cookbook {
  display: flex;
  flex-flow: column nowrap;
  align-items: center;
  height: 100%;

  &__header {
    position: relative;
    width: 80%;
    max-width: 600px;
    margin: 2.0em auto 0;
    display: grid;
    grid-template-columns: 1fr 2fr 1fr;
    align-items: center;

    &__cell {
      position: relative;

      &:last-of-type {
        justify-self: right;
      }
    }
  }

  &__content {
    display: flex;
    flex-flow: column nowrap;
    position: relative;
    width: 100%;
    flex: 1;
    overflow: auto;
  }

  &__navbar {
    display: flex;
    width: 100%;
    height: 6.4em;
    align-items: center;
    justify-content: center;
    background: #FAFAFA;
    box-shadow: 0 0 1.0em #DBDCDD;
    z-index: 1;

    &__inner {
      display: flex;
      width: 80%;
      max-width: 600px;
      height: 100%;
      align-items: center;
      justify-content: space-between;
    }
  }

  .searchbox {
    display: flex;
    position: relative;
    flex-flow: row nowrap;
    align-items: center;
    height: 48px;

    &__icon {
      position: absolute;
      left: 1.2em;
    }

    &__field {
      border: 0;
      padding: 0 1.4em 0 32px;
      margin: 0;
      background: transparent;
      height: 100%;
      width: 100%;
      border-radius: 2.4em;
      border: 2px solid #F5E0BE;
      background: #F5EDE1;
      color: #1D1007;
      font-size: 1.4em;
      transition: all 300ms;

      &:focus {
        outline: none;
        border: 2px solid #CEB946;
        box-shadow: 0 0 10px #F1F1F1;
      }
    }
  }
}
</style>
