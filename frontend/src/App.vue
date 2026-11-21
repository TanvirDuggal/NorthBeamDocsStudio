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
