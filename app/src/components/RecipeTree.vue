<template>
  <div
    class="recipe"
    :class="[
      {'recipe--is-multi-select': isMultiSelect }
    ]">

    <div
      class="recipe__node"
      v-if="!hasMultipleOptions">
      <label @click="toggleSelected">
        <input
          type="checkbox"
          :checked="node.selected"
          disabled="true" />
          {{ node.name }}
      </label>
      {{ node.type }}
      <span class="recipe__toggle" @click="toggleTree">
        <span v-if="node.num_recipes > 1">
          {{ node.num_recipes }} recipes
        </span>
        <span v-else-if="node.num_recipes == 1">
          {{ node.recipes[0].ingredients.length }} ingredients
        </span>
        <span v-else-if="node.ingredients && node.ingredients.length > 0">
          {{ node.ingredients.length }} ingredients
        </span>
      </span>
    </div>

    <div
      v-show="showTree || hasMultipleOptions"
      v-if="tree.length > 0"
      class="recipe__tree"
      :class="[
        {'recipe__tree--is-group': isOptionGroup}
      ]">
      <recipe-tree
        v-for="(childNode, ni) in tree"
        ref="children"
        :key="`${path}${ni}`"
        :path="`${path}${ni}`"
        :level="level + 1"
        :parent-idx="ni"
        :node="childNode"
        :is-multi-select="isOptionGroup"
        @select="onSelect"
        @update="onTreeUpdate">
      </recipe-tree>
    </div>
  </div> <!-- End Tree -->
</template>
<script>
export default {
  props: {
    parentIdx: Number,
    path: String,
    level: Number,
    node: [Object, Array],
    isMultiSelect: Boolean,
  },
  name: 'recipe-tree',
  data () {
    return {
      showTree: false,
    }
  },
  computed: {
    hasParent () {
      return typeof this.parentIdx !== 'undefined'
    },
    hasMultipleOptions () {
      return Array.isArray(this.node)
    },
    hasManyRecipes () {
      if (this.hasMultipleOptions) {
        return false
      }

      return this.node.num_recipes > 1
    },
    isOptionGroup () {
      return this.hasParent && (this.hasMultipleOptions || this.hasManyRecipes)
    },
    isSelected () {
      return (this.isMultiSelect) ? this.node.selected : false
    },
    tree: {
      get () {
        let tree = []

        if (Array.isArray(this.node)) {
          tree = this.node
        } else if (this.node.num_recipes > 1) {
          tree = this.node.recipes
        } else if (this.node.num_recipes === 1) {
          tree = this.node.recipes[0].ingredients
        } else if (this.node.ingredients && this.node.ingredients.length > 0) {
          tree = this.node.ingredients
        }

        return tree
      },
      set (newTree) {
        let nodeCopy =
          (Array.isArray(this.node))
            ? this.node.slice(0)
            : Object.assign({}, this.node)

        if (this.hasMultipleOptions && !Array.isArray(newTree)) {
          newTree = [newTree]
        }

        if (Array.isArray(this.node)) {
          nodeCopy = newTree
        } else if (this.node.num_recipes > 1) {
          nodeCopy.recipes = newTree
        } else if (this.node.num_recipes === 1) {
          nodeCopy.recipes[0].ingredients = newTree
        } else if (this.node.ingredients && this.node.ingredients.length > 0) {
          nodeCopy.ingredients = newTree
        }

        this.$emit('update', { tree: nodeCopy, parentIdx: this.parentIdx })
      }
    },
  },
  mounted () {},
  methods: {
    toggleSelected () {
      if (!this.isMultiSelect) {
        return
      }

      this.$emit('select', {
        nodeName: this.node.name,
        state: !this.node.selected,
      })
    },
    onSelect ({ nodeName, state }) {
      const treeCopy = this.tree.slice(0)
      for (let i = 0, l = treeCopy.length; i < l; i += 1) {
        treeCopy[i].selected = (treeCopy[i].name === nodeName)
      }
      this.tree = treeCopy
    },
    onTreeUpdate ({ tree, parentIdx }) {
      const treeCopy = this.tree.slice(0)
      treeCopy[parentIdx] = tree
      this.tree = treeCopy
    },
    toggleTree () {
      if (this.showTree) {
        this.collapseTree()
      } else {
        this.expandTree()
      }
    },
    collapseTree (cascade) {
      this.showTree = false

      const children = this.$refs.children
      if (cascade && typeof children !== 'undefined') {
        this.$refs.children.forEach((c) => c.collapseTree(cascade))
      }
    },
    expandTree (cascade) {
      this.showTree = true

      const children = this.$refs.children
      if (cascade && typeof children !== 'undefined') {
        this.$refs.children.forEach((c) => c.expandTree(cascade))
      }
      if (!cascade && this.isMultiSelect) {
        this.$emit('select', {
          nodeName: this.node.name,
          state: this.showTree,
        })
      }
    }
  },
}
</script>
<style lang="scss" scoped>
.recipe {
  &--is-multi-select {
    width: auto;
  }

  &__node {
    display: flex;
    flex: 1 0 auto;
    justify-content: left;
    flex-flow: column nowrap;
    margin: 15px 0;
  }

  &__tree {
    display: flex;
    flex-flow: column nowrap;
    justify-content: left;
    width: 100vw;
    overflow: auto;
    background: rgba(0,0,0,0.1);

    &--is-group {
      flex: 1 0 auto;
      flex-flow: row nowrap;
    }
  }
}
</style>
