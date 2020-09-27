<template>
  <div>
      <slot></slot>
  </div>
</template>
<script>
export default {
  data () {
    return {
      children: null,
      numChildren: null,
      intervalID: null,
      prevChildIdx: null,
      currChildIdx: null,
    }
  },
  mounted () {
    this.children = this.$el.childNodes
    this.numChildren = this.children.length

    if (this.numChildren > 0) {
      this.hideAllChildren()
      this.startInterval()
    }
  },
  beforeDestroy () {
    this.stopInterval()
  },
  methods: {
    hideAllChildren () {
      for (let i = 0; i < this.numChildren; i += 1) {
        const childEl = this.children[i]
        childEl.style.display = 'none'
      }
    },
    startInterval () {
      const self = this
      this.intervalID = window.setInterval(() => {
        if (
          self.prevChildIdx !== null &&
          typeof self.children[self.prevChildIdx] !== 'undefined'
        ) {
          self.children[self.prevChildIdx].style.display = 'none'
        }

        if (
          self.prevChildIdx === null ||
          self.prevChildIdx + 1 >= self.numChildren
        ) {
          self.currChildIdx = 0
        } else {
          self.currChildIdx = self.prevChildIdx + 1
        }

        self.children[self.currChildIdx].style.display = 'block'
        self.prevChildIdx = self.currChildIdx
      }, 500)
    },
    stopInterval () {
      window.clearInterval(this.intervalID)
    }
  }
}
</script>
