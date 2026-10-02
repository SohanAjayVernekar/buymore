<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { Compass, ShoppingBag, Search, Boxes, ArrowUpRight, LayoutGrid, ChevronDown, Check, ShoppingCart } from 'lucide-vue-next'
import { api, store } from './api'
import SelectMenu from './components/SelectMenu.vue'
const route = useRoute()
const count = computed(() => store.cart.reduce((s, i) => s + i.quantity, 0))
const shopper = computed(() => store.users.find(u => u.id === store.userId))
const error = ref('')
async function loadUsers() { try { store.users = await api('/users'); error.value = '' } catch(e) { error.value = e.message } }
onMounted(loadUsers)
</script>
<template>
  <div class="ambient" aria-hidden="true"><i class="orb orb-a"></i><i class="orb orb-b"></i></div>
  <div class="app-shell">
    <aside class="sidebar">
      <router-link to="/" class="brand"><span class="brand-mark" aria-hidden="true"><ShoppingBag :size="16"/></span>Buy<span>More</span><i></i></router-link>
      <p class="nav-label">YOUR EVERYDAY, UPGRADED</p>
      <nav>
        <router-link to="/" :class="{active: route.path === '/'}"><Compass :size="18"/> Explore new</router-link>
        <router-link to="/checkout" :class="{active: route.path === '/checkout'}"><ShoppingBag :size="18"/> My cart <small v-if="count">{{count}}</small></router-link>
        <div class="nav-divider"></div><p class="nav-label">MANAGE</p>
        <router-link to="/admin/search" :class="{active: route.path.startsWith('/admin/orders') || route.path === '/admin/search'}"><Search :size="18"/> Order search</router-link>
        <router-link to="/admin/catalog" :class="{active: route.path === '/admin/catalog'}"><Boxes :size="18"/> Product catalog</router-link>
      </nav>
      <div class="side-note"><div class="note-icon"><LayoutGrid :size="22"/></div><h3>A little more.<br>A little better.</h3><p>Thoughtful essentials for<br>your everyday setup.</p><router-link to="/">Explore the collection <ArrowUpRight :size="16"/></router-link></div>
      <div class="sidebar-bottom"><span class="live-dot"></span> The everyday collection <span>2026</span></div>
    </aside>
    <div class="workspace">
      <header class="topbar">
        <div class="edition"><strong>Good things,<br>great finds.</strong><span>CURATED FOR YOUR EVERYDAY</span></div>
        <div class="switcher"><router-link to="/" :class="{selected: !route.path.startsWith('/admin')}">Storefront</router-link><router-link to="/admin/search" :class="{selected: route.path.startsWith('/admin')}">Dashboard</router-link></div>
        <div class="account"><router-link class="cart-link" to="/checkout"><ShoppingCart :size="17"/><span>Cart</span><b :key="store.cartBump" :class="{'cart-count-pop': store.cartBump}">{{count}}</b></router-link><div class="avatar">{{shopper?.name?.split(' ').map(n => n[0]).join('') || 'JD'}}</div><SelectMenu v-model="store.userId" label="Log in as" compact :options="store.users.map(u => ({value: u.id, label: u.name}))"/></div>
      </header>
      <div v-if="error" class="notice error">{{error}} <button class="text-button" @click="loadUsers">Retry</button></div>
      <main><router-view v-slot="{ Component }"><Transition name="page" mode="out-in"><div :key="route.path" class="page-content"><component :is="Component"/></div></Transition></router-view></main>
      <footer><span>BuyMore · Everyday essentials</span><span>Thoughtfully picked. Simply yours.</span></footer>
    </div>
  </div>
  <div v-for="flight in store.flights" :key="flight.id" class="cart-flight" aria-hidden="true" :style="{left:flight.x+'px', top:flight.y+'px', '--flight-x':flight.dx+'px', '--flight-y':flight.dy+'px'}"><ShoppingBag :size="18"/><small>+1</small></div>
  <Transition name="toast"><div v-if="store.toast" class="toast" role="status"><Check :size="18"/>{{store.toast}}</div></Transition>
</template>
