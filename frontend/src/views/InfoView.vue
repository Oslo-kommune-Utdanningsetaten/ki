<script setup>
import {  useRoute } from 'vue-router'
import { axiosInstance as axios } from '../clients'
import { ref, watchEffect } from 'vue'

const contentText = ref('')
const route = useRoute()

watchEffect(() => {
  getcontent()
})

async function getcontent() {
  try {
    const { data } = await axios.get('/api/page_text/' + route.params.page)
    contentText.value = data.content_text
    version.value = data.version
  } catch (error) {
    console.log(error)
  }
}
</script>

<template>
  <span class="infotext" v-html="contentText"></span>
</template>
