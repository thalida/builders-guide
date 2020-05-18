<template>
  <div
    class="recipe-tree"
    :class="[
      {'recipe-tree--is-group': optionGroup}
    ]">
    <div
      class="recipe-tree__node"
      v-for="(node, ni) in tree"
      :key="`${path}${ni}`">

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
        :path="`${path}${ni}`"
        :tree="node"
        :option-group="true"
        :level="level + 1"
        @update="handleTreeUpdate">
      </recipe-tree>

      <!-- Has multiple recipes -->
      <div v-else-if="node.num_recipes > 1">
        <span class="recipe-tree__node-toggle" @click="toggleChildren(ni)">{{ node.num_recipes }} recipes</span>
        <recipe-tree
          v-if="showChildren[ni]"
          :parent-idx="ni"
          :path="`${path}${ni}`"
          :tree="node.recipes"
          :option-group="true"
          :level="level + 1"
          @update="handleTreeUpdate">
        </recipe-tree>
      </div>

      <!-- Has one recipe, so directly start showing ingredients -->
      <div v-else-if="node.num_recipes == 1">
        <span class="recipe-tree__node-toggle" @click="toggleChildren(ni)">{{ node.recipes[0].ingredients.length }} ingredients</span>
        <recipe-tree
          v-if="showChildren[ni]"
          :parent-idx="ni"
          :path="`${path}${ni}`"
          :tree="node.recipes[0].ingredients"
          :level="level + 1"
          @update="handleTreeUpdate">
        </recipe-tree>
      </div>

      <!-- For each ingredient show it's tree -->
      <div v-else-if="node.ingredients && node.ingredients.length > 0">
        <span class="recipe-tree__node-toggle" @click="toggleChildren(ni)">{{ node.ingredients.length }} ingredients</span>
        <recipe-tree
          v-if="showChildren[ni]"
          :parent-idx="ni"
          :path="`${path}${ni}`"
          :tree="node.ingredients"
          :level="level + 1"
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
    path: String,
    level: Number,
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

      const treeCopy = this.tree.slice(0)
      for (let i = 0, l = treeCopy.length; i < l; i += 1) {
        treeCopy[i].selected = (newVal === i)

        if (!treeCopy[i].selected) {
          this.showChildren[i] = false
        }
      }

      this.$emit('update', {
        parentIdx: this.parentIdx,
        tree: treeCopy,
        optionGroup: this.optionGroup,
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
    handleTreeUpdate ({ parentIdx, tree, optionGroup }) {
      let node = this.tree[parentIdx]
      const treeCopy = this.tree.slice(0)

      if (Array.isArray(node)) {
        node = tree
      } else if (node.num_recipes > 1) {
        node.recipes = tree
      } else if (node.num_recipes === 1) {
        node.recipes[0].ingredients = tree
      } else if (node.ingredients && node.ingredients.length > 0) {
        node.ingredients = tree
      }

      treeCopy[parentIdx] = node

      console.log(parentIdx, treeCopy, optionGroup)

      this.$emit('update', {
        parentIdx: this.parentIdx,
        tree: treeCopy,
        optionGroup: this.optionGroup,
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
