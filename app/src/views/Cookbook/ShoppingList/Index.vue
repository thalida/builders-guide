<template>
  <div id="cookbook__shopping_list">
    {{ rawIngredients }}
    {{itemsByLevel}}
  </div>
</template>

<script>
// @ is an alias to /src
export default {
  name: 'CookbookShoppingList',
  components: {},
  computed: {
    shoppingList: {
      get () {
        return this.$store.state.shoppingList
      },
      set (newList) {
        this.$store.commit('setShoppingList', newList)
      }
    },
    rawIngredients () {
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
    itemsByLevel () {
      const itemsByLevel = {}
      const list = Object.keys(this.shoppingList)
      for (let i = 0, l = list.length; i < l; i += 1) {
        const itemName = list[i]
        const item = this.shoppingList[itemName]
        const level = item.level

        if (typeof itemsByLevel[level] === 'undefined') {
          itemsByLevel[level] = []
        }

        itemsByLevel[level].push(itemName)
      }

      const levels = Object.keys(itemsByLevel)
      for (let i = 0, l = levels.length; i < l; i += 1) {
        const level = levels[i]
        itemsByLevel[level].sort()
      }

      return itemsByLevel
    }
  },
  mounted () {
    this.$store.dispatch('setupShoppingList')
  }
}
</script>
