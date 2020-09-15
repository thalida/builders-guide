<template>
  <router-view/>
</template>

<style lang="scss">
// @import './assets/css/_variables';
// @import './assets/css/normalize';
// body
// Base body styles including hiding scrollbars when modal is visible
// -----------------------------------------------------------------------------
html {
  box-sizing: border-box;
}
*, *:before, *:after {
  box-sizing: inherit;
}

html,
body {
  height: 100%;
  width: 100%;
  padding: 0;
  margin: 0;
}

body {
  font: normal normal 62.5%/1.2 'Jost', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;

  background: #fff;
  color: rgba(82, 77, 71, 1);
}

.body--with-modal {
  overflow: hidden;
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

ol {
  display: block;
  list-style-type: none;
  margin: 0;
  padding: 0;
}

h1,
h2,
h3,
h4,
h5,
p {
  margin: 0;
  padding: 0;
}

a.link {
  position: relative;
  color: rgba(82, 77, 71, 1);
  text-decoration: none;

  &:after {
    content: "";
    display: block;
    position: absolute;
    height: 0.05em;
    width: 100%;
    background: rgba(82, 77, 71, 1);
    transition: height 300ms;
  }

  &:hover {
    &:after {
      height: 0.15em;
    }
  }
}

@media screen and (max-width: 500px) {
  body {
    font-size: 80%;
  }
}

</style>
