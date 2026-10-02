<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, useId } from 'vue'
import { Check, ChevronDown } from 'lucide-vue-next'

const props = defineProps({
  modelValue: [String, Number],
  options: { type: Array, required: true },
  label: { type: String, required: true },
  compact: Boolean,
  disabled: Boolean,
})
const emit = defineEmits(['update:modelValue'])
const root = ref(null), trigger = ref(null), open = ref(false), highlighted = ref(0), upward = ref(false)
const id = useId()
const selected = computed(() => props.options.find(option => option.value === props.modelValue))
let typeBuffer = '', typeTimer

async function toggle() {
  if (props.disabled) return
  if (open.value) { close(); return }
  highlighted.value = Math.max(0, props.options.findIndex(option => option.value === props.modelValue))
  upward.value = window.innerHeight - trigger.value.getBoundingClientRect().bottom < Math.min(props.options.length * 43 + 16, 280)
  open.value = true
  await focusOption()
}
async function focusOption() {
  await nextTick()
  const item = root.value?.querySelector(`[data-option="${highlighted.value}"]`)
  item?.focus({ preventScroll: true })
  item?.scrollIntoView({ block: 'nearest' })
}
function close(returnFocus = true) { open.value = false; if (returnFocus) trigger.value?.focus({ preventScroll: true }) }
function select(option) { emit('update:modelValue', option.value); close() }
function outside(event) { if (!root.value?.contains(event.target)) close(false) }
function keydown(event) {
  if (props.disabled) return
  if (event.key === 'Escape') { event.stopPropagation(); event.preventDefault(); close(); return }
  if (event.key === 'Tab') { close(false); return }
  if (['ArrowDown', 'ArrowUp', 'Home', 'End'].includes(event.key)) {
    event.preventDefault()
    if (!open.value) { toggle(); return }
    if (event.key === 'Home') highlighted.value = 0
    else if (event.key === 'End') highlighted.value = props.options.length - 1
    else highlighted.value = (highlighted.value + (event.key === 'ArrowDown' ? 1 : -1) + props.options.length) % props.options.length
    focusOption()
  } else if (open.value && event.key.length === 1 && event.key !== ' ') {
    event.preventDefault(); clearTimeout(typeTimer); typeBuffer += event.key.toLowerCase()
    const index = props.options.findIndex(option => option.label.toLowerCase().startsWith(typeBuffer))
    if (index >= 0) { highlighted.value = index; focusOption() }
    typeTimer = setTimeout(() => typeBuffer = '', 700)
  }
}
onMounted(() => document.addEventListener('pointerdown', outside))
onUnmounted(() => { document.removeEventListener('pointerdown', outside); clearTimeout(typeTimer) })
</script>

<template>
  <div ref="root" class="select-menu" :class="{ compact, 'is-open': open }" @keydown="keydown">
    <button ref="trigger" type="button" class="select-trigger" :disabled="disabled || !options.length" :aria-label="label" aria-haspopup="listbox" :aria-expanded="open" :aria-controls="`${id}-list`" @click="toggle">
      <span class="select-copy"><small v-if="compact">{{ label }}</small><span>{{ selected?.label || 'Choose an option' }}</span></span>
      <ChevronDown :size="15" class="select-chevron" />
    </button>
    <Transition name="select-pop">
      <div v-if="open" :id="`${id}-list`" role="listbox" :aria-label="label" class="select-options" :class="{ upward }">
        <button v-for="(option, index) in options" :key="option.value" type="button" role="option" :aria-selected="option.value === modelValue" :data-option="index" tabindex="-1" :class="{ chosen: option.value === modelValue }" @click="select(option)" @focus="highlighted = index">
          <span>{{ option.label }}</span><Check v-if="option.value === modelValue" :size="15" />
        </button>
      </div>
    </Transition>
  </div>
</template>
