<script setup>
import { ClassicEditor } from 'ckeditor5'
import { createHtmlContent, editorConfig } from '@/utils/editorConfig.js'
import { useRoute, useRouter } from 'vue-router'
import { store } from '../store.js'
import { axiosInstance as axios } from '../clients'
import { ref, watchEffect, computed } from 'vue'

const page = ref({
  title: '',
  content: '',
  slug: '',
  accessableBy: 'student',
  hasSeparateMenu: false,
})
const showEdit = ref(false)
const fileInput = ref(null)
const route = useRoute()
const router = useRouter()

const htmlContent = computed(() => createHtmlContent(page.value.content))

const fetchPage = async () => {
  try {
    if (!route.params.slug) {
      showEdit.value = true
      return
    }

    const { data } = await axios.get('/api/info_page/' + route.params.slug)

    if (data) {
      showEdit.value = false
      page.value = data
    }
  } catch (error) {
    store.addMessage(`Kunne ikke laste siden. Vennligst prøv igjen senere.`, 'danger')
  }
}

const createPage = async () => {
  try {
    if (!page.value.title || !page.value.content) return

    const { data } = await axios.post('/api/info_page/', page.value)
    if (data) {
      page.value = data
      showEdit.value = false
    }
  } catch (error) {
    store.addMessage(`Kunne ikke opprette siden. Vennligst prøv igjen senere.`, 'danger')
  }
}

const updatePage = async () => {
  if (!page.value.title || !page.value.content) return

  try {
    const { data } = await axios.put(`/api/info_page/${route.params.slug}`, page.value)
    if (data) {
      page.value = data
      showEdit.value = false
    }
  } catch (error) {
    store.addMessage(`Kunne ikke oppdatere siden. Vennligst prøv igjen senere.`, 'danger')
    await fetchPage()
  }
}

const deletePage = async () => {
  try {
    if (!route.params.slug) return

    await axios.delete(`/api/info_page/${route.params.slug}`)
    router.push('/')
  } catch (error) {
    store.addMessage(`Kunne ikke slette siden. Vennligst prøv igjen senere.`, 'danger')
  }
}

const handleFileSelect = async event => {
  var formData = new FormData()
  fileInput.value = event.target.files[0]
  formData.append('upload', fileInput.value)
  try {
    const { data } = await axios.post('/api/upload_info_file', formData)
  } catch (error) {
    store.addMessage(`Kunne ikke laste opp dokumentet. Vennligst prøv igjen senere.`, 'danger')
  }
}

watchEffect(async () => {
  await fetchPage()
})
</script>

<template>
  <div v-if="!showEdit" class="container my-4">
    <button v-if="store.isAdmin" @click="showEdit = true" class="btn btn-primary mb-4">
      Rediger
    </button>
    <div class="container infotext my-4">
      <span v-html="htmlContent"></span>
    </div>
  </div>

  <div v-else-if="store.isAdmin" class="container my-4">
    <div class="card">
      <h1 class="card-header">{{ page.title }}</h1>
      <div class="card-body">
        <div class="mb-3 d-flex gap-2">
          <button @click="showEdit = false" class="btn btn-primary">Forhåndsvisning</button>
          <label for="file-input" class="btn btn-secondary">Last opp dokument</label>
          <input id="file-input" type="file" hidden @change="handleFileSelect" />
          <button
            v-if="route.params.slug"
            @click="updatePage"
            class="btn btn-success"
            :disabled="!page.title || !page.content"
          >
            Lagre
          </button>
          <button
            v-else
            @click="createPage"
            class="btn btn-success"
            :disabled="!page.title || !page.content"
          >
            Opprett
          </button>
          <button v-if="route.params.slug" @click="deletePage" class="btn btn-danger">Slett</button>
        </div>

        <div class="mb-3">
          <label class="form-label d-block">Tilgang</label>
          <div class="form-check form-check-inline">
            <input
              class="form-check-input"
              type="radio"
              id="accessAll"
              value="all"
              v-model="page.accessableBy"
            />
            <label class="form-check-label" for="accessAll">Åpen for alle</label>
          </div>
          <div class="form-check form-check-inline">
            <input
              class="form-check-input"
              type="radio"
              id="accessStud"
              value="student"
              v-model="page.accessableBy"
            />
            <label class="form-check-label" for="accessStud">Elever og ansatte</label>
          </div>
          <div class="form-check form-check-inline">
            <input
              class="form-check-input"
              type="radio"
              id="accessEmp"
              value="employee"
              v-model="page.accessableBy"
            />
            <label class="form-check-label" for="accessEmp">Bare ansatte</label>
          </div>
        </div>

        <div class="mb-3 form-check">
          <input
            type="checkbox"
            class="form-check-input"
            id="separateMenuCheck"
            v-model="page.hasSeparateMenu"
          />
          <label class="form-check-label" for="separateMenuCheck">Vis i eget menyvalg</label>
        </div>

        <div class="mb-3">
          <label for="titleInput" class="form-label">Tittel</label>
          <input
            type="text"
            class="form-control"
            id="titleInput"
            v-model="page.title"
            maxlength="50"
          />
          <div class="form-text text-end">{{ page.title.length }}/50</div>
        </div>
        <div class="mb-3"></div>

        <ckeditor
          class="form-control"
          :editor="ClassicEditor"
          v-model="page.content"
          :config="editorConfig"
        ></ckeditor>
      </div>
    </div>
  </div>
</template>
