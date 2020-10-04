import createClone from 'rfdc'

export const clone = createClone()

export const ITEM_ALIASES = {
  writable_book: 'book_and_quill',
  heavy_weighted_pressure_plate: 'iron_pressure_plate',
  light_weighted_pressure_plate: 'gold_pressure_plate'
}

export function getImage (image) {
  const images = require.context('./assets/minecraft/1.15/32x32/', false, /\.png$/)
  return images(`./${image}.png`)
}

export function getItemImage (node, attempt) {
  const fallbackImg = 'air'

  if (typeof node === 'string') {
    try {
      return getImage(node)
    } catch (error) {
      return getImage(fallbackImg)
    }
  }

  attempt = attempt || 1
  const maxAttempts = 2
  let image = null

  if (attempt === 1) {
    image = node.name
  } else {
    image = node.result_name
  }

  try {
    return getImage(image)
  } catch (error) {
    if (attempt < maxAttempts) {
      return getItemImage(node, attempt + 1)
    }

    return getImage(fallbackImg)
  }
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

        if (typeof phraseIdx === 'undefined') {
          phraseIdxMap[phrase] = phraseCounts.length
          phraseCounts.push({
            phrase,
            distFromEnd,
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
    if (a.count > b.count) return -1
    if (a.count < b.count) return 1

    if (a.distFromEnd < b.distFromEnd) return -1
    if (a.distFromEnd > b.distFromEnd) return 1

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
}

export function createBuildPaths (recipeTree, isGroup) {
  recipeTree = clone(recipeTree)
  const path = []

  for (let i = 0, l = recipeTree.length; i < l; i += 1) {
    const node = recipeTree[i]

    if (Array.isArray(node)) {
      const chosenNode = createBuildPaths(node, true)
      path.push(chosenNode[0])
      continue
    }

    if (!node.selected) {
      continue
    }

    const nodeCopy = Object.assign({}, node)

    if (nodeCopy.num_recipes >= 1) {
      nodeCopy.recipes = createBuildPaths(nodeCopy.recipes, true)
    } else if (nodeCopy.ingredients && nodeCopy.ingredients.length > 0) {
      nodeCopy.ingredients = createBuildPaths(nodeCopy.ingredients)
    }

    path.push(nodeCopy)

    if (isGroup) {
      break
    }
  }

  return path
}

export function restoreSelectedItems (recipeTree, selectedBuildPaths, isOptionGroup, hasParent) {
  isOptionGroup = (typeof isOptionGroup === 'boolean') ? isOptionGroup : false
  hasParent = hasParent || false

  const updatedTree = clone(recipeTree)
  let selectedNode = (isOptionGroup) ? selectedBuildPaths : null
  let defaultNodeIdx = null
  let foundSelectedNode = null

  for (let i = 0, l = updatedTree.length; i < l; i += 1) {
    let node = updatedTree[i]

    if (!isOptionGroup) {
      selectedNode = selectedBuildPaths[i]
    }

    if (Array.isArray(node)) {
      const isGroup = hasParent
      const treatAsChild = hasParent
      node = restoreSelectedItems(node, selectedNode, isGroup, treatAsChild)
      continue
    }

    if (typeof selectedNode === 'undefined') {
      break
    }

    if (isOptionGroup) {
      defaultNodeIdx = (node.selected) ? i : null
      node.selected = selectedNode.name === node.name
      foundSelectedNode = foundSelectedNode || node.selected
    }

    if (!node.selected) {
      continue
    }

    if (node.num_recipes >= 1) {
      node.recipes = restoreSelectedItems(node.recipes, selectedNode.recipes[0], true, true)
    } else if (node.ingredients && node.ingredients.length > 0) {
      node.ingredients = restoreSelectedItems(node.ingredients, selectedNode.ingredients, false, true)
    }
  }

  if (
    foundSelectedNode !== null &&
    !foundSelectedNode &&
    updatedTree.length > 0
  ) {
    let node = updatedTree[defaultNodeIdx]

    if (typeof node === 'undefined') {
      node = updatedTree[0]
    }

    node.selected = true
  }

  return updatedTree
}
