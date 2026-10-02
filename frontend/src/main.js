import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Shop from './views/Shop.vue'
import Checkout from './views/Checkout.vue'
import Search from './views/Search.vue'
import OrderDetails from './views/OrderDetails.vue'
import Catalog from './views/Catalog.vue'
import './style.css'
const router = createRouter({history: createWebHistory(), routes: [
  {path: '/', component: Shop}, {path: '/checkout', component: Checkout},
  {path: '/admin/search', component: Search}, {path: '/admin/orders/:id', component: OrderDetails},
  {path: '/admin/catalog', component: Catalog}, {path: '/:pathMatch(.*)*', redirect: '/'},
]})
createApp(App).use(router).directive('reveal', {
  mounted(el) {
    if (!('IntersectionObserver' in window)) return
    el.classList.add('reveal')
    const io = new IntersectionObserver(entries => {
      for (const e of entries) if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target) }
    }, { threshold: 0, rootMargin: '0px 0px -8% 0px' })
    io.observe(el)
    el.__revealIO = io
  },
  unmounted(el) { el.__revealIO?.disconnect() }
}).mount('#app')
