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

<style scoped>
.page { width: min(100% - 48px, 1040px); margin: 0 auto; padding: 72px 0; }
.page-heading { margin-bottom: 32px; }
.eyebrow { margin: 0 0 8px; color: #65798c; font-size: 12px; font-weight: 750; letter-spacing: .12em; text-transform: uppercase; }
h1 { margin: 0; font-size: clamp(30px, 4vw, 46px); letter-spacing: -.04em; }
.back-link { margin-bottom: 24px; padding: 0; border: 0; background: transparent; color: #687582; font-size: 14px; }
.subnav { display: flex; gap: 8px; margin-bottom: 24px; }
.subnav-button { padding: 10px 14px; border: 0; border-radius: 8px; background: transparent; color: #687582; font-size: 14px; font-weight: 650; }
.subnav-button.selected { background: #e6eef5; color: #24445f; }
@media (max-width: 650px) { .page { padding: 48px 0; } }
</style>
