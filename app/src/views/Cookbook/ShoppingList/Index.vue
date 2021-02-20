<template>
  <div class="cookbook-shopping">
    <div class="cookbook-shopping__description">
      <p class="text text--primary">
        All ingredients required for your build.
      </p>
      <p class="text text--secondary">
        (Don’t like an ingredient?
        <router-link to="/cookbook/recipes" class="link">
        Customize the chosen recipes and ingredients
        </router-link>
        in the pervious step.)
      </p>
    </div>

    <div v-if="isLoading"
      class="cookbook-shopping__loading">
      <shopping-list-icon class="loading" />
      <p class="cookbook-shopping__loading__text">
        Creating shopping list for {{ numSelectedItems }} items based on selected recipes and ingredients&hellip;
      </p>
    </div>

    <div v-if="!isLoading" class="cookbook-shopping__content">
      <div
        class="cookbook-shopping__accordion"
        :class="[{
          'cookbook-shopping__accordion--is-open': showNextIngredients
        }]">
        <a
          class="cookbook-shopping__accordion__toggle"
          tabindex="0"
          @click="toggleNextIngredients"
          @keyup.enter="toggleNextIngredients">
          <h3>Step-by-Step Guide</h3>
          <chevron-right-icon />
        </a>
        <div class="cookbook-shopping__accordion__content">
          <p class="cookbook-shopping__accordion__description text--secondary">
            The next {{ nextIngredients.length }} items you’ll need to have for your build.
          </p>
          <shopping-list-item
            v-for="item in nextIngredients"
            :key="item"
            :item-name="item">
          </shopping-list-item>
        </div>
      </div>

      <hr class="cookbook-shopping__divider" />

      <div class="cookbook-shopping__accordion"
        :class="[{
          'cookbook-shopping__accordion--is-open': showBuildProcess
        }]">
        <a
          class="cookbook-shopping__accordion__toggle"
          tabindex="0"
          @click="toggleBuildProcess"
          @keyup.enter="toggleBuildProcess">
          <h3>Build Process</h3>
          <chevron-right-icon />
        </a>
        <div class="cookbook-shopping__accordion__content">
          <p class="cookbook-shopping__accordion__description text--secondary">
            Every item you’ll for your build in reverse chronological order.
          </p>
          <div
            v-for="level in buildLevels"
            :key="level">
            <shopping-list-item
              v-for="item in buildProcess[level]"
              :key="item"
              :item-name="item"
              :is-anchor="true">
            </shopping-list-item>
          </div>
        </div>
      </div>
    </div> <!-- End Shopping List Content-->

    <div v-if="numSelectedItems > 0" class="cookbook-shopping__actions">
      <a
        class="link"
        tabindex="0"
        @click="resetShoppingList()"
        @keyup.enter="resetShoppingList()">
        Reset shopping list
      </a>
    </div>
  </div> <!-- End Shopping List View-->
</template>

<script>
import shoppingListIcon from '@/components/icons/shopping-list.vue'
import chevronRightIcon from '@/components/icons/chevron-right.vue'
import ShoppingListItem from '@/components/ShoppingListItem.vue'

export default {
  name: 'CookbookShoppingList',
  components: {
    shoppingListIcon,
    chevronRightIcon,
    ShoppingListItem,
  },
  beforeRouteEnter (to, from, next) {
    next(vm => {
      if (!vm.numSelectedItems > 0) {
        vm.$router.replace({ name: 'build' })
      }
    })
  },
  data () {
    return {
      showNextIngredients: true,
      showBuildProcess: true,
    }
  },
  computed: {
    isLoading () {
      return (
        (
          this.$store.state.requests.fetchRecipeTree.isLoading &&
          this.$store.state.requests.fetchShoppingList.isLoading
        ) || (
          this.numSelectedItems > 0 &&
          Object.keys(this.shoppingList).length === 0
        )
      )
    },
    selectedItems () {
      return this.$store.state.selectedItems
    },
    numSelectedItems () {
      return this.selectedItems.length
    },
    shoppingList: {
      get () {
        return this.$store.state.shoppingList
      },
      set (newList) {
        this.$store.dispatch('updateShoppingList', newList)
      }
    },
    nextIngredients () {
      const next = []
      const list = Object.keys(this.shoppingList)
      const listLength = list.length
      const targetLimit = 20
      const minPages = 2
      const limit = (Math.floor(listLength / targetLimit) >= minPages) ? targetLimit : listLength

      for (let i = 0; i < listLength; i += 1) {
        const itemName = list[i]
        const item = this.shoppingList[itemName]
        if (this.meetsRequirements(item)) {
          continue
        }

        let hasAllRequirements = true
        for (let j = 0, ll = item.requires.length; j < ll; j += 1) {
          const requiredItemName = item.requires[j]
          const requiredItem = this.shoppingList[requiredItemName]

          if (!this.meetsRequirements(requiredItem)) {
            hasAllRequirements = false
            break
          }
        }

        if (!hasAllRequirements) {
          continue
        }

        next.push(itemName)
      }

      next.sort((a, b) => {
        return this.shoppingList[b].amount_required - this.shoppingList[a].amount_required
      })

      next.splice(limit, next.length)

      return next
    },
    buildProcess () {
      const buildProcess = {}
      const list = Object.keys(this.shoppingList)
      for (let i = 0, l = list.length; i < l; i += 1) {
        const itemName = list[i]
        const item = this.shoppingList[itemName]
        const level = item.level

        if (typeof buildProcess[level] === 'undefined') {
          buildProcess[level] = []
        }

        buildProcess[level].push(itemName)
      }

      const levels = Object.keys(buildProcess)
      for (let i = 0, l = levels.length; i < l; i += 1) {
        const level = levels[i]
        buildProcess[level].sort()
      }

      return buildProcess
    },
    buildLevels () {
      return Object.keys(this.buildProcess)
    }
  },
  mounted () {},
  methods: {
    meetsRequirements (item) {
      return item.have + item.implied_have >= item.amount_required
    },
    toggleNextIngredients () {
      this.showNextIngredients = !this.showNextIngredients
    },
    toggleBuildProcess () {
      this.showBuildProcess = !this.showBuildProcess
    },
    resetShoppingList () {
      // this.$store.dispatch('resetShoppingList')
    },
  },
}
</script>

<style lang="scss">
.cookbook-shopping {
  display: flex;
  flex-flow: column nowrap;
  width: 100%;
  max-width: none;

  &__loading {
    flex: 1;
    width: 80%;
    max-width: 600px;
    margin: 0 auto;
    overflow: auto;
    display: flex;
    flex-flow: column nowrap;
    justify-content: center;
    align-items: center;

    .icon {
      width: 6.4em;
      height: 6.4em;
      margin-bottom: 2em;
    }

    &__text {
      font-size: 1.6em;
      font-weight: 500;
      color: #1D1007;
    }
  }

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
    overflow: auto;
  }

  &__divider {
    margin: 0;
    border: 0;
    height: 0.5em;
    background: #F1F1F1;
  }

  &__accordion {
    margin: 4.0em auto;
    width: 80%;
    max-width: 600px;

    .icon__chevron-right {
      transform: rotate(90deg);
      transition: all 600ms;
    }

    &__toggle {
      display: flex;
      flex-flow: row nowrap;
      align-items: center;
      justify-content: space-between;
      cursor: pointer;
      padding-right: 0.5em;
    }

    &__description {
      margin: 1em 0;
    }

    &__content {
      transition: all 600ms cubic-bezier(0, 1, 0, 1);
      max-height: 0;
      overflow: hidden;
    }

    &--is-open {
      .cookbook-shopping__accordion__content {
        max-height: 99999px;
        overflow: auto;
      }

      .icon__chevron-right {
        transform: rotate(-90deg);
      }
    }
  }

  .icon__chevron-right {
    &__path {
      fill: #1D1007;
    }
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
