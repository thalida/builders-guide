<template>
  <div class="cookbook">
    <header class="cookbook__header">
      <!-- <div class="cookbook__header__inner"> -->
        <div class="cookbook__header__cell">
          <router-link class="wordmark wordmark--minimal" to="/cookbook">bg</router-link>
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
      <!-- </div> -->
    </header>

    <router-view class="cookbook__content" v-if="show"></router-view>

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
      show: false,
    }
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
    this.$store
      .dispatch('setupItems')
      .then(() => { this.show = true })
  }
}
</script>

<style lang="scss">
$navbar-height: 6.4em;
.cookbook {
  display: flex;
  flex-flow: column nowrap;
  margin-bottom: $navbar-height;
  align-items: center;

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
    width: 80%;
    max-width: 600px;
  }

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
      width: 80%;
      max-width: 600px;
      height: 100%;
      align-items: center;
      // justify-content: space-evenly;
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
