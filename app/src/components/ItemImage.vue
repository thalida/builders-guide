<template>
<img :src="itemImageSrc" />
</template>
<script>
export default {
  name: 'ItemImage',
  props: ['item', 'size'],
  computed: {
    selectedVersion () {
      return this.$store.state.selectedVersion
    },
    itemImageSrc () {
      return this.getItemImage(this.item)
    }
  },
  methods: {
    fetchImage (image) {
      const images = require.context('@/assets/minecraft', true, /\.png$/)
      const path = `./${this.selectedVersion}/${this.size}x${this.size}/${image}.png`
      return images(path)
    },

    getItemImage (node, attempt) {
      let image
      attempt = attempt || 1

      if (attempt === 1) {
        image = (typeof node === 'object') ? node.key || node.name : node
      } else if (attempt === 2 && typeof node === 'object') {
        image = node.result_name
      } else {
        image = 'air'
      }

      try {
        return this.fetchImage(image)
      } catch (error) {
        return this.getItemImage(node, attempt + 1)
      }
    }
  }
}
</script>
