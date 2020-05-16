<template>
  <div class="recipe-tree">
    <div
      class="recipe-tree__node"
      v-for="(node, ni) in tree"
      :key="ni">

      <!-- Option group of items -->
      <!-- Should only be able to select one from this group -->
      <div v-if="Array.isArray(node)">
        <recipe-tree :tree="node" :option-group="true"></recipe-tree>
      </div>
      <div v-else>
        <label>
          <input
            type="checkbox"
            v-model="node.selected"
            :disabled="!optionGroup" />
            {{ node.name }}
        </label>

        <!-- Has multiple recipes -->
        <div v-if="node.num_recipes > 1">
          <span class="recipe-tree__node-toggle" @click="toggleChildren(ni)">{{ node.num_recipes }} recipes</span>
          <recipe-tree
            v-if="showChildren[ni]"
            :tree="node.recipes">
          </recipe-tree>
        </div>

        <!-- Has one recipe, so directly start showing ingredients -->
        <div v-else-if="node.num_recipes == 1">
          <span class="recipe-tree__node-toggle" @click="toggleChildren(ni)">{{ node.recipes[0].ingredients.length }} ingredients</span>
          <recipe-tree
            v-if="showChildren[ni]"
            :tree="node.recipes[0].ingredients">
          </recipe-tree>
        </div>

        <!-- For each ingredient show it's tree -->
        <div v-else-if="node.ingredients && node.ingredients.length > 0">
          <span class="recipe-tree__node-toggle" @click="toggleChildren(ni)">{{ node.ingredients.length }} ingredients</span>
          <recipe-tree
            v-if="showChildren[ni]"
            :tree="node.ingredients">
          </recipe-tree>
        </div>
      </div>
    </div>

  </div>
</template>
<script>
export default {
  props: {
    tree: Array,
    optionGroup: Boolean,
  },
  name: 'recipe-tree',
  data () {
    return {
      // selectedNode: (this.optionGroup) ? this.tree[0].name : null,
      showChildren: new Array(this.tree.length),
    }
  },
  computed: {},
  methods: {
    toggleChildren (ni) {
      if (typeof this.showChildren[ni] === 'undefined') {
        this.showChildren[ni] = false
      }

      this.showChildren.splice(ni, 1, !this.showChildren[ni])
    },
  },
  mounted () {
    console.log(this.optionGroup, this.tree)
  }
}
</script>
<style lang="scss" scoped>
.recipe-tree {
  background: rgba(0,0,0,0.1);

  &__node {
    margin: 15px 0;
  }

  &__node-toggle {
    cursor: pointer;
  }
}
</style>
