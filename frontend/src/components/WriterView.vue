<script setup lang="ts">
import { ref } from 'vue'
import CreateArticlePanel from './CreateArticlePanel.vue'
import SnapshotsPanel from './SnapshotsPanel.vue'

type WriterPanel = 'create' | 'snapshots'
defineEmits<{ goHome: [] }>()
const activePanel = ref<WriterPanel>('create')
</script>

<template>
  <section class="page">
    <div class="page-heading">
      <button class="back-link" type="button" @click="$emit('goHome')">← Home</button>
      <p class="eyebrow">Writer</p><h1>Article workspace</h1>
    </div>
    <nav class="subnav" aria-label="Writer panels">
      <button class="subnav-button" :class="{ selected: activePanel === 'create' }" type="button" @click="activePanel = 'create'">Create Article</button>
      <button class="subnav-button" :class="{ selected: activePanel === 'snapshots' }" type="button" @click="activePanel = 'snapshots'">Show Snapshots</button>
    </nav>
    <CreateArticlePanel v-if="activePanel === 'create'" />
    <SnapshotsPanel v-else />
  </section>
</template>
