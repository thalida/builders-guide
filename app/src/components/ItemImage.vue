<template>
<transition-group
  name="fade"
  tag="div"
  class="item-image">
  <img
    v-for="(img, i) in images"
    v-show="img.name !== 'air' && i === visibleIdx"
    class="item-image__img"
    :key="`item-${i}`"
    :src="img.path"
    :alt="img.label"
    :width="`${size}px`"
    :height="`${size}px`" />
</transition-group>
</template>
<script>
import { getItemLabel } from '@/helpers.js'

export default {
  name: 'ItemImage',
  props: {
    item: [String, Array, Object],
    size: {
      type: Number,
      default: 32
    },
    decorative: {
      type: Boolean,
      default: false
    },
  },
  data () {
    return {
      intervalID: null,
      visibleIdx: 0,
    }
  },
  computed: {
    selectedVersion () {
      return this.$store.state.selectedVersion
    },
    items () {
      return (Array.isArray(this.item)) ? this.item : [this.item]
    },
    images () {
      const images = []

      for (let i = 0, l = this.items.length; i < l; i += 1) {
        const item = this.items[i]
        const image = this.getItemImage(item)
        const label = (!this.decorative) ? this.getItemLabel(item) : ''
        images.push({ ...image, label })
      }

      return images
    },
  },
  mounted () {
    this.startInterval()
  },
  updated () {
    this.stopInterval()
    this.startInterval()
  },
  beforeDestroy () {
    this.stopInterval()
  },
  methods: {
    getItemLabel,

    fetchImagePath (imageName) {
      const images = require.context('@/assets/minecraft', true, /\.png$/)
      const path = `./${this.selectedVersion}/${this.size}x${this.size}/${imageName}.png`
      return images(path)
    },

    getItemImage (node, attempt) {
      let imageName
      attempt = attempt || 1

      if (attempt === 1) {
        imageName = (typeof node === 'object') ? node.key || node.name : node
      } else if (attempt === 2 && typeof node === 'object') {
        imageName = node.result_name
      } else {
        imageName = 'air'
      }

      try {
        const path = this.fetchImagePath(imageName)
        return { name: imageName, path }
      } catch (error) {
        return this.getItemImage(node, attempt + 1)
      }
    },

    startInterval () {
      if (this.items.length <= 1) {
        return
      }

      const self = this
      this.intervalID = window.setInterval(() => {
        const newVisibleIdx = (self.visibleIdx + 1 < self.items.length) ? self.visibleIdx + 1 : 0
        self.visibleIdx = newVisibleIdx
      }, 1000)
    },

    stopInterval () {
      window.clearInterval(this.intervalID)
    }
  }
}
</script>
<style lang="scss">
.item-image {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;

  &__img {
    display: block;
    position: absolute;
    top: 0;
    left: 0;
    margin: 0;
    width: 100%;
    height: 100%;
  }

  .fade-enter,
  .fade-leave-to  {
    opacity: 0;
  }

  .fade-enter-active,
  .fade-leave-active {
    transition: all 500ms ease;
  }
}
</style>
