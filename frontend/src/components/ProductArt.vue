<script setup>
import { computed } from 'vue'
const props = defineProps({title: {type: String, default: ''}, category: {type: String, default: ''}})
const kind = computed(() => {
  const t = props.title.toLowerCase()
  if (/mouse|trackpad/.test(t) && !/pad/.test(t.replace('trackpad', 'track'))) return 'mouse'
  if (/keyboard/.test(t)) return 'keyboard'
  if (/earbud|earphone/.test(t)) return 'earbuds'
  if (/lamp/.test(t)) return 'lamp'
  if (/headphone|headset/.test(t)) return 'headphones'
  if (/cable|adapter|hub|dock/.test(t) || props.category === 'cables') return 'hub'
  if (/speaker|microphone/.test(t)) return 'speaker'
  if (/webcam/.test(t)) return 'webcam'
  return 'desk'
})
</script>
<template>
  <svg class="product-art" viewBox="0 0 320 250" role="img" :aria-label="title">
    <defs>
      <linearGradient id="metal" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#e5e5e4"/><stop offset=".5" stop-color="#aaaead"/><stop offset="1" stop-color="#787e7d"/></linearGradient>
      <linearGradient id="dark" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#545958"/><stop offset="1" stop-color="#151a19"/></linearGradient>
      <linearGradient id="cream" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#fff"/><stop offset="1" stop-color="#c9d0c6"/></linearGradient>
      <filter id="shadow"><feGaussianBlur stdDeviation="7"/></filter>
    </defs>
    <ellipse cx="164" cy="214" rx="75" ry="9" fill="#25392c" opacity=".14" filter="url(#shadow)"/>
    <g v-if="kind === 'headphones'" transform="rotate(-17 160 125)">
      <path d="M88 140V105a72 72 0 0 1 144 0v35" fill="none" stroke="#252b28" stroke-width="22"/>
      <path d="M91 118V105a69 69 0 0 1 138 0v13" fill="none" stroke="#757e76" stroke-width="8"/>
      <rect x="69" y="115" width="47" height="85" rx="22" fill="url(#dark)"/><rect x="207" y="115" width="47" height="85" rx="22" fill="url(#dark)"/>
      <rect x="94" y="121" width="22" height="73" rx="10" fill="#111a14"/><rect x="207" y="121" width="22" height="73" rx="10" fill="#111a14"/>
      <path d="M79 139v33M244 139v33" stroke="#818881" stroke-width="2"/>
    </g>
    <g v-else-if="kind === 'mouse'" transform="rotate(-26 160 125)">
      <rect x="105" y="35" width="112" height="180" rx="55" fill="#767d74"/><rect x="103" y="30" width="112" height="177" rx="55" fill="url(#cream)"/>
      <path d="M159 32v65M107 104q52 -16 103 0" fill="none" stroke="#acb4a8"/>
      <rect x="154" y="60" width="10" height="31" rx="5" fill="#454d41"/>
      <path d="M121 141q0 40 23 50" stroke="#fff" stroke-width="3" fill="none" opacity=".7"/>
    </g>
    <g v-else-if="kind === 'keyboard'" transform="translate(15 20) rotate(-12 145 115)">
      <rect x="16" y="67" width="265" height="117" rx="14" fill="#969e92"/><rect x="12" y="61" width="265" height="117" rx="14" fill="#dce1d7"/>
      <g v-for="r in 4" :key="r"><rect v-for="c in 12" :key="c" :x="20+c*19" :y="50+r*24" width="15" height="18" rx="3" :fill="c === 12 ? '#b2cc90' : '#fafbf7'"/></g>
      <rect x="90" y="146" width="91" height="18" rx="3" fill="#b2cc90"/>
    </g>
    <g v-else-if="kind === 'earbuds'" transform="rotate(-12 160 120)">
      <rect x="86" y="119" width="155" height="86" rx="36" fill="url(#cream)"/><path d="M88 145h151" stroke="#b1b9aa"/>
      <circle cx="164" cy="176" r="3" fill="#8fa97c"/>
      <g transform="translate(105 38)"><rect width="21" height="72" rx="10" fill="url(#cream)"/><ellipse cx="9" cy="15" rx="22" ry="19" fill="url(#cream)"/><ellipse cx="0" cy="13" rx="9" ry="11" fill="#3b4438"/></g>
      <g transform="translate(195 36) rotate(20)"><rect width="21" height="72" rx="10" fill="url(#cream)"/><ellipse cx="9" cy="15" rx="22" ry="19" fill="url(#cream)"/><ellipse cx="20" cy="13" rx="9" ry="11" fill="#3b4438"/></g>
    </g>
    <g v-else-if="kind === 'lamp'">
      <ellipse cx="165" cy="207" rx="60" ry="12" fill="#788272"/><path d="M166 200V105l-37-41" stroke="#485442" stroke-width="10" fill="none"/>
      <path d="M103 55q37-25 66 5l-18 53-75-21Z" fill="#b8cd95"/><ellipse cx="114" cy="101" rx="39" ry="10" transform="rotate(16 114 101)" fill="#f9f3c4"/>
      <circle cx="165" cy="108" r="9" fill="#b8cd95"/>
    </g>
    <g v-else-if="kind === 'hub'" transform="rotate(-22 160 130)">
      <path d="M158 95V60q0-25 35-25h33" stroke="#696e69" stroke-width="9" fill="none"/><rect x="220" y="26" width="29" height="18" rx="4" fill="url(#metal)"/>
      <rect x="76" y="96" width="173" height="87" rx="16" fill="#747a76"/><rect x="74" y="88" width="173" height="87" rx="16" fill="url(#metal)"/>
      <rect v-for="i in 3" :key="i" :x="84+i*38" y="154" width="26" height="8" rx="2" fill="#24312b"/><text x="159" y="128" text-anchor="middle" fill="#f4f5f2" font-size="11" letter-spacing="3">BUYMORE</text>
    </g>
    <g v-else-if="kind === 'speaker'">
      <rect x="104" y="43" width="114" height="167" rx="37" fill="url(#dark)"/>
      <path v-for="i in 17" :key="i" :d="`M114 ${63+i*7}h94`" stroke="#879084" opacity=".35"/>
      <circle cx="161" cy="64" r="5" fill="#c1d7a8"/>
    </g>
    <g v-else-if="kind === 'webcam'">
      <path d="M160 137v55M112 202h99" stroke="#555f50" stroke-width="14" stroke-linecap="round"/>
      <rect x="72" y="66" width="180" height="87" rx="30" fill="url(#dark)"/>
      <circle cx="161" cy="110" r="31" fill="#848d82"/><circle cx="161" cy="110" r="24" fill="#141d1a"/><circle cx="163" cy="107" r="12" fill="#3e5a5e"/><circle cx="169" cy="100" r="5" fill="#a1b7b0"/>
    </g>
    <g v-else>
      <path d="m66 151 128-64 67 41-128 66Z" fill="url(#metal)"/><path d="m133 194 128-66v16l-128 65Z" fill="#747f72"/>
      <path d="m133 194-67-43v16l67 42Z" fill="#abb6a7"/><path d="m139 184 15 25 72-37-10-27" fill="#7c8976"/>
      <path d="m108 132 82-37" stroke="#e5eae1" stroke-width="5"/>
    </g>
  </svg>
</template>
