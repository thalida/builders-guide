<template>
  <div class="shopping-item">
    <a v-if="isAnchor" :id="itemName"></a>

    <div class="shopping-item__row">
      <label class="checkbox" tabindex="0">
        <input
          class="checkbox__input"
          type="checkbox"
          name="checkbox"
          :checked="hasAll"
          @change="onCheckboxChange">
        <check-icon class="checkbox__checkmark" />
      </label>

      <div class="shopping-item__row__item">
        <img
          class="shopping-item__row__icon"
          :src="getItemImage(itemName)" />

        <div class="shopping-item__row__text">
          <span class="shopping-item__row__label">
            {{ getItemLabel(itemName) }}
          </span>
          <a
            class="link"
            :href="`https://minecraft.gamepedia.com/${itemName}`"
            target="_blank">
            Minecraft Wiki
          </a>
        </div>
      </div>

      <div class="shopping-item__row__inputs">
        <input
          class="shopping-item__row__input"
          type="number"
          v-model.number="combinedHave"
          min="0" />
        <div class="shopping-item__row__divider"></div>
        <span class="shopping-item__row__amount-required">{{ amountRequired }}</span>
        <!-- <input
          class="shopping-item__row__input"
          type="number"
          v-model.number="amountRequired"
          min="0"
          :disabled="!isUserSelected" /> -->
      </div>
    </div>

    <div
      class="shopping-item__required-for"
      v-if="usedForItems.length > 0">
      <span
        class="shopping-item__required-for__label"
        v-if="item.amount_used_for.self > 0">
        Also used in:
      </span>
      <span
        class="shopping-item__required-for__label"
        v-else>
        Required for:
      </span>
      <a
        class="shopping-item__required-for__tag"
        v-for="(usedForItem, index) in usedForItems"
        :key="index"
        :href="`#${usedForItem}`">
          <img
            class="shopping-item__required-for__tag__icon"
            :src="getItemImage(usedForItem)" />
          <span class="shopping-item__required-for__tag__label">
            {{ getItemLabel(usedForItem) }}
          </span>
      </a>
    </div>
  </div>
</template>

<script>
import debounce from 'lodash.debounce'
import { getItemImage, getItemLabel } from '@/helpers.js'
import checkIcon from '@/components/icons/check.vue'

export default {
  props: {
    itemName: String,
    isAnchor: {
      type: Boolean,
      default: false,
    }
  },
  components: {
    checkIcon,
  },
  data () {
    return {}
  },
  computed: {
    selectedItems: {
      get () {
        return this.$store.state.selectedItems
      },
      set (newList) {
        this.debouncedUpdateSelected(newList)
      }
    },
    selectedItemsByKey () {
      return this.$store.getters.selectedByKey
    },
    isUserSelected () {
      return typeof this.selectedItemsByKey[this.item.name] !== 'undefined'
    },
    shoppingList: {
      get () {
        return this.$store.state.shoppingList
      },
      set (newList) {
        this.debouncedUpdateList(newList)
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

      const selfIdx = names.indexOf('self')
      names.splice(selfIdx, 1)

      const recipesIdx = names.indexOf('recipes')
      names.splice(recipesIdx, 1)

      names.sort()
      return names
    },
    combinedHave: {
      get () {
        return this.item.have + this.item.implied_have
      },
      set (newVal) {
        const haveAmount = newVal - this.item.implied_have
        this.item = Object.assign({}, this.item, { have: haveAmount })
      }
    },
    amountRequired: {
      get () {
        return this.item.amount_used_for.self + this.item.amount_used_for.recipes
      },
      set (newVal) {
        const newSelectedAmount =
          (newVal > this.item.amount_used_for.recipes)
            ? newVal - this.item.amount_used_for.recipes
            : 0

        const selectedCopy = this.selectedItems.slice(0)
        for (let i = 0, l = selectedCopy.length; i < l; i += 1) {
          const selectedItem = selectedCopy[i]
          if (selectedItem.name === this.item.name) {
            selectedItem.amount = newSelectedAmount
          }
        }
        this.selectedItems = selectedCopy
      }
    },
    hasAll () {
      return this.combinedHave >= this.item.amount_required
    },
  },
  watch: {},
  created () {
    this.debouncedUpdateList = debounce(this.updateShoppingList, 300)
  },
  methods: {
    getItemImage,
    getItemLabel,
    updateShoppingList (items) {
      this.$store.dispatch('updateShoppingList', items)
    },
    onCheckboxChange (e) {
      const isChecked = e.target.checked
      const haveAmount = (isChecked) ? this.item.amount_required : 0
      this.item = Object.assign({}, this.item, { have: haveAmount })
    }
  },
}
</script>

<style lang="scss">
.shopping-item {
  margin: 0 0 1em;

  &__row {
    display: flex;
    flex-flow: row nowrap;
    padding: 1.0em;
    background: #FAFAFA;

    &__item {
      flex: 2 0 auto;
      display: flex;
      flex-flow: row nowrap;
      align-items: center;
    }

    &__text {
      flex: 2 0 auto;
      margin: 0 1.0em 0 0;
      display: flex;
      flex-flow: column;
    }

    &__label {
      font-size: 1.6em;
      font-weight: 500;
      color: #1D1007;
      text-transform: capitalize;
      line-height: 1.6;
    }

    .link {
      width: fit-content;
    }

    &__icon {
      flex: 0 1 32px;
      height: 32px;
      width: 32px;
      margin: 0 1.0em;
    }

    &__inputs {
      display: flex;
      flex-flow: row nowrap;
      align-items: center;
    }

    &__input {
      width: 32px;
      height: 32px;
      padding: 0;
      border: 0;
      border-bottom: 1px solid #918C88;
      text-align: center;
      font-size: 1.6em;
      font-weight: 500;
      background: transparent;
    }

    &__divider {
      width: 0.2em;
      height: 1.5em;
      background: #DBDCDD;
      transform: rotate(40deg);
      margin: 0 1.0em;
    }

    &__amount-required {
      font-size: 1.6em;
      font-weight: 500;
      text-align: center;
    }
  }

  &__required-for {
    display: flex;
    flex-flow: row wrap;
    align-items: center;
    margin: 0.5em 0 2em 0;

    &__label {
      font-size: 1.2em;
      font-weight: 500;
    }

    &__tag {
      display: flex;
      flex-flow: row wrap;
      align-items: center;
      margin: 0.2em 0.5em;
      padding: 0.2em 0.8em;
      border-radius: 0.8em;
      background: #E9E9E9;
      text-decoration: none;
      background: #F1F1F1;
      border: 1px solid #DBDCDD;
      color: #1D1007;

      &__icon {
        width: 1.4em;
        height: 1.4em;
        margin: 0 0.8em 0 0;
      }

      &__label {
        font-size: 1.2em;
        font-weight: 500;
        text-transform: capitalize;
      }

      &:hover,
      &:focus {
        background: darken(#F1F1F1, 10);
        border: 1px solid darken(#DBDCDD, 10);
      }
    }
  }

  .checkbox {
    display: flex;
    flex-flow: row nowrap;
    font-size: 1.6em;
    align-items: center;
    cursor: pointer;

    &--disabled {
      color: pink;
    }

    &__checkmark .icon__check__path {
      stroke: #DBDCDD;
    }

    &__input {
      display: none;

      &:focus + .checkbox__checkmark {
        stroke: darken(#005226, 10)
      }

      &:checked + .checkbox__checkmark {
        .icon__check__path {
          stroke: #005226;
        }
      }

      &:disabled + .checkbox__checkmark {
        stroke: pink;
      }
    }
  }
}
</style>
