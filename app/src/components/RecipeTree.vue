<template>
  <div class="recipe-tree">
    <div v-if="isLoading"
      class="recipe-tree__loading">
      <recipes-icon class="loading" />
      <p class="recipe-tree__loading__text">
        Gathering all possible recipes and ingredients for {{ numSelectedItems }} items&hellip;
      </p>
    </div>

    <div v-if="!isLoading && isResetting"
      class="recipe-tree__loading">
      <recipes-icon class="loading" />
      <p class="recipe-tree__loading__text">
        Resetting selected recipes and ingredients for {{ numSelectedItems }} items&hellip;
      </p>
    </div>

    <div
      v-if="!isLoading && !isResetting"
      class="recipe-tree__levels">
      <div
        class="recipe-tree__level"
        v-for="(nodes, level) in treeByLevels"
        :key="level">

        <!-- Level Empty State -->
        <div
          v-if="nodes.length === 0"
          class="recipe-tree__node recipe-tree__node--is-empty">
          <chat-alert-icon />
          <p class="recipe-tree__node__alert">This item does not require crafting.</p>
        </div>

        <!-- Loop over all nodes in the level -->
        <div
          v-for="(formattedNode, index) in formatNodes(level, nodes)"
          :key="formattedNode.renderKey"
          class="recipe-tree__node"
          :class="[{
            'recipe-tree__node--is-selected': formattedNode.node.selected,
            'recipe-tree__node--is-open': formattedNode.isOpen,
            'recipe-tree__node--is-optional': formattedNode.isOptional,
            'recipe-tree__node--has-nested': formattedNode.numNestedNodes > 0,
          }]"
          :tabindex="0"
          @click="handleNodeSelected(level, index, formattedNode.node)"
          @keyup.enter="handleNodeSelected(level, index, formattedNode.node)">

          <div class="recipe-tree__node__content">
            <item-image
              :item="formattedNode.node"
              :size="32"
              class="recipe-tree__node__icon" />

            <!-- Node text -->
            <div class="recipe-tree__node__text">
              <p class="recipe-tree__node__label">
                {{ formattedNode.label }}
              </p>
              <div class="recipe-tree__node__requirements">
                {{ formattedNode.requirementsLabel }}
              </div>
            </div>
          </div> <!-- End Node Details -->
        </div> <!-- End Node -->
      </div> <!-- End Level -->
    </div>
  </div> <!-- End Tree -->
</template>
<script>
import { getItemLabel } from '@/helpers.js'
import recipesIcon from '@/components/icons/recipes.vue'
import chatAlertIcon from '@/components/icons/chat-alert.vue'
import ItemImage from '@/components/ItemImage.vue'

export default {
  components: {
    recipesIcon,
    chatAlertIcon,
    ItemImage,
  },
  data () {
    return {
      treeByLevels: [],
      isResetting: false,
      error: null,
    }
  },
  computed: {
    recipeTree: {
      get () {
        return this.$store.state.recipeTree
      },
      set (newTree) {
        this.$store
          .dispatch('updateRecipeTree', newTree)
          .catch((err) => {
            this.error = err
          })
      }
    },
    visiblePath: {
      get () {
        return this.$store.state.visibleBuildPath
      },
      set (newPath) {
        this.$store.dispatch('updateVisibleBuildPath', newPath)
      }
    },
    isLoading () {
      return this.$store.state.requests.fetchRecipeTree.isLoading
    },
    numSelectedItems () {
      return this.$store.state.selectedItems.length
    },
  },
  watch: {
    isLoading (newState, oldState) {
      if (oldState === true && newState === false) {
        this.initTreeLevels(this.recipeTree)
      }
    },
    visiblePath (newPath, oldPath) {
      if (newPath.length + 1 >= this.treeByLevels.length) {
        return
      }

      this.treeByLevels.splice(newPath.length + 1, this.treeByLevels.length)
    }
  },
  mounted () {
    this.initTreeLevels(this.recipeTree)
  },
  methods: {
    initTreeLevels (tree) {
      this.treeByLevels = [tree]

      if (tree.length === 0) {
        return
      }

      let removeLevelsAfter = null

      for (let level = 0; level < this.visiblePath.length; level += 1) {
        const visibleItem = this.visiblePath[level]
        const visibleIdx = visibleItem.index
        const visibleRenderKey = visibleItem.renderKey

        if (
          typeof this.treeByLevels[level] === 'undefined' ||
          typeof this.treeByLevels[level][visibleIdx] === 'undefined'
        ) {
          removeLevelsAfter = level
          break
        }

        const node = this.treeByLevels[level][visibleIdx]
        const label = getItemLabel(node)
        const renderKey = this.getRenderKey(level, label)

        if (renderKey !== visibleRenderKey) {
          removeLevelsAfter = level
          break
        }

        this.handleNodeSelected(level, visibleIdx, node, true)
      }

      if (removeLevelsAfter !== null) {
        const fixedVisiblePath = this.visiblePath.slice(0)
        fixedVisiblePath.splice(removeLevelsAfter, this.visiblePath.length)
        this.visiblePath = fixedVisiblePath
      }
    },
    reset () {
      this.isResetting = this.numSelectedItems > 100
      this.$store.dispatch('resetRecipeTree').then(() => {
        this.treeByLevels = [this.recipeTree]
        setTimeout(() => {
          this.isResetting = false
        }, 0)
      })
    },
    getRenderKey (level, label) {
      return `${level}-${label}`
    },
    formatNodes (level, nodes) {
      const formattedNodes = []
      const isOptional = this.getIsOptional(level)

      for (let i = 0; i < nodes.length; i += 1) {
        const node = nodes[i]
        const isOptionGroup = Array.isArray(node)
        const numNestedNodes = this.getNextLevel(node).length
        const label = getItemLabel(node)
        const renderKey = this.getRenderKey(level, label)
        let requirementsLabel = null

        if (numNestedNodes > 0) {
          let numIngredients = null

          if (isOptionGroup) {
            requirementsLabel = `${numNestedNodes} options`
          } else if (node.num_recipes > 1) {
            requirementsLabel = `${node.num_recipes} recipes`
          } else if (node.num_recipes === 1) {
            numIngredients = node.recipes[0].ingredients.length
          } else if (node.ingredients && node.ingredients.length > 0) {
            numIngredients = node.ingredients.length
          }

          if (numIngredients !== null) {
            const pluralize = (numIngredients === 1) ? '' : 's'
            requirementsLabel = `${numIngredients} ingredient${pluralize}`
          }
        }

        if (!Array.isArray(node)) {
          node.renderKey = renderKey
        }

        const isOpen = (
          typeof this.visiblePath[level] !== 'undefined' &&
          this.visiblePath[level].index === i &&
          this.visiblePath[level].renderKey === renderKey
        )

        formattedNodes.push({
          renderKey,
          isOpen,
          isOptionGroup,
          isOptional,
          numNestedNodes,
          label,
          requirementsLabel,
          node,
        })
      }

      return formattedNodes
    },
    getIsOptional (level) {
      const parentLevel = level - 1

      if (parentLevel < 0) {
        return false
      }

      if (typeof this.visiblePath[level - 1] === 'undefined') {
        return false
      }

      const parentNodeIdx = this.visiblePath[level - 1].index
      const parentNode = this.treeByLevels[parentLevel][parentNodeIdx]
      const isParentArray = Array.isArray(parentNode)
      const isParentMultiRecipe = parentNode.num_recipes > 1

      return isParentArray || isParentMultiRecipe
    },

    handleNodeSelected (level, index, node, isInit) {
      isInit = (typeof isInit === 'boolean') ? isInit : false

      this.toggleTree(level, index, node, isInit)

      const isOptional = this.getIsOptional(level)
      if (!isOptional || isInit) {
        return
      }

      const newTree = this.updateTreeByPath(level, index)
      this.recipeTree = newTree
    },

    toggleTree (level, index, node, isInit) {
      isInit = (typeof isInit === 'boolean') ? isInit : false

      const label = getItemLabel(node)
      const renderKey = this.getRenderKey(level, label)
      const newVisiblePath = this.visiblePath.slice(0)

      if (!isInit) {
        const isAlreadyVisible = (
          typeof this.visiblePath[level] !== 'undefined' &&
          this.visiblePath[level].index === index
        )
        this.treeByLevels.splice(level + 1, this.treeByLevels.length - level + 1)
        newVisiblePath.splice(level, this.visiblePath.length - level)

        if (isAlreadyVisible) {
          this.visiblePath = newVisiblePath
          return
        }
      }

      const nextLevel = this.getNextLevel(node, true)
      this.treeByLevels.push(nextLevel)

      if (isInit) {
        setTimeout(() => {
          const $firstLevel = this.$el.querySelector('.recipe-tree__level')
          const $openItem = $firstLevel.querySelector('.recipe-tree__node--is-open')
          const itemRowTop = $openItem.offsetTop - $firstLevel.offsetTop
          $openItem.focus()
          if (itemRowTop >= $firstLevel.offsetHeight - 10) {
            $firstLevel.scrollTop = itemRowTop - 12
          }
        }, 0)
      } else {
        newVisiblePath.push({
          index,
          renderKey
        })
        this.visiblePath = newVisiblePath
        setTimeout(() => {
          this.$el.scrollLeft = this.$el.scrollWidth - this.$el.clientWidth
        }, 0)
      }
    },

    updateTreeByPath (level, index, tree, currLevel) {
      currLevel = currLevel || 0

      if (typeof tree === 'undefined') {
        tree = this.recipeTree
      }

      if (currLevel > level) {
        return tree
      }

      if (currLevel === level) {
        for (let i = 0, l = tree.length; i < l; i += 1) {
          tree[i].selected = i === index
        }

        return tree
      }

      const currNodeIdx = this.visiblePath[currLevel].index
      let node = tree[currNodeIdx]
      const nextLevel = this.getNextLevel(node)

      if (nextLevel.length === 0) {
        return tree
      }

      const updatedTree = this.updateTreeByPath(level, index, nextLevel, currLevel + 1)
      if (Array.isArray(node)) {
        node = updatedTree
      } else if (node.num_recipes > 1) {
        node.recipes = updatedTree
      } else if (node.num_recipes === 1) {
        node.recipes[0].ingredients = updatedTree
      } else if (node.ingredients && node.ingredients.length > 0) {
        node.ingredients = updatedTree
      }

      tree[currNodeIdx] = node

      return tree
    },

    getNextLevel (node, fullSetup) {
      let level = []
      if (Array.isArray(node)) {
        level = node
      } else if (node.num_recipes > 1) {
        level = node.recipes
      } else if (node.num_recipes === 1) {
        level = node.recipes[0].ingredients
      } else if (node.ingredients && node.ingredients.length > 0) {
        level = node.ingredients
      }

      return level
    },
  }
}
</script>
<style lang="scss">
.recipe-tree {
  display: flex;
  flex-flow: row nowrap;
  width: 100%;
  height: 100%;
  overflow: auto;

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
    }
  }

  &__levels {
    display: flex;
    flex-flow: row nowrap;
    width: 100%;
    height: 100%;
  }

  &__level {
    flex: 0 0 auto;
    padding: 12px 1.0em 0;
    width: 40vw;
    max-width: 300px;
    height: 100%;
    overflow: auto;

    &:first-child {
      margin-left: auto;
    }

    &:last-child {
      margin-right: auto;
    }

    &:nth-child(1):nth-last-child(1) {
      width: 80%;
      max-width: 600px;
      padding-left: 0;
      padding-right: 0;
    }

    &:nth-child(1):nth-last-child(2) {
      padding-left: 0;
    }

    &:nth-child(2):nth-last-child(1) {
      padding-right: 0;
    }
  }

  &__node {
    position: relative;
    margin: 0 0 2em 0;
    padding: 1em;
    border: 1px solid #DBDCDD;
    background: #FFF;
    border-radius: 0.8em;
    transition: all 300ms;
    cursor: pointer;

    &__content {
      display: flex;
      flex-flow: row nowrap;
      align-items: center;
    }

    &__checkbox {
      display: none;
    }

    &__icon {
      flex: 0 0 32px;
      height: 32px;
      width: 32px;
      margin: 0 1em 0 0;

      .item-image__img {
        width: 100%;
      }
    }

    &__label {
      display: flex;
      flex-flow: row nowrap;
      align-items: center;
      justify-content: left;
      text-transform: capitalize;
      font-size: 1.6em;
      font-weight: 500;
      line-height: 1.4;
    }

    &__requirements {
      font-size: 1.4em;
      font-weight: 500;
      color: #005226;
    }

    &--is-empty {
      border: 1px solid transparent;
      cursor: default;

      .icon__chat-alert__path {
        fill: #918C88;
      }
      .recipe-tree__node__alert {
        font-size: 1.6em;
        font-weight: 500;
        color: #918C88;
      }
    }

    &--has-nested {
      .recipe-tree__node__content {
        align-items: start;
      }
    }

    &--is-optional {
      background: #F1F1F1;
      border: 1px solid transparent;

      .recipe-tree__node__requirements {
        color: darken(#005226, 10);
      }

      &.recipe-tree__node--is-selected:not(.recipe-tree__node--is-open) {
        background: #fff;
        border: 1px solid #DBDCDD;

        .recipe-tree__node__requirements {
          color: #005226;
        }
      }
    }

    &--is-open {
      background: #E0F4E9;
      border: 1px solid #4AA674;

      .recipe-tree__node__requirements {
        color: #524D47;
      }

      &:after {
        content: "";
        display: block;
        position: absolute;
        top: 50%;
        left: 100%;
        transform: translate(0, -50%);
        width: 0;
        height: 0;
        border-top: 0.8em solid transparent;
        border-bottom: 0.8em solid transparent;
        border-left: 0.8em solid #4AA674;
      }
    }
  }
}
</style>
