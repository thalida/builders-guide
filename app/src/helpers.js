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
