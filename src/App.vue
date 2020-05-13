<template>
  <div id="app">
    <router-view/>
  </div>
</template>

<style lang="scss">
// @import './assets/css/_variables';
// @import './assets/css/normalize';
// body
// Base body styles including hiding scrollbars when modal is visible
// -----------------------------------------------------------------------------
body {
  padding: 0;
  margin: 0;
  // font: normal normal 62.5%/1.2 'Signika', Arial, sans-serif;
  background: white;
  color: black;
}
.body--with-modal {
  overflow: hidden;
}

ol {
  display: block;
  list-style-type: none;
  margin: 0;
  padding: 0;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

#nav {
  padding: 30px;

  a {
    font-weight: bold;
    color: #2c3e50;

    &.router-link-exact-active {
      color: #42b983;
    }
  }
}
</style>
