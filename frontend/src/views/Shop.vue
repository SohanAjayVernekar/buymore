<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { ArrowUpRight, ArrowRight, Search, SlidersHorizontal, Plus, Check, Grid2X2, Headphones, Cable, Keyboard, LampDesk, ChevronLeft, ChevronRight } from 'lucide-vue-next'
import { api, addToCart, money, store } from '../api'
import ProductArt from '../components/ProductArt.vue'
const products = ref([]), category = ref(''), query = ref(''), loading = ref(true), error = ref(''), showFilters = ref(false), maxPrice = ref(250)
const page = ref(1), pageSize = ref(6), total = ref(0), totalPages = ref(0), paginationLoading = ref(false)
const categories = [{id: '', label: 'All', icon: Grid2X2}, {id: 'peripherals', label: 'Peripherals', icon: Keyboard}, {id: 'audio', label: 'Audio', icon: Headphones}, {id: 'cables', label: 'Cables', icon: Cable}, {id: 'office', label: 'Office', icon: LampDesk}]
const featured = ref([])
async function loadFeatured() {
  try {
    const [a, b] = await Promise.all([
      api('/products?query=' + encodeURIComponent('Noise Cancelling Headphones') + '&page_size=1'),
      api('/products?query=' + encodeURIComponent('Wireless Mouse Pro') + '&page_size=1')
    ])
    featured.value = [a.items?.[0], b.items?.[0]].filter(Boolean)
  } catch { featured.value = [] }
}
const browsing = computed(() => category.value || query.value || showFilters.value)
async function load(isPagination = false) { if (!isPagination) loading.value = true; else paginationLoading.value = true; try { const params = new URLSearchParams({ page: page.value, page_size: pageSize.value }); if (category.value) params.append('category', category.value); if (query.value) params.append('query', query.value); if (showFilters.value) params.append('max_price', maxPrice.value); const res = await api(`/products?${params.toString()}`); products.value = res.items; total.value = res.total; totalPages.value = res.total_pages; error.value = '' } catch(e) {error.value = e.message} finally {loading.value = false; paginationLoading.value = false} }
function explore(id) { category.value = id; page.value = 1; load() }
watch(() => category.value, () => { page.value = 1; load() })
watch(() => query.value, () => { page.value = 1; load() })
watch(() => showFilters.value, () => { page.value = 1; load() })
watch(() => maxPrice.value, () => { page.value = 1; load() })
watch(() => page.value, () => { load(true) })
const tabsEl = ref(null), tabStyle = ref({ transform: 'translateX(0px)', width: '0px' })
function placeTab() {
  const btn = tabsEl.value?.querySelector('button.selected')
  if (btn) tabStyle.value = { transform: `translateX(${btn.offsetLeft}px)`, width: `${btn.offsetWidth}px` }
}
watch(category, () => nextTick(placeTab))
onMounted(() => { load(); loadFeatured(); placeTab(); window.addEventListener('resize', placeTab); document.fonts?.ready.then(() => placeTab()) })
onUnmounted(() => window.removeEventListener('resize', placeTab))
</script>
<template>
  <section class="page-heading"><div><p class="eyebrow">FIND YOUR NEXT FAVOURITE</p><h1>Explore<span class="blue-dot">.</span></h1></div><div class="category-tabs" ref="tabsEl"><button v-for="c in categories" :key="c.id" :class="{selected: category === c.id}" @click="explore(c.id)"><component :is="c.icon" :size="15"/>{{c.label}}</button><i class="tab-slide" :style="tabStyle"></i></div><button class="filter-button" :class="{chosen: showFilters}" @click="showFilters = !showFilters"><SlidersHorizontal :size="15"/>Filters</button></section>
  <div v-if="error" class="notice error" role="alert">{{error}} <button @click="load">Try again</button></div>
  <div v-else-if="loading" class="loading">Finding your next favourite…</div>
  <template v-else>
    <div v-if="!browsing" class="editorial-grid">
      <div class="editorial-stack">
        <button class="banner mint-banner" @click="explore('peripherals')"><span class="banner-copy"><small>SMALL UPGRADES. BIG DIFFERENCE.</small><strong>Make room for<br>better everyday.</strong><span class="pill">Explore essentials <ArrowUpRight :size="14"/></span></span><ProductArt title="Wireless Keyboard"/></button>
        <button class="banner yellow-banner" @click="explore('audio')"><span class="banner-copy"><small>TUNE INTO YOUR WORLD</small><strong>Your day.<br>Your soundtrack.</strong><span>Find your perfect sound <ArrowRight :size="15"/></span></span><ProductArt title="Wireless Earbuds"/><span class="round-arrow"><ArrowUpRight :size="18"/></span></button>
      </div>
      <article v-for="(p, i) in featured" :key="p._id" class="featured-product" :class="i ? 'sand-card' : 'lavender-card'">
        <div class="product-top"><span class="swatches"><i></i><i></i></span><span class="mini-label">{{ i ? 'Everyday essential' : 'Our pick' }}</span></div><ProductArt :title="p.title" :category="p.category"/>
        <div class="featured-bottom"><div><small>{{p.category}}</small><h3>{{p.title}}</h3></div><button class="price-button" :class="{added: store.recentlyAdded === p._id}" @click="addToCart(p, $event)" :aria-label="`Add ${p.title} to cart`">{{money(p.price)}} <Check v-if="store.recentlyAdded === p._id" :size="13"/><Plus v-else :size="13"/></button></div>
      </article>
      <button class="desk-banner" @click="explore('office')"><div><small>A SPACE THAT WORKS FOR YOU</small><h2>Good design.<br>Better workdays.</h2><span>Discover office essentials <ArrowUpRight :size="16"/></span></div><ProductArt title="Desk Lamp LED"/></button>
      <button class="collection-banner" @click="explore('cables')"><div><small>STAY CONNECTED</small><h2>Less clutter.<br>More possibility.</h2><span>Shop cables & hubs <ArrowUpRight :size="16"/></span></div><ProductArt title="USB-C Hub 7-in-1"/></button>
    </div>
    <section class="collection-header" v-reveal><div><p class="eyebrow">THE EVERYDAY COLLECTION</p><h2>{{ category ? categories.find(c => c.id === category).label : "A few things you'll love" }} <span class="count">{{total}}</span></h2></div><label class="search-input"><Search :size="17"/><input v-model="query" placeholder="Find something good…" aria-label="Search products"/></label></section>
    <div v-if="showFilters" class="filter-strip"><label>Maximum price <strong>{{money(maxPrice)}}</strong><input v-model.number="maxPrice" type="range" min="0" max="250" step="5"/></label><button class="text-button" @click="maxPrice = 250; category = ''; query = ''">Reset filters</button></div>
    <div v-if="!products.length" class="empty"><Search :size="32"/><h3>No products found</h3><p>Try another search or a different category.</p><button class="secondary" @click="category = ''; query = ''; maxPrice = 250">Clear filters</button></div>
    <div class="product-grid" v-reveal><article v-for="p in products" :key="p._id" class="product-card"><div class="product-image" :class="p.category"><span class="mini-label">{{p.attributes.color}}</span><ProductArt :title="p.title" :category="p.category"/></div><div class="product-info"><small>{{p.category}} <span>· {{p.attributes.brand}}</span></small><h3>{{p.title}}</h3><p>{{p.description}}</p><div class="product-bottom"><strong>{{money(p.price)}}</strong><button class="add-button" :class="{added: store.recentlyAdded === p._id}" @click="addToCart(p, $event)" :aria-label="`Add ${p.title} to cart`"><Check v-if="store.recentlyAdded === p._id" :size="16"/><Plus v-else :size="16"/> {{store.recentlyAdded === p._id ? 'Added' : 'Add'}}</button></div></div></article></div>
    <div class="pagination" v-reveal><button class="icon-button" :disabled="page <= 1 || paginationLoading" @click="page--" aria-label="Previous page"><ChevronLeft :size="16"/></button><span class="page-info">Page {{page}} of {{totalPages || 1}} ({{total}} products)</span><button class="icon-button" :disabled="page >= totalPages || paginationLoading" @click="page++" aria-label="Next page"><ChevronRight :size="16"/></button></div>
  </template>
</template>
