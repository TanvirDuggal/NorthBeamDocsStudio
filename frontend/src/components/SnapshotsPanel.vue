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
const isLoading = ref(true)
const errorMessage = ref('')

function stateName(stateId: number) {
  return { 1: 'Draft', 2: 'Published', 3: 'UnPublished' }[stateId] ?? 'Unknown'
}

function renderContent(content: string) {
  return DOMPurify.sanitize(marked.parse(content, { async: false }))
}

function toggleArticle(articleId: string) {
  expandedArticle.value = expandedArticle.value === articleId ? null : articleId
}

function toggleSnapshot(snapshotId: string) {
  expandedSnapshot.value = expandedSnapshot.value === snapshotId ? null : snapshotId
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
          <span class="expand-icon">{{ expandedArticle === article.id ? '−' : '+' }}</span>
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
            @click="toggleSnapshot(snapshot.id)"
            @keydown.enter="toggleSnapshot(snapshot.id)"
            @keydown.space.prevent="toggleSnapshot(snapshot.id)"
          >
            <div class="snapshot-summary">
              <span>Version {{ snapshot.version_number }}</span>
              <span class="snapshot-date">{{ snapshot.creation_date }}</span>
              <span class="expand-icon">{{ expandedSnapshot === snapshot.id ? '−' : '+' }}</span>
            </div>
            <div
              v-if="expandedSnapshot === snapshot.id"
              class="snapshot-content"
              v-html="renderContent(snapshot.content)"
            />
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
.expand-icon { color: #55728a; font-size: 22px; font-weight: 400; }
.snapshot-list { display: grid; gap: 8px; border-top: 1px solid #edf0f3; padding: 14px 20px 20px; }
.snapshot-card { border: 1px solid #e5eaee; border-radius: 8px; cursor: pointer; }
.snapshot-card:hover, .snapshot-card.expanded { border-color: #9cb4c8; }
.snapshot-summary { display: grid; grid-template-columns: 1fr auto 24px; align-items: center; gap: 14px; padding: 12px 14px; color: #35536d; font-size: 14px; font-weight: 700; }
.snapshot-date { color: #748492; font-size: 12px; font-weight: 400; }
.snapshot-content { margin: 0 14px 14px; border-top: 1px solid #edf0f3; padding-top: 14px; color: #344653; line-height: 1.65; }
.snapshot-content :deep(p) { margin: 0 0 12px; }
.snapshot-content :deep(p:last-child) { margin-bottom: 0; }
.snapshot-content :deep(h1), .snapshot-content :deep(h2), .snapshot-content :deep(h3) { margin: 0 0 12px; color: #18212b; line-height: 1.25; }
.snapshot-content :deep(ul), .snapshot-content :deep(ol) { padding-left: 24px; }
.snapshot-content :deep(code) { border-radius: 4px; padding: 2px 5px; background: #f0f3f6; font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }
.empty-snapshots, .status { color: #687582; font-size: 14px; }
.empty-snapshots { margin: 0; }
.status.error { color: #a23d3d; }
@media (max-width: 650px) { .snapshots-panel { padding: 22px; } .snapshot-summary { grid-template-columns: 1fr 24px; } .snapshot-date { display: none; } }
</style>
