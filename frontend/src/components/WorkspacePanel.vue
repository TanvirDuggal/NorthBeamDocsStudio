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

<style scoped>
.panel { display: flex; min-height: 190px; padding: 26px; flex-direction: column; align-items: flex-start; border: 1px solid #e0e6eb; border-radius: 14px; background: #fff; box-shadow: 0 8px 28px rgb(25 43 60 / 5%); text-align: left; }
.panel-active { border-color: #b6c9dc; }
.panel-active:hover { border-color: #6f91b0; transform: translateY(-2px); }
.panel-muted { opacity: .7; }
.panel-number { margin-bottom: auto; color: #8496a7; font-size: 13px; font-weight: 700; }
.panel-title { margin-bottom: 8px; color: #18212b; font-size: 25px; font-weight: 750; }
.panel-description { color: #687582; }
</style>
