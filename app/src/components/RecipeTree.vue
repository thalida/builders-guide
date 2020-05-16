<template>
  <div
    class="recipe-tree"
    :class="[
      {'recipe-tree--is-group': optionGroup}
    ]">
    <div
      class="recipe-tree__node"
      v-for="(node, ni) in tree"
      :key="ni">

      <label v-if="optionGroup">
        <input
          type="radio"
          v-model="selectedNode"
          :value="ni" />
          {{ node.name }}
      </label>
      <label v-else-if="!Array.isArray(node)">
        <input
          type="checkbox"
          v-model="node.selected"
          disabled="true" />
          {{ node.name }}
      </label>

      <!-- Option group of items -->
      <!-- Should only be able to select one from this group -->
      <recipe-tree
        v-if="Array.isArray(node)"
        :parent-idx="ni"
        :tree="node"
        :option-group="true"
        @update="handleTreeUpdate">
      </recipe-tree>

      <!-- Has multiple recipes -->
      <div v-else-if="node.num_recipes > 1">
        <span class="recipe-tree__node-toggle" @click="toggleChildren(ni)">{{ node.num_recipes }} recipes</span>
        <recipe-tree
          v-if="showChildren[ni]"
          :parent-idx="ni"
          :tree="node.recipes"
          :option-group="true"
          @update="handleTreeUpdate">
        </recipe-tree>
      </div>

      <!-- Has one recipe, so directly start showing ingredients -->
      <div v-else-if="node.num_recipes == 1">
        <span class="recipe-tree__node-toggle" @click="toggleChildren(ni)">{{ node.recipes[0].ingredients.length }} ingredients</span>
        <recipe-tree
          v-if="showChildren[ni]"
          :parent-idx="ni"
          :tree="node.recipes[0].ingredients"
          @update="handleTreeUpdate">
        </recipe-tree>
      </div>

      <!-- For each ingredient show it's tree -->
      <div v-else-if="node.ingredients && node.ingredients.length > 0">
        <span class="recipe-tree__node-toggle" @click="toggleChildren(ni)">{{ node.ingredients.length }} ingredients</span>
        <recipe-tree
          v-if="showChildren[ni]"
          :parent-idx="ni"
          :tree="node.ingredients"
          @update="handleTreeUpdate">
        </recipe-tree>
      </div>

    </div> <!-- End Node Loop -->
  </div> <!-- End Tree -->
</template>
<script>
export default {
  props: {
    parentIdx: Number,
    tree: Array,
    optionGroup: Boolean,
  },
  name: 'recipe-tree',
  data () {
    return {
      showChildren: new Array(this.tree.length),
      selectedNode: null,
    }
  },
  computed: {},
  watch: {
    selectedNode (newVal) {
      if (!this.optionGroup) {
        return
      }

      for (let i = 0, l = this.tree.length; i < l; i += 1) {
        const newNode = this.tree[i]
        newNode.selected = (newVal === i)
        this.tree.splice(i, 1, newNode)

        if (!newNode.selected) {
          this.showChildren[i] = false
        }
      }

      this.$emit('update', {
        parentIdx: this.parentIdx,
        tree: this.tree,
      })
    }
  },
  mounted () {
    if (this.optionGroup) {
      for (let i = 0, l = this.tree.length; i < l; i += 1) {
        const node = this.tree[i]
        if (node.selected) {
          this.selectedNode = i
          break
        }
      }
    }
  },
  methods: {
    handleTreeUpdate ({ parentIdx, tree }) {
      const node = this.tree[parentIdx]

      if (node.num_recipes > 1) {
        node.recipes = tree
      } else if (node.num_recipes === 1) {
        node.recipes[0].ingredients = tree
      } else if (node.ingredients && node.ingredients.length > 0) {
        node.ingredients = tree
      }

      this.tree.splice(parentIdx, 1, node)

      this.$emit('update', {
        parentIdx: this.parentIdx,
        tree: this.tree,
      })
    },
    toggleChildren (ni) {
      if (typeof this.showChildren[ni] === 'undefined') {
        this.showChildren[ni] = false
      }

      this.showChildren.splice(ni, 1, !this.showChildren[ni])

      if (this.showChildren[ni] === true) {
        this.selectedNode = ni
      }
    },
    setChildren (ni, isVisible) {
      this.showChildren[ni] = isVisible
    }
  },
}
</script>
<style lang="scss" scoped>
.recipe-tree {
  display: flex;
  justify-content: center;
  flex-flow: column nowrap;
  width: 100vw;
  overflow: auto;

  &__node {
    display: flex;
    flex: 1 0 auto;
    flex-flow: column nowrap;
    margin: 15px 0;
    background: rgba(0,0,0,0.1);
  }

  &__node-toggle {
    cursor: pointer;
  }

  &--is-group {
    flex: 1 0 auto;
    flex-flow: row nowrap;
    justify-content: left;
  }

}
</style>
