<template>
  <div class="recipe-tree">
    <div
      class="recipe-tree__level"
      v-for="(nodes, level) in treeByLevels"
      :key="level">
      <div
        v-for="(node, index) in nodes"
        :key="index"
        class="recipe-tree__node"
        :class="[{
          'recipe-tree__node--is-selected': node.selected,
          'recipe-tree__node--is-selectable': getIsSelectable(level),
          'recipe-tree__node--is-open': visiblePath[level] === index,
        }]"
        tabindex="0"
        @click="handleNodeClick(level, index, node)"
        @keyup.enter="handleNodeClick(level, index, node)">
        <input
          class="recipe-tree__node__checkbox"
          type="checkbox"
          :checked="node.selected"
          disabled="true" />

        <div v-if="Array.isArray(node)">
          <b>Array of nodes! fix me</b>
        </div>
        <div
          v-else
          class="recipe-tree__node__label">
          <img
            class="recipe-tree__node__icon"
            :src="getItemImage(node.name)" />
            {{ getTitle(node.name) }}
        </div>

        <div v-if="getNextLevel(node).length > 0">
          <span v-if="Array.isArray(node)">
            {{ node.length }} options
          </span>
          <span v-else-if="node.num_recipes > 1">
            {{ node.num_recipes }} recipes
          </span>
          <span v-else-if="node.num_recipes == 1">
            {{ node.recipes[0].ingredients.length }} ingredient{{node.recipes[0].ingredients.length === 1 ? '' : 's'}}
          </span>
          <span v-else-if="node.ingredients && node.ingredients.length > 0">
            {{ node.ingredients.length }} ingredient{{ node.ingredients.length === 1 ? '' : 's' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
<script>
export default {
  props: {
    tree: Array,
  },
  data () {
    return {
      visiblePath: [],
      treeByLevels: []
    }
  },
  mounted () {
    this.treeByLevels.push(this.tree)
  },
  methods: {
    getIsSelectable (level) {
      const parentLevel = level - 1

      if (parentLevel < 0) {
        return false
      }

      const parentNodeIdx = this.visiblePath[level - 1]
      const parentNode = this.treeByLevels[parentLevel][parentNodeIdx]
      const isParentArray = Array.isArray(parentNode)
      const isParentMultiRecipe = parentNode.num_recipes > 1

      return isParentArray || isParentMultiRecipe
    },
    toggleTree (level, index, node) {
      const isAlreadyVisible = this.visiblePath[level] === index

      this.treeByLevels.splice(level + 1, this.treeByLevels.length - level + 1)
      this.visiblePath.splice(level, this.visiblePath.length - level)

      if (isAlreadyVisible) {
        return
      }

      const nextLevel = this.getNextLevel(node)

      if (nextLevel.length === 0) {
        return
      }

      this.treeByLevels.push(nextLevel)
      this.visiblePath.push(index)
    },

    handleNodeClick (level, index, node) {
      this.toggleTree(level, index, node)

      if (!this.getIsSelectable(level)) {
        return
      }

      this.$emit('update', this.updateTreeByPath(level, index))
    },

    updateTreeByPath (level, index, tree, currLevel) {
      currLevel = currLevel || 0

      if (typeof tree === 'undefined') {
        tree = this.tree.slice(0)
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

      const currNodeIdx = this.visiblePath[currLevel]
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

    getNextLevel (node) {
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

    getTitle (item) {
      return item.split('_').join(' ')
    },

    getItemImage (item) {
      const images = require.context('../assets/minecraft/1.15/32x32/', false, /\.png$/)
      try {
        return images(`./${item}.png`)
      } catch (error) {
        return images('./air.png')
      }
    },
  }
}
</script>
<style lang="scss" scoped>
.recipe-tree {
  display: flex;
  flex-flow: row nowrap;
  font-size: 1.6em;
  width: 100%;

  &__level {
    flex: 0 0 auto;
    width: 30vw;
    height: 100%;
    overflow: auto;
  }

  &__node {
    margin: 0.4em 0;
    border: 4px solid transparent;

    &__checkbox {
      display: none;
    }

    &__icon {
      margin: 0 0.5em 0 0;
    }

    &__label {
      display: flex;
      flex-flow: row nowrap;
      align-items: center;
      justify-content: left;
      text-transform: capitalize;
    }

    &--is-selectable {
      opacity: 0.4;

      &.recipe-tree__node--is-selected {
        opacity: 1;
        background: yellow;
      }
    }

    &--is-open {
      border: 4px solid green;
    }
  }
}
</style>
