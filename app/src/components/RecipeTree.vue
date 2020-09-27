<template>
  <div class="recipe-tree">
    <div
      class="recipe-tree__level"
      v-for="(nodes, level) in treeByLevels"
      :key="level">

      <!-- Level Empty State -->
      <div
        v-if="nodes.length === 0"
        class="recipe-tree__node recipe-tree__node--is-empty">
        <chat-alert-icon />
        <p class="recipe-tree__node__alert">This item has no ingredients.</p>
      </div>

      <!-- Loop over all nodes in the level -->
      <div
        v-for="(formattedNode, index) in formatNodes(level, nodes)"
        :key="formattedNode.key"
        class="recipe-tree__node"
        :class="[{
          'recipe-tree__node--is-selected': formattedNode.node.selected,
          'recipe-tree__node--is-open': formattedNode.isOpen,
          'recipe-tree__node--is-plaintext': formattedNode.isStatic,
          'recipe-tree__node--is-optional': formattedNode.isOptional,
          'recipe-tree__node--has-nested': formattedNode.numNestedNodes > 0,
        }]"
        :tabindex="(formattedNode.isStatic) ? -1 : 0"
        @click="handleNodeSelected(level, index, formattedNode.node)"
        @keyup.enter="handleNodeSelected(level, index, formattedNode.node)">

        <div class="recipe-tree__node__content">
          <!-- If this node is an option group loop through all the images -->
          <content-looper
           v-if="formattedNode.isOptionGroup"
           class="recipe-tree__node__icon-set">
            <img
              v-for="(nestedNode, nni) in formattedNode.node"
              :key="nni"
              class="recipe-tree__node__icon"
              :src="getItemImage(nestedNode)" />
          </content-looper>

          <!-- Otherwise render the node image -->
          <img
            v-else
            class="recipe-tree__node__icon"
            :src="getItemImage(formattedNode.node)" />

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
    formatNodes (level, nodes) {
      const formattedNodes = []
      const isOptional = this.getIsOptional(level)

      for (let i = 0; i < nodes.length; i += 1) {
        const node = nodes[i]
        const isOptionGroup = Array.isArray(node)
        const numNestedNodes = this.getNextLevel(node).length
        const label = this.getLabel(node)
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

        formattedNodes.push({
          key: `${level}-${i}-${label}`,
          isStatic: !isOptional && numNestedNodes === 0,
          isOpen: this.visiblePath[level] === i,
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

    handleNodeSelected (level, index, node) {
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
      } else if (node.ingredients && node.ingredients.length > 0) {
        level = node.ingredients
      }

      return level
    },

    getLabel (nodes) {
      if (!Array.isArray(nodes)) {
        if (typeof nodes === 'object' && nodes !== null) {
          return nodes.name.split('_').join(' ')
        } else {
          return null
        }
      }

      const numNodes = nodes.length
      const phraseIdxMap = {}
      const phraseCounts = []

      for (let i = 0; i < numNodes; i += 1) {
        const node = nodes[i]

        if (
          typeof node !== 'object' ||
          node === null ||
          typeof node.name === 'undefined'
        ) {
          continue
        }

        const nameParts = node.name.split('_')
        for (let startIdx = 0; startIdx < nameParts.length; startIdx += 1) {
          for (let endIdx = startIdx + 1; endIdx <= nameParts.length; endIdx += 1) {
            const phrase = nameParts.slice(startIdx, endIdx).join('_')
            const phraseIdx = phraseIdxMap[phrase]

            if (typeof phraseIdx === 'undefined') {
              phraseIdxMap[phrase] = phraseCounts.length
              phraseCounts.push({ phrase, count: 1 })
              continue
            }

            phraseCounts[phraseIdx].count += 1
          }
        }
      }

      phraseCounts.sort((a, b) => {
        if (a.count > b.count) return -1
        if (a.count < b.count) return 1

        if (a.phrase.length > b.phrase.length) return -1
        if (a.phrase.length < b.phrase.length) return 1

        if (a.phrase > b.phrase) return 1
        if (a.phrase < b.phrase) return -1
      })

      let describedNodes = 0
      const foundNames = []
      for (let si = 0; si < phraseCounts.length; si += 1) {
        const phraseCount = phraseCounts[si]

        foundNames.push(phraseCount.phrase.split('_').join(' '))
        describedNodes += phraseCount.count

        if (describedNodes >= numNodes) {
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
      color: #005226;
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

    &:focus {
      &.recipe-tree__node--is-plaintext {
        outline: none;
      }
    }
  }
}
</style>
