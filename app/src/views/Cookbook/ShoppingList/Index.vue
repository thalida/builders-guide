<template>
  <div id="cookbook__shopping_list">
    {{ shoppingList }}
  </div>
</template>

<script>
// @ is an alias to /src
export default {
  name: 'CookbookShoppingList',
  components: {},
  computed: {
    shoppingList () {
      return this.$store.state.shoppingList
    },
  },
  mounted () {
    this.$store.dispatch('calculateResources')
  }
}
</script>
