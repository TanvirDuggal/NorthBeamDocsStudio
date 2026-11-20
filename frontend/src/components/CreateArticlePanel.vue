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

<style scoped>
.editor-card { padding: 30px; border: 1px solid #e0e6eb; border-radius: 14px; background: #fff; box-shadow: 0 8px 28px rgb(25 43 60 / 5%); }
.editor-heading { display: flex; align-items: flex-start; justify-content: space-between; margin-bottom: 28px; }
.eyebrow { margin: 0 0 8px; color: #65798c; font-size: 12px; font-weight: 750; letter-spacing: .12em; text-transform: uppercase; }
h2 { margin: 0; font-size: 24px; letter-spacing: -.025em; }
.markdown-badge { padding: 6px 10px; border-radius: 999px; background: #f0f3f6; color: #65798c; font-size: 12px; font-weight: 700; }
label { display: block; margin: 0 0 8px; color: #3e4e5c; font-size: 13px; font-weight: 700; }
input, textarea { display: block; width: 100%; margin-bottom: 22px; border: 1px solid #d4dde5; border-radius: 8px; padding: 12px 14px; outline: none; background: #fbfcfd; color: #18212b; font: inherit; }
input:focus, textarea:focus { border-color: #7597b5; box-shadow: 0 0 0 3px rgb(117 151 181 / 15%); }
textarea { min-height: 260px; resize: vertical; font-family: ui-monospace, SFMono-Regular, Consolas, monospace; line-height: 1.55; }
.actions { display: flex; justify-content: flex-end; gap: 10px; }
.action-button { border: 1px solid transparent; border-radius: 8px; padding: 11px 18px; font-weight: 700; }
.action-button:disabled { cursor: wait; opacity: .65; }
.action-button.secondary { border-color: #c9d5df; background: #fff; color: #35536d; }
.action-button.primary { background: #294b67; color: #fff; }
.message { margin: -6px 0 20px; font-size: 14px; }
.message.error { color: #a23d3d; }
.message.success { color: #267052; }
@media (max-width: 650px) { .editor-card { padding: 22px; } }
</style>
