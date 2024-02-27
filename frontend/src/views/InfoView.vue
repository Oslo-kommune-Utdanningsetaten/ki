<script setup>
import { RouterLink, useRouter, useRoute } from 'vue-router';
import axios from 'axios';
import { ref, onMounted, watchEffect } from 'vue'

const contentText = ref('');
const page = ref('');
const route = useRoute();
// page.value = route.params.page;

watchEffect(() => {
  getcontent()
});

async function getcontent() {
  try {
    const { data } = await axios.get('/api/page_text/' + route.params.page);
    contentText.value = data.content_text;
    // page.value = data.page;
  } catch (error) {
    console.log(error);
  }
}

</script>

<template>
  <span v-html="contentText"></span>
</template>
