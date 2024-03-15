<script setup>
import { RouterLink, useRouter, useRoute } from 'vue-router';
import { ref, onMounted, watchEffect } from 'vue'
import { store } from '../store.js';

const route = useRoute();
const $router = useRouter();


watchEffect(() => {
  route.params.text ? store.addMessage(route.params.text, route.params.type) : null;
  $router.push('/');
});

</script>

<template>
</template>
