<template>
<div class="item-image">
  <!-- If multiple images -->
  <transition-group
    v-if="numItems > 1"
    name="fade"
    tag="div"
    class="item-image__group">
    <img
      v-for="(nestedItem, i) in item"
      v-show="i === visibleIdx"
      class="item-image__img"
      :key="`item-${i}`"
      :src="getItemImage(nestedItem)" />
  </transition-group>

  <!-- Otherwise render the node image -->
  <img
    v-else
    class="item-image__img"
    :src="getItemImage(item)"  />
</div>
</template>
<script>
export default {
  name: 'ItemImage',
  props: ['item', 'size'],
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
    numItems () {
      return (Array.isArray(this.item)) ? this.item.length : 1
    }
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
    },

    startInterval () {
      if (this.numItems <= 1) {
        return
      }

      const self = this
      this.intervalID = window.setInterval(() => {
        const newVisibleIdx = (self.visibleIdx + 1 < self.numItems) ? self.visibleIdx + 1 : 0
        self.visibleIdx = newVisibleIdx
      }, 3000)
    },

    stopInterval () {
      window.clearInterval(this.intervalID)
    }
  }
}
</script>
<style lang="scss">
.item-image {
  &__group {
    position: relative;
    flex: 0 1 100%;
    width: 100%;
    height: 100%;
    overflow: hidden;

    .item-image__img {
      display: block;
      position: absolute;
      top: 0;
      left: 0;
      margin: 0;
    }
  }

  .fade-enter,
  .fade-leave-to  {
    opacity: 0;
  }

  .fade-enter-active,
  .fade-leave-active {
    transition: all 1000ms ease;
  }
}
</style>
