<script setup lang="ts">
import { ref } from 'vue'
import HomeView from './components/HomeView.vue'
import UserView from './components/UserView.vue'
import WriterView from './components/WriterView.vue'

type View = 'home' | 'writer' | 'user'
const view = ref<View>('home')
</script>

<template>
  <main class="app-shell">
    <header class="app-header">
      <button class="brand" type="button" @click="view = 'home'">NorthBeam Docs Studio</button>
      <span class="header-label">Simple document publishing</span>
    </header>

    <HomeView
      v-if="view === 'home'"
      @open-writer="view = 'writer'"
      @open-user="view = 'user'"
    />
    <WriterView v-else-if="view === 'writer'" @go-home="view = 'home'" />
    <UserView v-if="view === 'user'" @go-home="view = 'home'" />
  </main>
</template>

<style scoped>
:global(*) { box-sizing: border-box; }
:global(body) { margin: 0; background: #f5f7f9; color: #18212b; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
button, input, textarea { font: inherit; }
button { cursor: pointer; }
.app-shell { min-height: 100vh; }
.app-header { display: flex; align-items: center; justify-content: space-between; padding: 24px max(24px, calc((100vw - 1040px) / 2)); border-bottom: 1px solid #e1e6eb; background: #fff; }
.brand { padding: 0; border: 0; background: transparent; color: #18212b; font-size: 17px; font-weight: 750; }
.header-label { color: #687582; font-size: 13px; }
@media (max-width: 650px) { .app-header { align-items: flex-start; flex-direction: column; gap: 8px; } }
</style>
