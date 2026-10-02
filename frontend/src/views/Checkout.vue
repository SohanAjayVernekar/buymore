<script setup>
import { computed, ref } from 'vue'
import { ArrowLeft, ArrowRight, Check, Minus, Plus, ShoppingBag, Trash2 } from 'lucide-vue-next'
import { store, post, money } from '../api'
import ProductArt from '../components/ProductArt.vue'
const total = computed(() => store.cart.reduce((sum, i) => sum + i.unit_price * i.quantity, 0))
const busy = ref(false), error = ref(''), result = ref(null)
async function checkout() {
  busy.value = true; error.value = ''
  try { result.value = await post('/orders', {user_id: store.userId, items: store.cart.map(({product_id, quantity}) => ({product_id, quantity}))}); store.cart = [] }
  catch(e) { error.value = e.message } finally { busy.value = false }
}
function remove(id) { store.cart = store.cart.filter(i => i.product_id !== id) }
</script>
<template>
  <div class="page-heading"><div><p class="eyebrow">JUST A FEW GOOD CHOICES</p><h1>Your cart<span class="blue-dot">.</span></h1></div><router-link class="back-link" to="/"><ArrowLeft :size="16"/>Continue exploring</router-link></div>
  <div v-if="result" class="success-panel"><span class="success-icon"><Check :size="30"/></span><p class="eyebrow">ALL SET</p><h2>A little better is on its way.</h2><p>Order #{{result.order_id}} was placed successfully.</p><strong>{{money(result.total_amount)}}</strong><p v-if="result.sync_status === 'queue_unavailable'" class="notice warning">Your order is saved. Search synchronization needs attention; please contact the demo administrator.</p><p v-else>Your order will appear in order search shortly.</p><div class="button-row"><router-link class="primary" :to="`/admin/orders/${result.order_id}`">View order <ArrowRight :size="16"/></router-link><router-link class="secondary" to="/">Keep exploring</router-link></div></div>
  <div v-else-if="!store.cart.length" class="empty"><ShoppingBag :size="42"/><h2>Good things start here.</h2><p>Your cart is empty. Find something for your everyday.</p><router-link to="/" class="primary">Explore the collection <ArrowRight :size="16"/></router-link></div>
  <div v-else class="checkout-layout"><section class="cart-items"><article v-for="item in store.cart" :key="item.product_id" class="cart-item"><div class="cart-art"><ProductArt :title="item.title" :category="item.category"/></div><div class="cart-description"><small>{{item.category}}</small><h3>{{item.title}}</h3><p>{{money(item.unit_price)}} each</p><div class="quantity"><button @click="item.quantity--" :disabled="busy || item.quantity <= 1" :aria-label="`Decrease ${item.title}`"><Minus :size="13"/></button><span>{{item.quantity}}</span><button @click="item.quantity++" :disabled="busy || item.quantity >= 100" :aria-label="`Increase ${item.title}`"><Plus :size="13"/></button></div></div><div class="cart-line-total"><strong>{{money(item.unit_price * item.quantity)}}</strong><button class="icon-button" :disabled="busy" @click="remove(item.product_id)" :aria-label="`Remove ${item.title}`"><Trash2 :size="17"/></button></div></article></section><aside class="order-summary"><p class="eyebrow">ONE STEP AWAY</p><h2>Order summary</h2><div class="summary-row"><span>Items ({{store.cart.reduce((s, i) => s+i.quantity, 0)}})</span><strong>{{money(total)}}</strong></div><div class="summary-row total"><span>Total</span><strong>{{money(total)}}</strong></div><p>Ordering as <strong>{{store.users.find(u => u.id === store.userId)?.name || 'your selected shopper'}}</strong>.</p><p class="subtle">Prices are checked again when you place your order.</p><div v-if="error" class="notice error" role="alert">{{error}}</div><button class="primary full" @click="checkout" :disabled="busy || !store.users.length">{{busy ? 'Placing your order…' : 'Place order'}}<ArrowRight :size="17"/></button></aside></div>
</template>
