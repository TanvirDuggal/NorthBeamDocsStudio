<script setup lang="ts">
import WorkspacePanel from './WorkspacePanel.vue'
defineEmits<{ openWriter: []; openUser: [] }>()
</script>

<template>
  <section class="page">
    <div class="page-heading"><p class="eyebrow">Home</p><h1>Choose a workspace</h1></div>
    <div class="panel-grid">
      <WorkspacePanel number="01" title="Writer" description="Create and manage articles." active @select="$emit('openWriter')" />
      <WorkspacePanel number="02" title="User" description="Read published articles." active @select="$emit('openUser')" />
    </div>
  </section>
</template>

<style scoped>
.page { width: min(100% - 48px, 1040px); margin: 0 auto; padding: 72px 0; }
.page-heading { margin-bottom: 32px; }
.eyebrow { margin: 0 0 8px; color: #65798c; font-size: 12px; font-weight: 750; letter-spacing: .12em; text-transform: uppercase; }
h1 { margin: 0; font-size: clamp(30px, 4vw, 46px); letter-spacing: -.04em; }
.panel-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }
@media (max-width: 650px) { .page { padding: 48px 0; } .panel-grid { grid-template-columns: 1fr; } }
</style>
