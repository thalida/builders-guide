// // import { expect } from 'chai'
// import { createLocalVue } from '@vue/test-utils'
// import Vuex from 'vuex'

// import store from '@/store'
// // import ItemImage from '@/components/ItemImage.vue'

// const localVue = createLocalVue()
// localVue.use(Vuex)

// // describe('HelloWorld.vue', () => {
// //   it('renders props.msg when passed', () => {
// //     const msg = 'new message'
// //     const wrapper = shallowMount(HelloWorld, {
// //       propsData: { msg }
// //     })
// //     expect(wrapper.text()).to.include(msg)
// //   })
// // })

// describe('ItemImage.vue', () => {
//   let localStore
//   beforeEach(() => {
//     localStore
//       .dispatch('init')
//       .then(() => {

//       })

//     localStore = store
//   })

//   it('all 1.15 items have an image', () => {
//     localStore
//       .dispatch('init')
//       .then(() => {
//         console.log(localStore.state.gameData[this.version].items)
//         // const wrapper = shallowMount(ItemImage, { propsData, store, localVue })
//         // expect(wrapper.text()).to.include(msg)
//       })
//   })
// })
