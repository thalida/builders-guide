<template>
  <div
    class="recipe"
    :class="[
      {'recipe--is-multi-select': isMultiSelect }
    ]">

    <div
      class="recipe__node"
      :class="[{
        'recipe__node--is-selected': node.selected,
        'recipe__node--is-open': showTree,
      }]"
      v-if="!hasMultipleOptions">
      <label
        class="recipe__node__label"
        tabindex="0"
        @click="toggleSelected"
        @keyup.enter="toggleSelected">
        <input
          class="recipe__node__checkbox"
          v-show="isMultiSelect"
          type="checkbox"
          :checked="node.selected"
          disabled="true" />
        <img
          class="recipe__node__icon"
          :src="getItemImage(node.name)" />
          {{ getTitle(node.name) }}
      </label>
      <!-- hi? {{ node.type }} -->
      <div
        class="recipe__node__toggle"
        tabindex="0"
        @click="toggleTree"
        @keyup.enter="toggleTree"
        v-if="tree.length > 0">
        <span v-if="node.num_recipes > 1">
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

    <div
      v-show="showTree || hasMultipleOptions"
      v-if="tree.length > 0"
      class="recipe__tree"
      :class="[
        `recipe__tree--level-${level}`,
        {
          'recipe__tree--is-group': isOptionGroup,
          'recipe__tree--has-multi-options': hasMultipleOptions
        }
      ]">
      <recipe-tree
        v-for="(childNode, ni) in tree"
        ref="children"
        :key="`${path}${ni}`"
        :path="`${path}${ni}`"
        :level="level + 1"
        :is-last-node="ni + 1 === tree.length"
        :parent-idx="ni"
        :node="childNode"
        :is-multi-select="isOptionGroup"
        @select="onSelect"
        @update="onTreeUpdate">
      </recipe-tree>
    </div>

    <hr
      class="recipe__divider"
      v-if="level==1 && !isLastNode" />
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
    isLastNode: Boolean,
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
      return this.node.selected
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
  watch: {
    isSelected (newState) {
      if (newState === false) {
        this.collapseTree(true)
      }
    }
  },
  mounted () {},
  methods: {
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
  // padding: 0 1.0em;

  &--is-multi-select {
    width: auto;
    // margin: 0 0 1.0em 0;
  }

  &__divider {
    width: 100vw;
    margin: 3.0em 0;
    padding: 0;
    border: 5px solid #F1F1F1;

    display: none;
  }

  &__node {
    display: flex;
    flex: 1 0 auto;
    justify-content: center;
    align-items: center;
    flex-flow: column nowrap;
    opacity: 0.4;

    margin: 0 1.0em 2.0em;
    // margin: 15px 0;

    &__checkbox {
      display: none;
    }

    &__label {
      display: flex;
      flex-flow: row nowrap;
      align-items: center;
      justify-content: center;
      background: #F1F1F1;
      border: 1px solid #E9E9E9;
      border-radius: 0.8em;
      padding: 0.5em 1em;
      text-transform: capitalize;
      font-size: 1.6em;
      font-weight: 500;
      white-space: nowrap;
      cursor: pointer;
    }

    &__icon {
      margin: 0 0.5em 0 0;
    }

    &__toggle {
      padding: 0.4em 0.8em;
      font-size: 1.2em;
      font-weight: 500;
      text-align: center;
      background: #E9E9E9;
      color: #524D47;
      cursor: pointer;
      border-radius: 0 0 0.8em 0.8em;
    }

    &--is-selected,
    &--is-open {
      opacity: 1;
    }

    &--is-selected {
      .recipe__node__label {
        background: #FFF;
      }
    }

    &--is-open {
      .recipe__node__label {
        border: 1px solid #63D798;
      }
      .recipe__node__toggle {
        background: #E0F4E9;
      }
    }
  }

  &__tree {
    display: flex;
    // justify-content: left;
    // flex-flow: column nowrap;
    // align-items: center;
    // width: 100vw;
    // overflow-x: auto;
    // overflow-y: hidden;
    flex-flow: row nowrap;
    align-items: start;
    // justify-content: center;
    justify-content: left;
    overflow: auto;

    &--is-group {
      flex: 1 0 auto;
      flex-flow: row nowrap;
      justify-content: left;
      // align-items: center;
    }

    &--has-multi-options {
      flex-flow: column nowrap;
      align-items: center;
    }

    &--level-0 {
      align-items: center;
      // justify-content: center;
      justify-content: start;
    }
  }
}
</style>
