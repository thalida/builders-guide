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

.wordmark {
  margin: 0.4em 0;
  font: 4.8em/1.2 'Grand Hotel', cursive;
  color: #1D1007;
  text-decoration: none;

  &--minimal {
    font-size: 2.4em;

    &:hover {
      color: rgba(12, 136, 68, 1);
    }
  }
}

h1 {
  font-size: 1.6em;
  font-weight: 500;
  text-align: center;
}

.font-weight--medium {
  font-weight: 500;
}

a.link {
  position: relative;
  font-size: 1.4em;
  color: rgba(12, 136, 68, 1);
  // color: rgba(82, 77, 71, 1);
  text-decoration: none;

  // &:after {
  //   content: "";
  //   display: block;
  //   position: absolute;
  //   height: 0.05em;
  //   width: 100%;
  //   background: rgba(82, 77, 71, 1);
  //   transition: height 300ms;
  // }

  &:hover {
    text-decoration: underline;
    // &:after {
    //   height: 0.15em;
    // }
  }
}

@media screen and (max-width: 500px) {
  body {
    font-size: 80%;
  }
}

</style>
