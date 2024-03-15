<script setup>
import { store } from '../store.js';

</script>

<template>

<div>
  <div v-for="(message, index) in store.messages" class="alert alert-dismissible" :class="`alert-${message.type}`" role="alert">
    {{ message.text }}
    <button type="button" class="btn-close" aria-label="Close" @click="store.removeMessage(index)"></button>
  </div>
</div>

</template>