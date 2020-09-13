<template>
  <div id="cookbook__build">
    <select>
      <option>v1.15.2</option>
    </select>

    <div class="build-menu">
      <input
        type="text"
        v-model="searchTerm"
        placeholder="What do you need?"
        v-on:focus="goToSearch" />

      <router-link to="/cookbook/build/freeform">F</router-link>
    </div>

    <div v-if="hasSelectedItems">
      <button v-on:click="removeAllItems()">clear all</button>
      <div
        class="item-row"
        v-for="(item, i) in selectedItems"
        :key="item.key">
        <input type="number" min="0" v-model.number="selectedItems[i].amount_required" />
        <img :src="getItemImage(item.key)" />
        {{item.key}}
        <a :href="`https://minecraft.gamepedia.com/${item.name}`" target="_blank">Minecraft Wiki</a>
        <button v-on:click="removeSelectedItem(i)">x</button>
      </div>
    </div>
    <div v-else>
      <p>Search for something to create</p>
      <p>or</p>
      <a href>Randomly Pick an Item</a>
    </div>

    <!-- Router view for modals -->
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'CookbookBuild',
  components: {},
  data () {
    return {
      searchTerm: null
    }
  },
  computed: {
    selectedItems () {
      return this.$store.state.selectedItems
    },
    hasSelectedItems () {
      return this.selectedItems.length > 0
    },
  },
  watch: {
    selectedItems: {
      deep: true,
      handler (newVal) {
        this.$store.commit('setSelectedItems', newVal)
        this.$store.dispatch('setupRecipeTree')
      }
    }
  },
  methods: {
    getItemImage (item) {
      const images = require.context('../../../assets/minecraft/1.15/32x32/', false, /\.png$/)
      try {
        return images(`./${item}.png`)
      } catch (error) {
        return images('./air.png')
      }
    },
    removeAllItems () {
      this.selectedItems.splice(0, this.selectedItems.length)
    },
    removeSelectedItem (i) {
      this.selectedItems.splice(i, 1)
    },
    goToSearch () {
      const q = this.searchTerm
      this.searchTerm = null

      let query = {}
      if (typeof q === 'string' && q.length > 0) {
        query = { q }
      }

      this.$router.push({ path: '/cookbook/build/search', query })
    }
  }
}
</script>

<style lang="scss" scoped></style>
