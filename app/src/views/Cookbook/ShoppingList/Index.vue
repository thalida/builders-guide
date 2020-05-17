<template>
  <div id="cookbook__shopping_list">
    <div>
      <div>
        <h3>Step-by-Step Guide</h3>
        <p>The next set of items you’ll need to have for your build.</p>
        <a @click="toggleNextIngredients">Toggle</a>
      </div>
      <div v-if="showNextIngredients">
        <shopping-list-item
          v-for="item in nextIngredients"
          :key="item"
          :item-name="item">
        </shopping-list-item>
      </div>
    </div>
    <div>
      <div>
        <h3>Build Process</h3>
        <p>Every item you’ll for your build in reverse order.</p>
        <a @click="toggleBuildProcess">Toggle</a>
      </div>
      <div v-if="showBuildProcess">
        <div
          v-for="level in buildLevels"
          :key="level">
          <shopping-list-item
            v-for="item in buildProcess[level]"
            :key="item"
            :item-name="item">
          </shopping-list-item>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ShoppingListItem from '@/components/ShoppingListItem.vue'

export default {
  name: 'CookbookShoppingList',
  components: {
    ShoppingListItem,
  },
  data () {
    return {
      showNextIngredients: true,
      showBuildProcess: true,
    }
  },
  computed: {
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
        if (item.have + item.implied_have >= item.amount_required) {
          continue
        }

        if (item.has_recipe) {
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
    toggleNextIngredients () {
      this.showNextIngredients = !this.showNextIngredients
    },
    toggleBuildProcess () {
      this.showBuildProcess = !this.showBuildProcess
    },
  },
}
</script>
