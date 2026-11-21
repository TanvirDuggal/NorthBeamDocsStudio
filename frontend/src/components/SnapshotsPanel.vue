<script setup lang="ts">
import { onMounted, ref } from 'vue'
import DOMPurify from 'dompurify'
import { marked } from 'marked'

interface Snapshot { id: string; version_number: number; content: string; creation_date: string }
interface Article { id: string; title: string; slug: string; state_id: number; creation_date: string; tags: string; draft_content: string; snapshots: Snapshot[] }

const articles = ref<Article[]>([])
const expandedArticle = ref<string | null>(null)
const expandedSnapshot = ref<string | null>(null)
const selectedSnapshotId = ref<string | null>(null)
const editorContent = ref('')
const isLoading = ref(true)
const unpublishingArticleId = ref<string | null>(null)
const deletingSnapshotId = ref<string | null>(null)
const savingArticleId = ref<string | null>(null)
const publishingArticleId = ref<string | null>(null)
const updatingArticleId = ref<string | null>(null)
const editingArticle = ref<Article | null>(null)
const updateContent = ref('')
const updateTags = ref('')
const errorMessage = ref('')
const successMessage = ref('')

function stateName(stateId: number) { return { 1: 'Draft', 2: 'Published', 3: 'UnPublished' }[stateId] ?? 'Unknown' }
function renderContent(content: string) { return DOMPurify.sanitize(marked.parse(content, { async: false })) }
function toggleArticle(articleId: string) { expandedArticle.value = expandedArticle.value === articleId ? null : articleId }
function openUpdateModal(article: Article) { editingArticle.value = article; updateContent.value = article.draft_content || article.snapshots[0]?.content || ''; updateTags.value = article.tags; errorMessage.value = '' }
function closeUpdateModal() { if (updatingArticleId.value === null) { editingArticle.value = null; updateContent.value = ''; updateTags.value = '' } }
function toggleSnapshot(snapshot: Snapshot) { selectedSnapshotId.value = snapshot.id; editorContent.value = snapshot.content; successMessage.value = ''; expandedSnapshot.value = expandedSnapshot.value === snapshot.id ? null : snapshot.id }

async function unpublishArticle(article: Article) {
  errorMessage.value = ''; unpublishingArticleId.value = article.id
  try {
    const response = await fetch(`/api/writer/article/${article.id}/unpublish`, { method: 'POST' })
    const data = await response.json() as { state_id?: number; error?: string }
    if (!response.ok) throw new Error(data.error ?? 'Unable to unpublish article.')
    article.state_id = data.state_id ?? 3
  } catch (error) { errorMessage.value = error instanceof Error ? error.message : 'Unable to connect to the backend.' }
  finally { unpublishingArticleId.value = null }
}

async function deleteSnapshot(article: Article, snapshot: Snapshot) {
  errorMessage.value = ''; deletingSnapshotId.value = snapshot.id
  try {
    const response = await fetch(`/api/writer/article/snapshot/${snapshot.id}`, { method: 'DELETE' })
    const data = await response.json() as { error?: string }
    if (!response.ok) throw new Error(data.error ?? 'Unable to delete snapshot.')
    article.snapshots = article.snapshots.filter((item) => item.id !== snapshot.id)
    if (expandedSnapshot.value === snapshot.id) expandedSnapshot.value = null
  } catch (error) { errorMessage.value = error instanceof Error ? error.message : 'Unable to connect to the backend.' }
  finally { deletingSnapshotId.value = null }
}

async function saveArticleEdit(article: Article) {
  errorMessage.value = ''; successMessage.value = ''; savingArticleId.value = article.id
  try {
    const response = await fetch(`/api/writer/article/${article.id}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ content: editorContent.value }) })
    const data = await response.json() as { error?: string }
    if (!response.ok) throw new Error(data.error ?? 'Unable to save article changes.')
    successMessage.value = 'Article changes saved.'
  } catch (error) { errorMessage.value = error instanceof Error ? error.message : 'Unable to connect to the backend.' }
  finally { savingArticleId.value = null }
}

async function publishArticle(article: Article) {
  errorMessage.value = ''; successMessage.value = ''; publishingArticleId.value = article.id
  try {
    const saveResponse = await fetch(`/api/writer/article/${article.id}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ content: editorContent.value }) })
    const saveData = await saveResponse.json() as { error?: string }
    if (!saveResponse.ok) throw new Error(saveData.error ?? 'Unable to save article changes.')
    const response = await fetch(`/api/writer/article/${article.id}/publish`, { method: 'POST' })
    const data = await response.json() as { error?: string }
    if (!response.ok) throw new Error(data.error ?? 'Unable to publish article.')
    successMessage.value = 'Article published as a new snapshot.'; selectedSnapshotId.value = null; expandedSnapshot.value = null; editorContent.value = ''
    await loadArticles()
  } catch (error) { errorMessage.value = error instanceof Error ? error.message : 'Unable to connect to the backend.' }
  finally { publishingArticleId.value = null }
}

async function publishUpdate() {
  const article = editingArticle.value
  if (!article) return
  errorMessage.value = ''; successMessage.value = ''; updatingArticleId.value = article.id
  try {
    if (article.state_id === 2) {
      const response = await fetch(`/api/writer/article/${article.id}/unpublish`, { method: 'POST' })
      const data = await response.json() as { state_id?: number; error?: string }
      if (!response.ok) throw new Error(data.error ?? 'Unable to unpublish article.')
      article.state_id = data.state_id ?? 3
    }
    const updateResponse = await fetch(`/api/writer/article/${article.id}`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ content: updateContent.value, tags: updateTags.value }) })
    const updateData = await updateResponse.json() as { error?: string }
    if (!updateResponse.ok) throw new Error(updateData.error ?? 'Unable to save article changes.')
    const publishResponse = await fetch(`/api/writer/article/${article.id}/publish`, { method: 'POST' })
    const publishData = await publishResponse.json() as { error?: string }
    if (!publishResponse.ok) throw new Error(publishData.error ?? 'Unable to publish article.')
    editingArticle.value = null; updateContent.value = ''; updateTags.value = ''; successMessage.value = 'Article updated and published as a new snapshot.'
    await loadArticles()
  } catch (error) { errorMessage.value = error instanceof Error ? error.message : 'Unable to connect to the backend.' }
  finally { updatingArticleId.value = null }
}

async function loadArticles() {
  isLoading.value = true; errorMessage.value = ''
  try {
    const response = await fetch('/api/writer/article/all')
    const data = await response.json() as Article[] | { error?: string }
    if (!response.ok) throw new Error('error' in data && data.error ? data.error : 'Unable to load articles.')
    articles.value = data as Article[]
  } catch (error) { errorMessage.value = error instanceof Error ? error.message : 'Unable to connect to the backend.' }
  finally { isLoading.value = false }
}

onMounted(loadArticles)
</script>

<template>
  <section class="snapshots-panel">
    <div class="panel-heading"><div><p class="eyebrow">Snapshots</p><h2>Article history</h2></div></div>
    <p v-if="isLoading" class="status">Loading articles...</p>
    <p v-else-if="errorMessage" class="status error">{{ errorMessage }}</p>
    <p v-else-if="articles.length === 0" class="status">No articles yet.</p>
    <p v-if="successMessage" class="status success">{{ successMessage }}</p>

    <div v-else class="article-list">
      <div v-for="article in articles" :key="article.id" class="article-card">
        <div class="article-summary" role="button" tabindex="0" @click="toggleArticle(article.id)" @keydown.enter="toggleArticle(article.id)" @keydown.space.prevent="toggleArticle(article.id)">
          <div><h3>{{ article.title }}</h3><p>{{ article.slug }} · {{ stateName(article.state_id) }} · {{ article.creation_date }}</p></div>
          <div class="article-actions">
            <button class="update-button" type="button" @click.stop="openUpdateModal(article)">Update</button>
            <button v-if="article.state_id === 2" class="unpublish-button" type="button" :disabled="unpublishingArticleId === article.id" @click.stop="unpublishArticle(article)">{{ unpublishingArticleId === article.id ? 'Unpublishing...' : 'Unpublish' }}</button>
            <span class="expand-icon">{{ expandedArticle === article.id ? '−' : '+' }}</span>
          </div>
        </div>

        <div v-if="expandedArticle === article.id" class="snapshot-list">
          <p v-if="article.snapshots.length === 0" class="empty-snapshots">No snapshots for this article.</p>
          <div v-for="snapshot in article.snapshots" :key="snapshot.id" class="snapshot-card" :class="{ expanded: expandedSnapshot === snapshot.id }" role="button" tabindex="0" @click="toggleSnapshot(snapshot)" @keydown.enter="toggleSnapshot(snapshot)" @keydown.space.prevent="toggleSnapshot(snapshot)">
            <div class="snapshot-summary">
              <span>Version {{ snapshot.version_number }}</span><span class="snapshot-date">{{ snapshot.creation_date }}</span>
              <button v-if="article.snapshots[0]?.id !== snapshot.id" class="delete-button" type="button" :disabled="deletingSnapshotId === snapshot.id" @click.stop="deleteSnapshot(article, snapshot)">{{ deletingSnapshotId === snapshot.id ? 'Deleting...' : 'Delete' }}</button>
              <span class="expand-icon">{{ expandedSnapshot === snapshot.id ? '−' : '+' }}</span>
            </div>
            <div v-if="expandedSnapshot === snapshot.id" class="snapshot-content" v-html="renderContent(snapshot.content)" />
            <div v-if="selectedSnapshotId === snapshot.id && article.state_id !== 2" class="snapshot-editor" @click.stop>
              <label :for="`edit-${snapshot.id}`">Edit content</label><textarea :id="`edit-${snapshot.id}`" v-model="editorContent" rows="10" @click.stop />
              <div class="editor-actions"><button class="save-button" type="button" :disabled="savingArticleId === article.id || publishingArticleId === article.id" @click="saveArticleEdit(article)">{{ savingArticleId === article.id ? 'Saving...' : 'Save Changes' }}</button><button class="publish-button" type="button" :disabled="savingArticleId === article.id || publishingArticleId === article.id" @click="publishArticle(article)">{{ publishingArticleId === article.id ? 'Publishing...' : 'Publish' }}</button></div>
            </div>
            <p v-if="selectedSnapshotId === snapshot.id && article.state_id === 2" class="edit-hint">Unpublish this article to edit and publish a new snapshot.</p>
          </div>
        </div>
      </div>
    </div>

    <div v-if="editingArticle" class="modal-backdrop" @click.self="closeUpdateModal">
      <section class="update-modal" role="dialog" aria-modal="true" aria-labelledby="update-title">
        <div class="modal-heading"><div><p class="eyebrow">Update article</p><h2 id="update-title">{{ editingArticle.title }}</h2></div><button class="close-button" type="button" :disabled="updatingArticleId !== null" @click="closeUpdateModal">×</button></div>
        <label for="update-tags">Tags</label><input id="update-tags" v-model="updateTags" type="text" placeholder="be, fe, api" />
        <label for="update-content">New content</label><textarea id="update-content" v-model="updateContent" rows="14" />
        <p v-if="errorMessage" class="message error">{{ errorMessage }}</p>
        <div class="modal-actions"><button class="cancel-button" type="button" :disabled="updatingArticleId !== null" @click="closeUpdateModal">Cancel</button><button class="publish-button" type="button" :disabled="updatingArticleId !== null" @click="publishUpdate">{{ updatingArticleId !== null ? 'Publishing...' : 'Publish' }}</button></div>
      </section>
    </div>
  </section>
</template>
