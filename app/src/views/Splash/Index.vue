<template>
  <div class="splash">
    <div class="splash__background">
        <div
          class="splash__background__item"
          v-for="(itemName, index) in renderItems"
          :key="index">
          <img
            class="splash__background__img"
            :src="getItemImage(itemName)" />
        </div>
    </div>

    <div class="splash__container">
      <section class="splash__content">
        <h1 class="wordmark">builder's guide</h1>
        <h2>A Minecraft Cookbook</h2>
        <p class="font-size--normal">
          Figure out the recipes and resources you’ll need for your next build!
        </p>
        <router-link
          to="/cookbook"
          class="splash__cta">
          Plan your build
          <chevron-right-icon />
        </router-link>
      </section>
    </div>

    <footer class="splash__footer">
      <div class="splash__checkbox">
        <label>
          <input type="checkbox" v-model="skipSplash" />
          <span>Don't show this again</span>
        </label>
      </div>
      <router-link to="/about" class="link">About</router-link>
    </footer>
  </div>
</template>

<script>
import chevronRightIcon from '@/components/icons/chevron-right.vue'

// @ is an alias to /src
export default {
  name: 'Splash',
  components: {
    chevronRightIcon
  },
  data: () => {
    return {
      checked: true,
      numBlocks: 16,
      // numBlocks: 30,
      renderItems: [],
    }
  },
  computed: {
    items () {
      if (
        typeof this.$store.state.gameData[this.$store.state.selectedVersion] === 'undefined' ||
        typeof this.$store.state.gameData[this.$store.state.selectedVersion].items === 'undefined'
      ) {
        return []
      }

      return this.$store.state.gameData[this.$store.state.selectedVersion].items
    },
    skipSplash: {
      get () {
        return this.$store.state.skipSplash
      },
      set (newBool) {
        this.$store.commit('setSkipSplash', newBool)
      }
    }
  },
  mounted () {
    this.$store
      .dispatch('setupItems')
      .then(this.setupRenderItems)
  },
  methods: {
    selectRandomItem (arr) {
      const len = arr.length
      const randIdx = Math.floor(Math.random() * Math.floor(len))
      return {
        index: randIdx,
        item: arr[randIdx]
      }
    },
    setupRenderItems () {
      const itemsCopy = this.items.splice(0)

      for (let i = 0; i < this.numBlocks; i += 1) {
        const randItem = this.selectRandomItem(itemsCopy)
        this.renderItems.push(randItem.item)
        itemsCopy.splice(randItem.index, 1)
      }
    },
    getItemImage (item) {
      const images = require.context('../../assets/minecraft/1.15/128x128/', false, /\.png$/)
      try {
        return images(`./${item}.png`)
      } catch (error) {
        return images('./air.png')
      }
    },
  }
}
</script>

<style lang="scss" scoped>
@keyframes animation--item-circle {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

@keyframes animation--item {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

.splash {
  $item-count: 16;
  $circle-size: 85vh;
  $item-size: 10vh;

  display: flex;
  position: relative;
  flex-flow: column nowrap;
  justify-content: space-between;
  align-items: center;
  min-width: 100vw;
  min-height: 100vh;
  overflow: hidden;

  &__container {
    display: flex;
    width: 100%;
    flex: 2 0 auto;
    justify-content: center;
    align-items: center;
  }

  &__content {
    display: flex;
    width: 60vh;
    margin-top: 10vh;
    flex-flow: column wrap;
    justify-content: center;
    align-items: center;
    text-align: center;
  }

  h2 {
    font-size: 2.2em;
    font-weight: 500;
  }

  p {
    margin-top: 0.4em;
    line-height: 1.4;
  }

  &__checkbox {
    font-size: 1.4em;

    label {
      cursor: pointer;
    }

    span {
      padding: 0 0.2em;
    }

    &:hover,
    &:focus {
      span {
        text-decoration: underline;
      }
    }
  }

  &__cta {
    display: flex;
    flex-flow: row nowrap;
    justify-content: space-between;
    align-items: center;

    font-size: 1.8em;
    color: #fff;
    background: rgba(12, 136, 68, 1);
    border-radius: 2.4em;
    margin: 1.2em 0;
    padding: 0.8em 1.6em;
    text-decoration: none;

    transition: background 300ms;

    svg {
      margin-left: 0.8em;
    }

    &:hover,
    &:focus {
      background: darken(rgba(12, 136, 68, 1), 10);
    }
  }

  &__footer {
    width: 100%;
    padding: 4vh 20%;

    flex: 0 1 24vh;
    align-self: flex-end;
    display: flex;
    flex-flow: row nowrap;
    justify-content: space-between;
    align-items: flex-end;

    background-image: url('../../assets/background_wavy.svg');
    background-color: transparent;
    background-position: top center;
    background-size: cover;
    background-repeat: no-repeat;
  }

  // https://css-tricks.com/snippets/sass/placing-items-circle/
  &__background {
    position: absolute;
    width:  $circle-size;
    height: $circle-size;
    padding: 0;
    margin: 0;
    border-radius: 50%;
    z-index: -1;

    animation-duration: 420s;
    animation-timing-function: linear;
    animation-name: animation--item-circle;
    animation-iteration-count: infinite;

    &__item {
      display: block;
      position: absolute;
      top:  50%;
      left: 50%;
      width:  $item-size;
      height: $item-size;
      margin: -($item-size / 2);

      $angle: (360 / $item-count);
      $rot: 0;
      @for $i from 1 through $item-count {
        $circle_radius: $circle-size / 2;
        $rand_translate: $circle_radius;
        // $rand_translate: random(round($circle_radius / 4)) + $circle_radius;
        $rand_item_rot: random(22) + $rot;

        &:nth-of-type(#{$i}) {
          @if random(1) == 1 {
            transform:
              rotate($rot * 1deg)
              translate($rand_translate)
              rotate($rand_item_rot * -1deg);
          } @else {
            transform:
              rotate($rot * 1deg)
              translate($rand_translate)
              rotate($rand_item_rot * 1deg);
          }
        }

        $rot: $rot + $angle;
      }
    }

    &__img {
      width: 100%;
      height: 100%;

      animation-timing-function: linear;
      animation-name: animation--item;
      animation-iteration-count: infinite;

      @for $i from 1 through $item-count {
        &:nth-of-type(#{$i}) {
          animation-duration: random(30) + 30s;
        }
      }
    }
  }

  @media screen and (max-width: 600px) {
    &__footer {
      padding-left: 8%;
      padding-right: 8%;
    }
  }
}
</style>
