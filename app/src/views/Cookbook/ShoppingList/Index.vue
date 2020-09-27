<template>
  <div class="cookbook-shopping">
    <div class="cookbook-shopping__description">
      <p class="text text--primary">
        The ingredients you’ll use for your build.
      </p>
      <p class="text text--secondary">
        (Don’t like an ingredient? Customize the chosen recipes and ingredients on the pervious screen.)
      </p>
    </div>

    <div class="cookbook-shopping__content">
      <div class="cookbook-shopping__accordion">
        <a
          class="cookbook-shopping__accordion__toggle"
          tabindex="0"
          @click="toggleNextIngredients"
          @keyup.enter="toggleNextIngredients">
          <h3>Step-by-Step Guide</h3>
          <chevron-right-icon />
        </a>
        <div
          v-if="showNextIngredients"
          class="cookbook-shopping__accordion__content">
          <p class="cookbook-shopping__accordion__description text--secondary">
            The next set of items you’ll need to have for your build.
          </p>
          <shopping-list-item
            v-for="item in nextIngredients"
            :key="item"
            :item-name="item">
          </shopping-list-item>
        </div>
      </div>

      <hr class="cookbook-shopping__divider" />

      <div class="cookbook-shopping__accordion">
        <a
          class="cookbook-shopping__accordion__toggle"
          tabindex="0"
          @click="toggleBuildProcess"
          @keyup.enter="toggleBuildProcess">
          <h3>Build Process</h3>
          <chevron-right-icon />
        </a>
        <div
          v-if="showBuildProcess"
          class="cookbook-shopping__accordion__content">
          <p class="cookbook-shopping__accordion__description text--secondary">
            Every item you’ll for your build in reverse order.
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
  </div> <!-- End Shopping List View-->
</template>

<script>
import chevronRightIcon from '@/components/icons/chevron-right.vue'
import ShoppingListItem from '@/components/ShoppingListItem.vue'

export default {
  name: 'CookbookShoppingList',
  components: {
    chevronRightIcon,
    ShoppingListItem,
  },
  beforeRouteEnter (to, from, next) {
    next(vm => {
      if (!vm.hasSelectedItems) {
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
    selectedItems () {
      return this.$store.state.selectedItems
    },
    hasSelectedItems () {
      return this.selectedItems.length > 0
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
      for (let i = 0, l = list.length; i < l; i += 1) {
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

      next.sort()

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
  mounted () {
    if (Object.keys(this.shoppingList).length === 0) {
      this.$store.dispatch('setupShoppingList')
    }
  },
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
  },
}
</script>

<style lang="scss">
.cookbook-shopping {
  display: flex;
  flex-flow: column nowrap;
  width: 100%;
  max-width: none;

  &__description {
    margin: 3.0em auto 2.0em;

    .text {
      text-align: center;
    }
  }

  &__divider {
    margin: 0;
    border: 0;
    height: 0.5em;
    background: #F1F1F1;
  }

  &__accordion {
    width: 80%;
    max-width: 600px;
    margin: 4.0em auto;

    &__toggle {
      display: flex;
      flex-flow: row nowrap;
      align-items: center;
      justify-content: space-between;
      cursor: pointer;
    }

    &__description {
      margin: 1em 0;
    }

    &__content {

    }
  }

  .icon__chevron-right {
    &__path {
      fill: #1D1007;
    }
  }
}
</style>
