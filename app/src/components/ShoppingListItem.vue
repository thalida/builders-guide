<template>
  <div class="shopping-list-item">
    <input
      type="checkbox"
      :checked="hasAll"
      @change="onCheckboxChange" />
    <img :src="getItemImage(itemName)" />
    {{itemName}}
    <input type="number" v-model.number="combinedHave" />
    <input type="number" v-model.number="item.amount_required" />
    <div>
      Required For:
      <span
        v-for="(usedForItem, i) in usedForItems"
        :key="i">
        <img :src="getItemImage(usedForItem)" />
        {{ usedForItem }}
      </span>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    itemName: String,
  },
  data () {
    return {
      // item: {},
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
    item: {
      get () {
        return this.$store.state.shoppingList[this.itemName]
      },
      set (updatedItem) {
        const updatedList = Object.assign({}, this.shoppingList)
        updatedList[this.itemName] = updatedItem
        this.shoppingList = Object.assign({}, this.shoppingList, updatedList)
      }
    },
    usedForItems () {
      const names = Object.keys(this.item.amount_used_for)
      names.sort()
      return names
    },
    combinedHave: {
      get () {
        return this.item.have + this.item.implied_have
      },
      set (newHave) {
        const comboHave = this.item.have + this.item.implied_have
        const newHaveDelta = newHave - comboHave
        this.item.have = this.item.have + newHaveDelta
      }
    },
    hasAll () {
      return this.combinedHave >= this.item.amount_required
    },
  },
  watch: {},
  mounted () {},
  methods: {
    getItemImage (item) {
      const images = require.context('../assets/minecraft/1.15/32x32/', false, /\.png$/)
      try {
        return images(`./${item}.png`)
      } catch (error) {
        return images('./air.png')
      }
    },
    onCheckboxChange (e) {
      const isChecked = e.target.checked
      const haveAmount = (isChecked) ? this.item.amount_required : 0
      this.item = Object.assign({}, this.item, { have: haveAmount })
    }
  },
}
</script>

<style lang="scss" scoped>
.shopping-list-item {
  margin: 10px 0;
}
</style>