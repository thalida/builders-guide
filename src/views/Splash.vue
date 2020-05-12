<template>
  <div id="splash">
    <section>
      <h1>builder's guide</h1>
      <h2>A Minecraft Cookbook</h2>
      <p>
        Figure out the recipes and resources you’ll need for your next build!
      </p>
      <router-link to="/cookbook">Plan your build</router-link>
    </section>
    <footer>
      <div class="input">
        <label><input type="checkbox" v-model="skipSplash" /> Don't show this again</label>
      </div>
      <router-link to="/about">About</router-link>
    </footer>
  </div>
</template>

<script>
// @ is an alias to /src
export default {
  name: 'Splash',
  data: () => {
    return {
      checked: true,
      skipSplash: null,
    }
  },
  watch: {
    skipSplash (newValue) {
      this.$localStorage.set('skipSplash', newValue)
    }
  },
  mounted () {
    this.skipSplash = this.$localStorage.get('skipSplash', false, Boolean)
  }
}
</script>
