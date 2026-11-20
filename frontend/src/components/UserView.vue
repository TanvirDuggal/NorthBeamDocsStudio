<script setup lang="ts">
import { onMounted, ref } from 'vue'
import DOMPurify from 'dompurify'
import { marked } from 'marked'

interface Article {
  title: string
  content: string
  creation_date: string
  slug: string
}

defineEmits<{ goHome: [] }>()

const articles = ref<Article[]>([])
const expandedSlug = ref<string | null>(null)
const isLoading = ref(true)
const errorMessage = ref('')

function toggleArticle(slug: string) {
  expandedSlug.value = expandedSlug.value === slug ? null : slug
}

function renderContent(content: string) {
  return DOMPurify.sanitize(marked.parse(content, { async: false }))
}

async function loadArticles() {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const response = await fetch('/api/writer/article')
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
  <section class="page">
    <div class="page-heading">
      <button class="back-link" type="button" @click="$emit('goHome')">← Home</button>
      <p class="eyebrow">User</p>
      <h1>Published articles</h1>
    </div>

    <p v-if="isLoading" class="status">Loading articles...</p>
    <p v-else-if="errorMessage" class="status error">{{ errorMessage }}</p>
    <p v-else-if="articles.length === 0" class="status">No published articles yet.</p>

    <div v-else class="article-list">
      <div
        v-for="article in articles"
        :key="article.slug"
        class="article-card"
        :class="{ expanded: expandedSlug === article.slug }"
        role="button"
        tabindex="0"
        @click="toggleArticle(article.slug)"
        @keydown.enter="toggleArticle(article.slug)"
        @keydown.space.prevent="toggleArticle(article.slug)"
      >
        <div class="article-summary">
          <div>
            <h2>{{ article.title }}</h2>
            <p class="article-meta">{{ article.slug }} · {{ article.creation_date }}</p>
          </div>
          <span class="expand-icon">{{ expandedSlug === article.slug ? '−' : '+' }}</span>
        </div>

        <div
          v-if="expandedSlug === article.slug"
          class="article-content"
          v-html="renderContent(article.content)"
        />
      </div>
    </div>
  </section>
</template>

<style scoped>
.page { width: min(100% - 48px, 1040px); margin: 0 auto; padding: 72px 0; }
.page-heading { margin-bottom: 32px; }
.eyebrow { margin: 0 0 8px; color: #65798c; font-size: 12px; font-weight: 750; letter-spacing: .12em; text-transform: uppercase; }
h1 { margin: 0; font-size: clamp(30px, 4vw, 46px); letter-spacing: -.04em; }
.back-link { margin-bottom: 24px; padding: 0; border: 0; background: transparent; color: #687582; font-size: 14px; }
.article-list { display: grid; gap: 12px; }
.article-card { border: 1px solid #e0e6eb; border-radius: 12px; background: #fff; box-shadow: 0 8px 28px rgb(25 43 60 / 5%); cursor: pointer; }
.article-card:hover, .article-card.expanded { border-color: #9cb4c8; }
.article-summary { display: flex; align-items: center; justify-content: space-between; gap: 20px; padding: 22px 24px; }
h2 { margin: 0 0 7px; font-size: 20px; letter-spacing: -.02em; }
.article-meta { margin: 0; color: #748492; font-size: 13px; }
.expand-icon { color: #55728a; font-size: 25px; font-weight: 400; }
.article-content { margin: 0 24px 22px; border-top: 1px solid #edf0f3; padding-top: 20px; color: #344653; line-height: 1.65; }
.article-content :deep(p) { margin: 0 0 14px; }
.article-content :deep(p:last-child) { margin-bottom: 0; }
.article-content :deep(h1), .article-content :deep(h2), .article-content :deep(h3) { margin: 0 0 14px; color: #18212b; line-height: 1.25; }
.article-content :deep(ul), .article-content :deep(ol) { padding-left: 24px; }
.article-content :deep(code) { border-radius: 4px; padding: 2px 5px; background: #f0f3f6; font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }
.status { color: #687582; }
.status.error { color: #a23d3d; }
@media (max-width: 650px) { .page { padding: 48px 0; } .article-summary { padding: 18px; } .article-content { margin: 0 18px 18px; } }
</style>
