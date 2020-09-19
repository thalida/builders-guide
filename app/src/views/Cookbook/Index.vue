<template>
  <div
    class="cookbook"
    :class="[
      {
        'cookbook--has-selected-items': hasSelectedItems,
        'cookbook--no-selected-items': !hasSelectedItems,
      }
    ]">
    <header>
      <router-link to="/cookbook">bg</router-link>
      <router-link to="/about">About</router-link>
    </header>

    <router-view></router-view>

    <nav class="cookbook__navbar">
      <div class="cookbook__navbar__inner">
        <router-link
          to="/cookbook/build"
          class="cookbook__navbar__link cookbook__navbar__link--build">
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
          class="cookbook__navbar__link cookbook__navbar__link--recipes">
          <recipes-icon
            :class="[
            {
              'faded': currRoute!=='recipes' && !hasSelectedItems,
              'outlined': currRoute!=='recipes' && hasSelectedItems,
              'filled': currRoute==='recipes',
            }]" />
        </component>

        <arrow-right-icon :class="hasSelectedItems ? 'highlighted' : 'faded'" />

        <component
          :is="hasSelectedItems ? 'router-link' : 'span'"
          to="/cookbook/shopping-list"
          class="cookbook__navbar__link cookbook__navbar__link--shopping">
          <shopping-list-icon
            :class="[
            {
              'faded': currRoute!=='shoppingList' && !hasSelectedItems,
              'outlined': currRoute!=='shoppingList' && hasSelectedItems,
              'filled': currRoute==='shoppingList',
            }]" />
        </component>
      </div>
    </nav>
  </div>
</template>

<script>
import arrowRightIcon from '../../components/icons/arrow-right.vue'
import buildIcon from '../../components/icons/build.vue'
import recipesIcon from '../../components/icons/recipes.vue'
import shoppingListIcon from '../../components/icons/shopping-list.vue'

export default {
  name: 'Cookbook',
  components: {
    arrowRightIcon,
    buildIcon,
    recipesIcon,
    shoppingListIcon,
  },
  computed: {
    currRoute () {
      return this.$route.name
    },
    selectedItems () {
      return this.$store.state.selectedItems
    },
    hasSelectedItems () {
      return this.selectedItems.length > 0
    },
  },
  mounted () {
    console.log(this.$route)
  }
}
</script>

<style lang="scss">
$navbar-height: 6.4em;
.cookbook {
  display: flex;
  flex-flow: column nowrap;
  margin-bottom: $navbar-height * 2;

  &__navbar {
    display: flex;
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    height: $navbar-height;
    align-items: center;
    justify-content: center;
    background: #FAFAFA;

    &__inner {
      display: flex;
      width: 100%;
      max-width: 60.0em;
      height: 100%;
      align-items: center;
      justify-content: space-evenly;
    }
  }
}
</style>
