<script setup>
import { RouterLink } from 'vue-router';
import axios from 'axios';
import { onMounted, computed, ref, watchEffect } from 'vue';
import { useRoute } from 'vue-router';
import { store } from '../store.js';


const menuItems = ref([]);

const getMenuItems = async () => {
  try {
    const { data } = await axios.get('/api/menu_items');
    menuItems.value = data.menuItems;
    store.isAdmin = data.role ? data.role.is_admin : false;
    store.isEmployee = data.role ? data.role.is_employee : false;
    store.editGroups = data.role ? data.role.edit_g : false;
  } catch (error) {
    console.log(error);
  }
}


watchEffect(() => {
  const route = useRoute()
  getMenuItems()
});  


</script>

<template>

<header>
    <div id="header" class="d-flex justify-content-between p-4 oslo-bg-light">
        <RouterLink active-class="active" class="nav-link" to="/">
            <h1 class="h3 p-3">
                Kunstig intelligens for Osloskolen
            </h1>
        </RouterLink>
        <RouterLink active-class="active" class="logo" to="/">
            <img src="@/assets/img/oslo_logo_sort.svg" alt="Oslologo">
        </RouterLink>
    </div>
</header>

<nav class="d-flex flex-row-reverse">
  <div v-if="menuItems.length === 0" class="nav-item">
    <a class="nav-link p-3" href="/auth/feidelogin">
      Logg inn
    </a>
  </div>
  <div v-else class="nav-item">
    <a class="nav-link p-3" href="/auth/logout">
      Logg ut
    </a>
  </div>
  <div v-for="item in menuItems" :key="item.id" class="nav-item">
      <RouterLink active-class="active" class="nav-link p-3" :class="item.class" :to="item.url">
          {{ item.title }}
      </RouterLink>
  </div>
</nav>


</template>