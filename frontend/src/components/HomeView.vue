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
