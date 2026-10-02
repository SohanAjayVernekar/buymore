<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ArrowLeft, Check, RotateCw } from 'lucide-vue-next'
import { api, post, money, date, statusLabel, notify } from '../api'
import SelectMenu from '../components/SelectMenu.vue'
const route = useRoute(), order = ref(null), error = ref(''), busy = ref(false), status = ref('')
async function load() {busy.value = true; try {order.value = await api(`/orders/${route.params.id}`); status.value = order.value.status; error.value = ''} catch(e) {error.value = e.message} finally {busy.value = false}}
async function save() {busy.value = true; try {order.value = await post(`/orders/${route.params.id}/status`, {status: status.value}, 'PATCH'); error.value = ''; notify('Order status updated')} catch(e) {error.value = e.message} finally {busy.value = false}}
onMounted(load); watch(() => route.params.id, load)
</script>
<template>
  <router-link class="back-link" to="/admin/search"><ArrowLeft :size="16"/>Back to orders</router-link>
  <div v-if="error" class="notice error" role="alert">{{error}} <button @click="load">Retry</button></div>
  <template v-if="order"><div class="page-heading"><div><p class="eyebrow">EVERY DETAIL, RIGHT HERE</p><h1>Order #{{String(order.order_id).padStart(4, '0')}}<span class="blue-dot">.</span></h1><p class="subtle">Placed {{date(order.order_date)}}</p></div><span class="status" :class="order.status.toLowerCase()">{{statusLabel(order.status)}}</span></div>
  <div class="details-layout"><section class="receipt panel"><h2>Itemized receipt</h2><div class="table-wrap"><table><thead><tr><th>Product</th><th>Unit price</th><th>Quantity</th><th>Total</th></tr></thead><tbody><tr v-for="(item,i) in order.items" :key="i"><td><strong>{{item.title}}</strong></td><td>{{money(item.unit_price)}}</td><td>{{item.quantity}}</td><td class="amount">{{money(item.unit_price*item.quantity)}}</td></tr></tbody></table></div><div class="receipt-total"><span>Order total</span><strong>{{money(order.total_amount)}}</strong></div><p class="subtle">Product names and prices are saved as they were when this order was placed.</p></section><aside class="detail-sidebar"><div class="panel"><p class="eyebrow">CUSTOMER</p><h3>{{order.customer.name}}</h3><p>{{order.customer.email}}</p></div><div class="panel"><h3>Fulfillment status</h3><div class="input-label">Update status<SelectMenu v-model="status" label="Update status" :disabled="busy" :options="['PENDING','PROCESSING','SHIPPED'].map(s => ({value:s, label:statusLabel(s)}))"/></div><button class="primary full" :disabled="busy || status === order.status" @click="save">Save status <Check :size="16"/></button></div><div class="panel sync-panel"><h3>Search synchronization</h3><span class="sync-badge" :class="{synced: order.sync_status === 'in_sync'}"><span class="live-dot"></span>{{({in_sync:'Up to date',pending:'Update pending',queued:'Update queued',unavailable:'Search unavailable',queue_unavailable:'Needs attention'})[order.sync_status]}}</span><p class="subtle">{{order.sync_status === 'in_sync' ? 'Order search matches this saved order.' : 'Your order is saved. Search may take a moment to catch up.'}}</p><button class="text-button" @click="load" :disabled="busy"><RotateCw :size="14"/>Check again</button></div></aside></div></template>
  <div v-else-if="busy" class="loading">Loading your order…</div>
</template>
