import VueFinder from 'vuefinder'
import 'vuefinder/dist/vuefinder.css'

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.use(VueFinder)
})
