<template>
  <div id="cookbook__shopping_list">
    <div>
      <div>
        <h3>Raw Ingredients</h3>
        <p>The base level ingredients you’ll need to craft.</p>
        <a @click="toggleNextIngredients">Toggle</a>
      </div>
      <div v-if="showNextIngredients">
        <shopping-list-item
          v-for="(item, index) in nextIngredients"
          :key="index"
          :item="shoppingList[item]"
          :item-name="item">
        </shopping-list-item>
      </div>
    </div>
    <div>
      <div>
        <h3>Build Process</h3>
        <p>Each item you’ll need to craft in reverse order.</p>
        <a @click="toggleBuildProcess">Toggle</a>
      </div>
      <div v-if="showBuildProcess">
        <div
          v-for="(level) in buildLevels"
          :key="level">
          <shopping-list-item
            v-for="(item, index) in buildProcess[level]"
            :key="index"
            :item="shoppingList[item]"
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
      const raw = []
      const list = Object.keys(this.shoppingList)
      for (let i = 0, l = list.length; i < l; i += 1) {
        const itemName = list[i]
        const item = this.shoppingList[itemName]
        if (item.has_recipe) {
          continue
        }

        raw.push(itemName)
      }

      raw.sort()

      return raw
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
