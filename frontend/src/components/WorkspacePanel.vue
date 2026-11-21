<script setup lang="ts">
defineProps<{ number: string; title: string; description: string; active?: boolean }>()
defineEmits<{ select: [] }>()
</script>

<template>
  <button v-if="active" class="panel panel-active" type="button" @click="$emit('select')">
    <span class="panel-number">{{ number }}</span>
    <span class="panel-title">{{ title }}</span>
    <span class="panel-description">{{ description }}</span>
  </button>
  <div v-else class="panel panel-muted">
    <span class="panel-number">{{ number }}</span>
    <span class="panel-title">{{ title }}</span>
    <span class="panel-description">{{ description }}</span>
  </div>
</template>
