<script setup>
import { RouterView } from 'vue-router';
import Navbar from '@/components/Navbar.vue';
</script>

<template>
  <header>
    <Navbar />
  </header>
  <div class="container mt-3">   
    <RouterView />
  </div>
</template>

<style scoped>
@font-face {
  font-family: 'OsloSans';
  src: url('@/assets/fonts/OsloSans-Light.woff');
  font-weight: normal;
  font-style: normal;
}

@font-face {
  font-family: 'OsloSans';
  src: url('@/assets/fonts/OsloSans-LightItalic.woff');
  font-weight: normal;
  font-style: italic;
}

@font-face {
  font-family: 'OsloSans';
  src: url('@/assets/fonts/OsloSans-Regular.woff');
  font-weight: 500;
  font-style: normal;
}

@font-face {
  font-family: 'OsloSans';
  src: url('@/assets/fonts/OsloSans-RegularItalic.woff');
  font-weight: 500;
  font-style: italic;
}

@font-face {
  font-family: 'OsloSans';
  src: url('@/assets/fonts/OsloSans-Medium.woff');
  font-weight: bold;
  font-style: normal;
}

@font-face {
  font-family: 'OsloSans';
  src: url('@/assets/fonts/OsloSans-MediumItalic.woff');
  font-weight: bold;
  font-style: italic;
}
/* 
@font-face {
  font-family: 'OsloSans';
  src: url('@/assets/fonts/OsloSans-Bold.woff');
  font-weight: 700;
  font-style: normal;
}

@font-face {
  font-family: 'OsloSans';
  src: url('@/assets/fonts/OsloSans-BoldItalic.woff');
  font-weight: 700;
  font-style: italic;
}
 */

</style>




