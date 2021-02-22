<template>
  <router-view v-if="show" />
</template>

<script>
export default {
  name: 'App',
  data () {
    return {
      show: false
    }
  },
  created () {
    this.$store
      .dispatch('init')
      .then(() => {
        this.show = true
      })
  },
}
</script>

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

  background: #000;
  color: #1D1007;
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

    &:hover,
    &:focus {
      color: #005226;
    }
  }
}

h1 {
  font-size: 1.6em;
  font-weight: 500;
  text-align: center;
}

h2 {
  font-size: 2.2em;
  font-weight: 500;
}

h3 {
  font-size: 1.6em;
  font-weight: 500;
  color: #524D47;
}

.font-weight--medium {
  font-weight: 500;
}

.font-weight--bold {
  font-weight: 700;
}

.font-size--normal {
  font-size: 1.8em;
}

a.link {
  cursor: pointer;
  position: relative;
  font-size: 1.4em;
  color: #005226;
  text-decoration: none;
  font-weight: 500;

  &:hover,
  &:focus {
    text-decoration: underline;
  }
}

.item-title {
  font-size: 1.6em;
  font-weight: 500;
  text-transform: capitalize;
}

.text {
  &--primary {
    font-size: 1.6em;
    color: #1D1007;
  }

  &--secondary {
    font-size: 1.4em;
    color: #524D47;
  }
}

.button {
  font-size: 1.6em;
  border-radius: 2.4em;
  margin: 1.2em 0;
  padding: 0.8em 1em;
  text-decoration: none;
  cursor: pointer;

  transition: background 300ms;

  &--primary {
    color: #fff;
    background: #005226;
    border: 0;

    &:hover,
    &:focus {
      background: darken(#005226, 10);
    }
  }

  &--secondary {
    background: #F1F1F1;
    border: 1px solid #DBDCDD;
    color: #1D1007;

    &:hover,
    &:focus {
      background: darken(#F1F1F1, 10);
      border: 1px solid darken(#DBDCDD, 10);
    }
  }
}

@media screen and (max-width: 400px) {
  .button {
    font-size: 1.4em;
  }
}
</style>
