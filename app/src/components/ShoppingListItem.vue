<template>
  <div class="shopping-list-item">
    <input
      type="checkbox"
      :checked="hasAll"
      @change="onCheckboxChange" />
    <img :src="getItemImage(itemName)" />
    {{itemName}}
    <input type="number" v-model.number="combinedHave" min="0" />
    <input
      type="number"
      v-model.number="amountRequired"
      min="0"
      :disabled="item.amount_used_for.self === 0" />
    <div>
      Required For:
      <span
        v-for="(usedForItem, index) in usedForItems"
        v-show="usedForItem !== 'self'"
        :key="index">
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
    return {}
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
      set (newVal) {
        const haveAmount = newVal - this.item.implied_have
        console.log(
          this.item.name,
          newVal,
          this.item.implied_have,
          haveAmount
        )
        this.item = Object.assign({}, this.item, { have: haveAmount })
      }
    },
    amountRequired: {
      get () {
        return this.item.amount_required
      },
      set (newVal) {
        const remainder = newVal - this.item.amount_used_for.recipes
        let amountRequired = 0
        // let selfAmount = 0
        if (remainder < this.item.amount_used_for.recipes) {
          amountRequired = this.item.amount_used_for.recipes
          // selfAmount = 0
        } else {
          amountRequired = newVal
          // selfAmount = remainder
        }
        // const newSelf = newVal - everythingElse
        this.item = Object.assign({}, this.item, {
          amount_required: amountRequired
        })
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
