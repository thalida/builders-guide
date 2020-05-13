<template>
  <div id="cookbook">
    <header>
      <router-link to="/cookbook">bg</router-link>
      <router-link to="/about">About</router-link>
    </header>

    <router-view></router-view>

    <nav>
      <router-link to="/cookbook/build">Build</router-link> |
      <router-link to="/cookbook/recipes">Recipes</router-link> |
      <router-link to="/cookbook/shopping-list">Shopping List</router-link>
    </nav>
  </div>
</template>

<script>
// @ is an alias to /src
export default {
  name: 'Cookbook',
  components: {}
}
</script>
