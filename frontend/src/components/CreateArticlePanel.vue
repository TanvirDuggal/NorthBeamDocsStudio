<script setup lang="ts">
import { ref } from 'vue'

interface ArticleResponse { slug: string }
const title = ref('')
const content = ref('')
const isSaving = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

async function createArticle(stateId: 1 | 2) {
  errorMessage.value = ''
  successMessage.value = ''
  if (!title.value.trim()) { errorMessage.value = 'Please enter a title.'; return }
  isSaving.value = true
  try {
    const response = await fetch('/api/writer/article', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: title.value, content: content.value, state_id: stateId }),
    })
    const data = await response.json() as ArticleResponse | { error?: string }
    if (!response.ok) throw new Error('error' in data && data.error ? data.error : 'Unable to create article.')
    successMessage.value = `Article created as ${stateId === 1 ? 'draft' : 'published'}: ${(data as ArticleResponse).slug}`
    title.value = ''
    content.value = ''
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Unable to connect to the backend.'
  } finally { isSaving.value = false }
}
</script>

<template>
  <section class="editor-card">
    <div class="editor-heading">
      <div><p class="eyebrow">New article</p><h2>Create an article</h2></div>
      <span class="markdown-badge">Markdown</span>
    </div>
    <form @submit.prevent>
      <label for="title">Title</label>
      <input id="title" v-model="title" type="text" placeholder="Article title" />
      <label for="content">Content</label>
      <textarea id="content" v-model="content" rows="14" placeholder="# Start writing..." />
      <p v-if="errorMessage" class="message error">{{ errorMessage }}</p>
      <p v-if="successMessage" class="message success">{{ successMessage }}</p>
      <div class="actions">
        <button class="action-button secondary" type="button" :disabled="isSaving" @click="createArticle(1)">{{ isSaving ? 'Saving...' : 'Save Draft' }}</button>
        <button class="action-button primary" type="button" :disabled="isSaving" @click="createArticle(2)">{{ isSaving ? 'Saving...' : 'Publish' }}</button>
      </div>
    </form>
  </section>
</template>
