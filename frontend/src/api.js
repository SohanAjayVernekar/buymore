import { reactive, watch } from 'vue'

export async function api(path, options = {}) {
  const response = await fetch('/api' + path, { ...options, headers: {'Content-Type': 'application/json', ...options.headers} })
  let data
  try { data = await response.json() } catch { throw new Error('The service is unavailable. Please try again.') }
  if (!response.ok) {
    const detail = data.detail
    throw new Error(Array.isArray(detail) ? detail.map(d => d.msg).join('. ') : detail || 'Something went wrong. Please try again.')
  }
  return data
}
export const post = (path, body, method = 'POST') => api(path, {method, body: JSON.stringify(body)})
let saved = {}
try { saved = JSON.parse(localStorage.getItem('buymore-cart') || '{}') } catch { /* Discard malformed saved state. */ }
export const store = reactive({userId: saved?.userId || 1, cart: Array.isArray(saved?.cart) ? saved.cart : [], users: [], toast: '', flights: [], cartBump: 0, recentlyAdded: ''})
watch(() => [store.userId, store.cart], () => localStorage.setItem('buymore-cart', JSON.stringify({userId: store.userId, cart: store.cart})), {deep: true})
let toastTimer
export function notify(message) { store.toast = message; clearTimeout(toastTimer); toastTimer = setTimeout(() => store.toast = '', 3000) }
let flightId = 0, addedTimer
export function addToCart(product, event) {
  const item = store.cart.find(i => i.product_id === product._id)
  if (item) { if (item.quantity >= 100) return; item.quantity++ }
  else store.cart.push({product_id: product._id, title: product.title, unit_price: product.price, category: product.category, quantity: 1})
  store.recentlyAdded = product._id
  clearTimeout(addedTimer)
  addedTimer = setTimeout(() => store.recentlyAdded = '', 1400)
  const source = event?.currentTarget?.getBoundingClientRect()
  let destination = document.querySelector('.cart-link')?.getBoundingClientRect()
  if (!destination || destination.bottom < 0) destination = document.querySelector('.sidebar a[href="/checkout"]')?.getBoundingClientRect()
  if (source && destination && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const id = ++flightId
    store.flights.push({id, x: source.left + source.width/2 - 19, y: source.top + source.height/2 - 19,
      dx: destination.left + destination.width/2 - source.left - source.width/2,
      dy: destination.top + destination.height/2 - source.top - source.height/2})
    setTimeout(() => { store.flights = store.flights.filter(f => f.id !== id); store.cartBump++ }, 720)
  } else store.cartBump++
  notify(`${product.title} added to cart`)
}
export const money = value => new Intl.NumberFormat('en-US', {style: 'currency', currency: 'USD'}).format(value || 0)
export const date = value => new Intl.DateTimeFormat('en-US', {month: 'short', day: 'numeric', year: 'numeric'}).format(new Date(value))
export const statusLabel = value => value?.charAt(0) + value?.slice(1).toLowerCase()
