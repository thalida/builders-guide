import createClone from 'rfdc'

export const clone = createClone()

export const ITEM_ALIASES = {
  writable_book: 'book_and_quill',
  heavy_weighted_pressure_plate: 'iron_pressure_plate',
  light_weighted_pressure_plate: 'gold_pressure_plate'
}

export function getItemLabel (nodes, useAlias) {
  if (typeof useAlias !== 'boolean') {
    useAlias = true
  }

  if (!Array.isArray(nodes)) {
    let name = null
    if (typeof nodes === 'string') {
      name = nodes
    } else if (typeof nodes === 'object' && nodes !== null) {
      name = nodes.name || nodes.tag
    }

    if (name === null) {
      return
    }

    if (useAlias) {
      const alias = ITEM_ALIASES[name]
      if (typeof alias === 'string') {
        name = alias
      }
    }

    return name.split('_').join(' ')
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

    let name = null
    const alias = ITEM_ALIASES[node.name]
    if (useAlias && typeof alias === 'string') {
      name = alias
    } else {
      name = node.name
    }

    const nameParts = name.split('_')
    for (let startIdx = 0; startIdx < nameParts.length; startIdx += 1) {
      for (let endIdx = startIdx + 1; endIdx <= nameParts.length; endIdx += 1) {
        const phrase = nameParts.slice(startIdx, endIdx).join('_')
        const phraseIdx = phraseIdxMap[phrase]
        const distFromEnd = name.length - (name.indexOf(phrase) + phrase.length)
        const numParts = endIdx - startIdx

        if (typeof phraseIdx === 'undefined') {
          phraseIdxMap[phrase] = phraseCounts.length
          phraseCounts.push({
            phrase,
            distFromEnd,
            numParts,
            count: 1,
          })
          continue
        }

        if (distFromEnd < phraseCounts[phraseIdx].distFromEnd) {
          phraseCounts[phraseIdx].distFromEnd = distFromEnd
        }

        phraseCounts[phraseIdx].count += 1
      }
    }
  }

  phraseCounts.sort((a, b) => {
    if (a.distFromEnd < b.distFromEnd) return -1
    if (a.distFromEnd > b.distFromEnd) return 1

    if (a.count > b.count) return -1
    if (a.count < b.count) return 1

    if (a.numParts < b.numParts) return -1
    if (a.numParts > b.numParts) return 1

    if (a.phrase < b.phrase) return -1
    if (a.phrase > b.phrase) return 1
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
}

export function createBuildPaths (recipeTree, isGroup) {
  recipeTree = clone(recipeTree)
  let path = {}

  for (let i = 0, l = recipeTree.length; i < l; i += 1) {
    const node = recipeTree[i]

    if (Array.isArray(node)) {
      const chosenNode = createBuildPaths(node, true)
      path = Object.assign({}, path, chosenNode)
      continue
    }

    if (!node.selected) {
      continue
    }

    const pathNode = {
      name: node.name,
      tag: node.tag,
      selected: node.selected,
      type: node.type,
      amount_required: node.amount_required,
      amount_created: node.amount_created,
    }

    if (node.num_recipes >= 1) {
      const chosenRecipe = createBuildPaths(node.recipes, true)
      pathNode.recipe = Object.values(chosenRecipe)[0]
    } else if (node.ingredients && node.ingredients.length > 0) {
      pathNode.ingredients = createBuildPaths(node.ingredients)
    }

    path[pathNode.name] = pathNode

    if (isGroup) {
      break
    }
  }

  return path
}
