<script setup lang="ts">
import { onMounted, ref } from 'vue'
import DOMPurify from 'dompurify'
import { marked } from 'marked'

interface Snapshot {
  id: string
  version_number: number
  content: string
  creation_date: string
}

interface Article {
  id: string
  title: string
  slug: string
  state_id: number
  creation_date: string
  snapshots: Snapshot[]
}

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
const errorMessage = ref('')
const successMessage = ref('')

function stateName(stateId: number) {
  return { 1: 'Draft', 2: 'Published', 3: 'UnPublished' }[stateId] ?? 'Unknown'
}

function renderContent(content: string) {
  return DOMPurify.sanitize(marked.parse(content, { async: false }))
}

function toggleArticle(articleId: string) {
  expandedArticle.value = expandedArticle.value === articleId ? null : articleId
}

function toggleSnapshot(snapshot: Snapshot) {
  selectedSnapshotId.value = snapshot.id
  editorContent.value = snapshot.content
  successMessage.value = ''
  expandedSnapshot.value = expandedSnapshot.value === snapshot.id ? null : snapshot.id
}

async function unpublishArticle(article: Article) {
  errorMessage.value = ''
  unpublishingArticleId.value = article.id

  try {
    const response = await fetch(`/api/writer/article/${article.id}/unpublish`, {
      method: 'POST',
    })
    const data = await response.json() as { state_id?: number; error?: string }

    if (!response.ok) {
      throw new Error(data.error ?? 'Unable to unpublish article.')
    }

    article.state_id = data.state_id ?? 3
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Unable to connect to the backend.'
  } finally {
    unpublishingArticleId.value = null
  }
}

async function deleteSnapshot(article: Article, snapshot: Snapshot) {
  errorMessage.value = ''
  deletingSnapshotId.value = snapshot.id

  try {
    const response = await fetch(`/api/writer/article/snapshot/${snapshot.id}`, {
      method: 'DELETE',
    })
    const data = await response.json() as { error?: string }

    if (!response.ok) {
      throw new Error(data.error ?? 'Unable to delete snapshot.')
    }

    article.snapshots = article.snapshots.filter((item) => item.id !== snapshot.id)
    if (expandedSnapshot.value === snapshot.id) {
      expandedSnapshot.value = null
    }
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Unable to connect to the backend.'
  } finally {
    deletingSnapshotId.value = null
  }
}

async function saveArticleEdit(article: Article) {
  errorMessage.value = ''
  successMessage.value = ''
  savingArticleId.value = article.id

  try {
    const response = await fetch(`/api/writer/article/${article.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: editorContent.value }),
    })
    const data = await response.json() as { error?: string }

    if (!response.ok) {
      throw new Error(data.error ?? 'Unable to save article changes.')
    }

    successMessage.value = 'Article changes saved.'
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Unable to connect to the backend.'
  } finally {
    savingArticleId.value = null
  }
}

async function publishArticle(article: Article) {
  errorMessage.value = ''
  successMessage.value = ''
  publishingArticleId.value = article.id

  try {
    const saveResponse = await fetch(`/api/writer/article/${article.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content: editorContent.value }),
    })
    const saveData = await saveResponse.json() as { error?: string }
    if (!saveResponse.ok) {
      throw new Error(saveData.error ?? 'Unable to save article changes.')
    }

    const response = await fetch(`/api/writer/article/${article.id}/publish`, {
      method: 'POST',
    })
    const data = await response.json() as { error?: string }

    if (!response.ok) {
      throw new Error(data.error ?? 'Unable to publish article.')
    }

    successMessage.value = 'Article published as a new snapshot.'
    selectedSnapshotId.value = null
    expandedSnapshot.value = null
    editorContent.value = ''
    await loadArticles()
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Unable to connect to the backend.'
  } finally {
    publishingArticleId.value = null
  }
}

async function loadArticles() {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const response = await fetch('/api/writer/article/all')
    const data = await response.json() as Article[] | { error?: string }

    if (!response.ok) {
      throw new Error('error' in data && data.error ? data.error : 'Unable to load articles.')
    }

    articles.value = data as Article[]
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : 'Unable to connect to the backend.'
  } finally {
    isLoading.value = false
  }
}

onMounted(loadArticles)
</script>

<template>
  <section class="snapshots-panel">
    <div class="panel-heading">
      <p class="eyebrow">Snapshots</p>
      <h2>Article history</h2>
    </div>

    <p v-if="isLoading" class="status">Loading articles...</p>
    <p v-else-if="errorMessage" class="status error">{{ errorMessage }}</p>
    <p v-else-if="articles.length === 0" class="status">No articles yet.</p>
    <p v-if="successMessage" class="status success">{{ successMessage }}</p>

    <div v-else class="article-list">
      <div v-for="article in articles" :key="article.id" class="article-card">
        <div
          class="article-summary"
          role="button"
          tabindex="0"
          @click="toggleArticle(article.id)"
          @keydown.enter="toggleArticle(article.id)"
          @keydown.space.prevent="toggleArticle(article.id)"
        >
          <div>
            <h3>{{ article.title }}</h3>
            <p>{{ article.slug }} · {{ stateName(article.state_id) }} · {{ article.creation_date }}</p>
          </div>
          <div class="article-actions">
            <button
              v-if="article.state_id === 2"
              class="unpublish-button"
              type="button"
              :disabled="unpublishingArticleId === article.id"
              @click.stop="unpublishArticle(article)"
            >
              {{ unpublishingArticleId === article.id ? 'Unpublishing...' : 'Unpublish' }}
            </button>
            <span class="expand-icon">{{ expandedArticle === article.id ? '−' : '+' }}</span>
          </div>
        </div>

        <div v-if="expandedArticle === article.id" class="snapshot-list">
          <p v-if="article.snapshots.length === 0" class="empty-snapshots">No snapshots for this article.</p>

          <div
            v-for="snapshot in article.snapshots"
            :key="snapshot.id"
            class="snapshot-card"
            :class="{ expanded: expandedSnapshot === snapshot.id }"
            role="button"
            tabindex="0"
            @click="toggleSnapshot(snapshot)"
            @keydown.enter="toggleSnapshot(snapshot)"
            @keydown.space.prevent="toggleSnapshot(snapshot)"
          >
            <div class="snapshot-summary">
              <span>Version {{ snapshot.version_number }}</span>
              <span class="snapshot-date">{{ snapshot.creation_date }}</span>
              <button
                v-if="article.snapshots[0]?.id !== snapshot.id"
                class="delete-button"
                type="button"
                :disabled="deletingSnapshotId === snapshot.id"
                @click.stop="deleteSnapshot(article, snapshot)"
              >
                {{ deletingSnapshotId === snapshot.id ? 'Deleting...' : 'Delete' }}
              </button>
              <span class="expand-icon">{{ expandedSnapshot === snapshot.id ? '−' : '+' }}</span>
            </div>
            <div
              v-if="expandedSnapshot === snapshot.id"
              class="snapshot-content"
              v-html="renderContent(snapshot.content)"
            />
            <div
              v-if="selectedSnapshotId === snapshot.id && article.state_id !== 2"
              class="snapshot-editor"
              @click.stop
            >
              <label :for="`edit-${snapshot.id}`">Edit content</label>
              <textarea
                :id="`edit-${snapshot.id}`"
                v-model="editorContent"
                rows="10"
                @click.stop
              />
              <div class="editor-actions">
                <button
                  class="save-button"
                  type="button"
                  :disabled="savingArticleId === article.id || publishingArticleId === article.id"
                  @click="saveArticleEdit(article)"
                >
                  {{ savingArticleId === article.id ? 'Saving...' : 'Save Changes' }}
                </button>
                <button
                  class="publish-button"
                  type="button"
                  :disabled="savingArticleId === article.id || publishingArticleId === article.id"
                  @click="publishArticle(article)"
                >
                  {{ publishingArticleId === article.id ? 'Publishing...' : 'Publish' }}
                </button>
              </div>
            </div>
            <p v-if="selectedSnapshotId === snapshot.id && article.state_id === 2" class="edit-hint">
              Unpublish this article to edit and publish a new snapshot.
            </p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.snapshots-panel { padding: 30px; border: 1px solid #e0e6eb; border-radius: 14px; background: #fff; box-shadow: 0 8px 28px rgb(25 43 60 / 5%); }
.panel-heading { margin-bottom: 24px; }
.eyebrow { margin: 0 0 8px; color: #65798c; font-size: 12px; font-weight: 750; letter-spacing: .12em; text-transform: uppercase; }
h2 { margin: 0; font-size: 24px; letter-spacing: -.025em; }
.article-list { display: grid; gap: 14px; }
.article-card { border: 1px solid #e0e6eb; border-radius: 10px; background: #fff; }
.article-summary { display: flex; align-items: center; justify-content: space-between; gap: 20px; padding: 20px; cursor: pointer; }
.article-summary:hover, .article-card:has(.snapshot-list) { border-color: #9cb4c8; }
h3 { margin: 0 0 6px; font-size: 18px; }
.article-summary p { margin: 0; color: #748492; font-size: 13px; }
.article-actions { display: flex; align-items: center; gap: 14px; }
.unpublish-button { border: 1px solid #d7b8b8; border-radius: 7px; padding: 7px 10px; background: #fff; color: #9b4b4b; font-size: 12px; font-weight: 700; }
.unpublish-button:hover { border-color: #a23d3d; background: #fff8f8; }
.unpublish-button:disabled { cursor: wait; opacity: .65; }
.expand-icon { color: #55728a; font-size: 22px; font-weight: 400; }
.snapshot-list { display: grid; gap: 8px; border-top: 1px solid #edf0f3; padding: 14px 20px 20px; }
.snapshot-card { border: 1px solid #e5eaee; border-radius: 8px; cursor: pointer; }
.snapshot-card:hover, .snapshot-card.expanded { border-color: #9cb4c8; }
.snapshot-summary { display: grid; grid-template-columns: 1fr auto auto 24px; align-items: center; gap: 14px; padding: 12px 14px; color: #35536d; font-size: 14px; font-weight: 700; }
.snapshot-date { color: #748492; font-size: 12px; font-weight: 400; }
.delete-button { border: 1px solid #d7b8b8; border-radius: 6px; padding: 5px 8px; background: #fff; color: #9b4b4b; font-size: 11px; font-weight: 700; }
.delete-button:hover { border-color: #a23d3d; background: #fff8f8; }
.delete-button:disabled { cursor: wait; opacity: .65; }
.snapshot-content { margin: 0 14px 14px; border-top: 1px solid #edf0f3; padding-top: 14px; color: #344653; line-height: 1.65; }
.snapshot-content :deep(p) { margin: 0 0 12px; }
.snapshot-content :deep(p:last-child) { margin-bottom: 0; }
.snapshot-content :deep(h1), .snapshot-content :deep(h2), .snapshot-content :deep(h3) { margin: 0 0 12px; color: #18212b; line-height: 1.25; }
.snapshot-content :deep(ul), .snapshot-content :deep(ol) { padding-left: 24px; }
.snapshot-content :deep(code) { border-radius: 4px; padding: 2px 5px; background: #f0f3f6; font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }
.snapshot-editor { border-top: 1px solid #edf0f3; padding: 14px; }
.snapshot-editor label { display: block; margin-bottom: 8px; color: #3e4e5c; font-size: 13px; font-weight: 700; }
.snapshot-editor textarea { display: block; width: 100%; resize: vertical; border: 1px solid #d4dde5; border-radius: 7px; padding: 10px; outline: none; color: #18212b; font: inherit; font-family: ui-monospace, SFMono-Regular, Consolas, monospace; line-height: 1.5; }
.snapshot-editor textarea:focus { border-color: #7597b5; box-shadow: 0 0 0 3px rgb(117 151 181 / 15%); }
.editor-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 10px; }
.save-button, .publish-button { border: 1px solid transparent; border-radius: 6px; padding: 8px 12px; font-size: 12px; font-weight: 700; }
.save-button { border-color: #c9d5df; background: #fff; color: #35536d; }
.publish-button { background: #294b67; color: #fff; }
.save-button:disabled, .publish-button:disabled { cursor: wait; opacity: .65; }
.edit-hint { margin: 0; border-top: 1px solid #edf0f3; padding: 12px 14px 0; color: #748492; font-size: 13px; }
.empty-snapshots, .status { color: #687582; font-size: 14px; }
.empty-snapshots { margin: 0; }
.status.error { color: #a23d3d; }
.status.success { color: #267052; }
@media (max-width: 650px) { .snapshots-panel { padding: 22px; } .snapshot-summary { grid-template-columns: 1fr auto 24px; } .snapshot-date { display: none; } }
</style>
