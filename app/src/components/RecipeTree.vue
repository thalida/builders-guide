<template>
  <div class="recipe-tree">
    <div
      class="recipe-tree__level"
      v-for="(nodes, level) in treeByLevels"
      :key="level">
      <div
        v-if="nodes.length === 0"
        class="recipe-tree__node recipe-tree__node--is-empty">
        <chat-alert-icon />
        <p class="recipe-tree__node__alert">This item has no ingredients.</p>
      </div>
      <div
        v-for="(node, index) in nodes"
        :key="index"
        class="recipe-tree__node"
        :class="[{
          'recipe-tree__node--is-selected': node.selected,
          'recipe-tree__node--is-plaintext': !getIsOptional(level) && getNextLevel(node).length === 0,
          'recipe-tree__node--is-optional': getIsOptional(level),
          'recipe-tree__node--has-nested': getNextLevel(node).length > 0,
          'recipe-tree__node--is-open': visiblePath[level] === index,
        }]"
        :tabindex="(getIsOptional(level) || getNextLevel(node).length > 0) ? 0 : -1"
        @click="handleNodeClick(level, index, node)"
        @keyup.enter="handleNodeClick(level, index, node)">
        <input
          class="recipe-tree__node__checkbox"
          type="checkbox"
          :checked="node.selected"
          disabled="true" />

        <div
          class="recipe-tree__node__content"
          v-if="Array.isArray(node)">
          <content-looper class="recipe-tree__node__icon-set">
            <img
              v-for="(nestedNode, nni) in node"
              :key="nni"
              class="recipe-tree__node__icon"
              :src="getItemImage(nestedNode)" />
          </content-looper>

          <div class="recipe-tree__node__text">
            <p class="recipe-tree__node__label">
              {{ getGroupTitle(node) }}
            </p>
            <div class="recipe-tree__node__requirements">
              {{ node.length }} options
            </div>
          </div>
        </div>
        <div
          class="recipe-tree__node__content"
          v-else>
          <img
            class="recipe-tree__node__icon"
            :src="getItemImage(node)" />

          <div class="recipe-tree__node__text">
            <p class="recipe-tree__node__label">
              {{ getTitle(node.name) }}
            </p>

            <div
              v-if="getNextLevel(node).length > 0"
              class="recipe-tree__node__requirements">
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
        </div> <!-- End Node Details -->
      </div> <!-- End Node -->
    </div> <!-- End Level -->
  </div> <!-- End Tree -->
</template>
<script>
import chatAlertIcon from '@/components/icons/chat-alert.vue'
import ContentLooper from '@/components/ContentLooper.vue'

export default {
  props: {
    tree: Array,
  },
  components: {
    chatAlertIcon,
    ContentLooper,
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
    getIsOptional (level) {
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

      const nextLevel = this.getNextLevel(node, true)

      this.treeByLevels.push(nextLevel)
      this.visiblePath.push(index)

      setTimeout(() => {
        this.$el.scrollLeft = this.$el.scrollWidth - this.$el.clientWidth
      }, 0)
    },

    handleNodeClick (level, index, node) {
      const isOptional = this.getIsOptional(level)
      if (!isOptional && this.getNextLevel(node).length === 0) {
        return
      }

      this.toggleTree(level, index, node)

      if (!isOptional) {
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

    getNextLevel (node, fullSetup) {
      let level = []
      if (Array.isArray(node)) {
        level = node
      } else if (node.num_recipes > 1) {
        level = node.recipes
      } else if (node.num_recipes === 1) {
        level = node.recipes[0].ingredients

        if (fullSetup) {
          for (let i = 0; i < level.length; i += 1) {
            level[i].type = node.recipes[0].type
          }
        }
      } else if (node.ingredients && node.ingredients.length > 0) {
        level = node.ingredients
      }

      return level
    },

    getTitle (item) {
      return item.split('_').join(' ')
    },

    getGroupTitle (nodes) {
      const numNodes = nodes.length
      const phraseCounts = {}

      for (let i = 0; i < numNodes; i += 1) {
        const node = nodes[i]

        if (
          typeof node !== 'object' ||
          node === null ||
          typeof node.name === 'undefined'
        ) {
          continue
        }

        const permutations = []
        const nameParts = node.name.split('_')
        for (let j = 0; j < nameParts.length; j += 1) {
          permutations.push(
            nameParts.slice(j, nameParts.length).join('_')
          )

          for (let k = j + 1; k < nameParts.length; k += 1) {
            permutations.push(nameParts.slice(j, k).join('_'))
          }
        }

        for (let pi = 0; pi < permutations.length; pi += 1) {
          const phrase = permutations[pi]
          if (typeof phraseCounts[phrase] === 'undefined') {
            phraseCounts[phrase] = 1
          } else {
            phraseCounts[phrase] += 1
          }
        }
      }

      const sortedPhraseCounts = []
      for (const phrase in phraseCounts) {
        sortedPhraseCounts.push([phrase, phraseCounts[phrase]])
      }

      sortedPhraseCounts.sort((a, b) => {
        if (a[1] > b[1]) return -1
        if (a[1] < b[1]) return 1

        if (a[0].length > b[0].length) return -1
        if (a[0].length < b[0].length) return 1

        if (a[0] > b[0]) return 1
        if (a[0] < b[0]) return -1
      })

      let capturedNodes = 0
      const foundNames = []
      for (let si = 0; si < sortedPhraseCounts.length; si += 1) {
        const phraseCount = sortedPhraseCounts[si]
        const name = phraseCount[0]
        const frequency = phraseCount[1]

        foundNames.push(name.split('_').join(' '))
        capturedNodes += frequency

        if (capturedNodes >= numNodes) {
          break
        }
      }

      return foundNames.join(' / ')
    },

    getItemImage (node, attempt) {
      attempt = attempt || 1
      const maxAttempts = 2
      const images = require.context('../assets/minecraft/1.15/32x32/', false, /\.png$/)
      try {
        let image = null
        if (attempt === 1) {
          image = node.name
        } else {
          image = node.result_name
        }
        return images(`./${image}.png`)
      } catch (error) {
        if (attempt < maxAttempts) {
          return this.getItemImage(node, attempt + 1)
        }

        return images('./air.png')
      }
    },

    getTypeImage (nodeType) {
      const images = require.context('../assets/minecraft/1.15/32x32/', false, /\.png$/)
      let image = null

      if (nodeType === 'minecraft:blasting') {
        image = 'blast_furnace'
      } else if (nodeType === 'minecraft:smelting') {
        image = 'furnace'
      }

      try {
        return images(`./${image}.png`)
      } catch (error) {
        return images('./air.png')
      }
    }
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

  &__level {
    flex: 0 0 auto;
    width: 40vw;
    max-width: 300px;
    height: 100%;
    overflow: auto;
    padding: 12px 1.0em 0;

    &:first-child {
      margin-left: auto;
    }

    &:last-child {
      margin-right: auto;
    }

    &:nth-child(1):nth-last-child(1) {
      width: 80%;
      max-width: 600px;
      padding: 0;
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
    border: 1px solid transparent;
    border-radius: 0.8em;
    transition: all 300ms;

    &__content {
      display: flex;
      flex-flow: row nowrap;
      align-items: center;
    }

    &__checkbox {
      display: none;
    }

    &__type {
      width: 24px;
      height: 24px;
      position: absolute;
      left: 50%;
      transform: translateX(-50%);
      top: -12px;

      &__icon {
        width: 100%;
      }
    }

    &__icon-set {
      position: relative;
      flex: 0 0 32px;
      width: 32px;
      height: 32px;
      margin: 0 1em 0 0;
      overflow: hidden;

      .recipe-tree__node__icon {
        display: block;
        position: absolute;
        top: 0;
        left: 0;
        margin: 0;
      }
    }

    &__icon {
      flex: 0 1 32px;
      height: 32px;
      width: 32px;
      margin: 0 1em 0 0;
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
      color: rgba(12, 136, 68, 1);
    }

    &--is-empty {
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
      background: #FFF;
      border: 1px solid #DBDCDD;
      cursor: pointer;

      .recipe-tree__node__content {
        align-items: start;
      }
    }

    &--is-optional {
      background: #F1F1F1;
      border: 1px solid transparent;
      cursor: pointer;

      .recipe-tree__node__requirements {
        color: darken(rgba(12, 136, 68, 1), 10);
      }

      &.recipe-tree__node--is-selected:not(.recipe-tree__node--is-open) {
        background: #fff;
        border: 1px solid #DBDCDD;

        .recipe-tree__node__requirements {
          color: rgba(12, 136, 68, 1);
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

    &:focus {
      &.recipe-tree__node--is-plaintext {
        outline: none;
      }
    }
  }
}
</style>
