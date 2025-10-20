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
  accessable_by: 'stud',
})
const showEdit = ref(false)
const route = useRoute()
const router = useRouter()

const htmlContent = computed(() => createHtmlContent(page.value.content))

const fetchPage = async () => {
  try {
    if (!route.params.slug) {
      // if (!store.isAdmin) return router.push('/')
      showEdit.value = true

      // TODO new page

      return
    }

    const { data } = await axios.get('/api/info_page/' + route.params.slug)

    if (data) {
      showEdit.value = false
      page.value = data
    }
  } catch (error) {
    store.addMessage(`Kunne ikke laste siden. Vennligst prøv igjen senere.`, 'danger')
  } finally {
    // isLoading.value = false
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
  } finally {
    // isLoading.value = false
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
  } finally {
    // isLoading.value = false
  }
}

const deletePage = async () => {
  try {
    if (!route.params.slug) return

    await axios.delete(`/api/info_page/${route.params.slug}`)
    router.push('/')
  } catch (error) {
    store.addMessage(`Kunne ikke slette siden. Vennligst prøv igjen senere.`, 'danger')
  } finally {
    // isLoading.value = false
  }
}

watchEffect(async () => {
  await fetchPage()
})
</script>

<template>
  <!-- <span class="infotext" v-html="contentText"></span> -->

  <div v-if="!showEdit" class="container my-4">
    <button v-if="store.isAdmin" @click="(showEdit = true)" class="btn btn-primary mb-4">
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
          <button @click="(showEdit = false)" class="btn btn-primary">Forhåndsvisning</button>
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
              v-model="page.accessable_by"
            />
            <label class="form-check-label" for="accessAll">Åpen for alle</label>
          </div>
          <div class="form-check form-check-inline">
            <input
              class="form-check-input"
              type="radio"
              id="accessStud"
              value="stud"
              v-model="page.accessable_by"
            />
            <label class="form-check-label" for="accessStud">Elever og ansatte</label>
          </div>
          <div class="form-check form-check-inline">
            <input
              class="form-check-input"
              type="radio"
              id="accessEmp"
              value="emp"
              v-model="page.accessable_by"
            />
            <label class="form-check-label" for="accessEmp">Bare ansatte</label>
          </div>
        </div>
        <!-- <div class="form-check form-switch mb-3">
          <input class="form-check-input" type="checkbox" id="publicSwitch" v-model="page.public" />
          <label class="form-check-label" for="publicSwitch">Offentlig</label>
        </div> -->
        <div class="mb-3">
          <label for="titleInput" class="form-label">Tittel</label>
          <input type="text" class="form-control" id="titleInput" v-model="page.title" />
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
