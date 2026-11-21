<script setup lang="ts">
import { onMounted, ref } from 'vue'
import DOMPurify from 'dompurify'
import { marked } from 'marked'

interface Article {
  title: string
  content: string
  creation_date: string
  slug: string
  tags: string
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
            <p class="article-meta">{{ article.slug }} · {{ article.creation_date }}<span v-if="article.tags"> · {{ article.tags }}</span></p>
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
