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
          <build-filled v-if="currRoute==='build' && hasSelectedItems" />
          <build-selected v-else-if="currRoute==='build'" />
          <build-default v-else />
        </router-link>
        <arrow-right />
        <component
          :is="hasSelectedItems ? 'router-link' : 'span'"
          to="/cookbook/recipes"
          class="cookbook__navbar__link cookbook__navbar__link--recipies">
          <recipies-selected v-if="currRoute==='recipes'" />
          <recipies-default v-else />
        </component>
        <arrow-right />
        <component
          :is="hasSelectedItems ? 'router-link' : 'span'"
          to="/cookbook/shopping-list"
          class="cookbook__navbar__link cookbook__navbar__link--shopping">
          <shopping-selected v-if="currRoute==='shoppingList'" />
          <shopping-default v-else />
        </component>
      </div>
    </nav>
  </div>
</template>

<script>
import arrowRight from '../../components/icons/arrow-right.vue'
import buildDefault from '../../components/icons/build-default.vue'
import buildSelected from '../../components/icons/build-selected.vue'
import buildFilled from '../../components/icons/build-filled.vue'
import recipiesDefault from '../../components/icons/recipies-default.vue'
import recipiesSelected from '../../components/icons/recipies-selected.vue'
import shoppingDefault from '../../components/icons/shopping-default.vue'
import shoppingSelected from '../../components/icons/shopping-selected.vue'

export default {
  name: 'Cookbook',
  components: {
    arrowRight,
    buildDefault,
    buildSelected,
    buildFilled,
    recipiesDefault,
    recipiesSelected,
    shoppingDefault,
    shoppingSelected,
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

    .icon {
      transition: all 300ms;
    }
  }

  &--no-selected-items {
    .icon--arrow-right,
    .icon--recipies,
    .icon--shopping {
      fill: #DBDCDD;
    }
  }

  &--has-selected-items {
    .icon--arrow-right {
      fill: #A07532;
    }

    a.cookbook__navbar__link {
      .icon--default {
        fill: #918C88
      }

      &:hover .icon--default {
        fill: #000;
      }
    }
  }
}
</style>
