<script setup>
import { ref, computed } from 'vue'
import { store } from '@/store.js'
import { axiosInstance as axios } from '../clients'
import GridView from '@/components/GridViewOfBots.vue'
import ListView from '@/components/ListViewOfBots.vue'

const filterMode = ref(localStorage.getItem('filterMode') || 'favorites')
const isListView = ref(localStorage.getItem('isListView') === 'true' || false)
const isFilterSelected = ref(false)
const activeBot = ref(null)

const props = defineProps({
  bots: Array,
  isBotFilteringEnabled: Boolean,
  tagCategories: Array,
})

const filteredBots = computed(() => {
  var bots = props.bots
  bots.sort((a, b) => b.isMandatory - a.isMandatory || a.botTitle.localeCompare(b.botTitle))
  if (!store.isEmployee && !store.isAdmin) {
    return bots // Show all bots for students
  }
  if (filterMode.value === 'library') {
    let botsFiltered = bots
    props.tagCategories.forEach(tagCategory => {
      const filterArray = tagCategory.tagItems
        .filter(tagItem => tagItem.checked)
        .map(tagItem => tagItem.weight)
      if (filterArray.length > 0) {
        let binarySum = filterArray.reduce((partialSum, a) => partialSum + Math.pow(2, a), 0)
        botsFiltered = botsFiltered.filter(
          bot =>
            bot.tag.filter(tag => tag.categoryId === tagCategory.id && tag.tagValue & binarySum)
              .length > 0
        )
      }
    })
    return botsFiltered.filter(bot => !bot.personal && !bot.isMandatory)
  } else if (filterMode.value === 'personal') {
    return bots.filter(bot => bot.personal)
  } else if (filterMode.value === 'favorites') {
    return bots.filter(bot => bot.isMandatory || bot.favorite)
  } else {
    return bots
  }
})

const tagCategoriesSorted = computed(() => {
  return props.tagCategories.sort((a, b) => a.order - b.order)
})

const tagItemSorted = tagCategory => {
  return tagCategory.tagItems.sort((a, b) => a.order - b.order)
}

const toggleFavorite = async bot => {
  try {
    const { data } = await axios.put('/api/favorite/' + bot.uuid)
    bot.favorite = data.favorite
  } catch (error) {
    console.log(error)
  }
}

const changeFilterMode = mode => {
  filterMode.value = mode
  localStorage.setItem('filterMode', mode)
}

const toggleIsListView = () => {
  isListView.value = !isListView.value
  localStorage.setItem('isListView', isListView.value)
}

const setActiveBot = bot => {
  activeBot.value = bot
}

const enableCreateBot = computed(() => {
  return store.isAuthor || store.isAdmin || (store.isEmployee && filterMode.value === 'personal')
})

const showSideBar = computed(
  () => filterMode.value === 'library' && props.isBotFilteringEnabled && isFilterSelected.value
)

const botLink = bot => (bot.imgBot ? 'imgbot/' + bot.uuid : 'bot/' + bot.uuid)
</script>

<template>
  <!-- Botinfo Modal -->
  <div
    class="modal fade"
    id="botinfo"
    tabindex="-1"
    aria-labelledby="botInfoLabel"
    aria-hidden="true"
  >
    <div class="modal-dialog">
      <div v-if="activeBot" class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5" id="botInfoLabel">
            {{ activeBot.botTitle }}
          </h1>
          <button
            type="button"
            class="btn-close"
            data-bs-dismiss="modal"
            aria-label="Close"
          ></button>
        </div>
        <div class="modal-body">
          <span v-html="activeBot.botInfo"></span>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn oslo-btn-secondary" data-bs-dismiss="modal">Lukk</button>
        </div>
      </div>
    </div>
  </div>

  <!-- show filter tabs -->
  <div v-if="store.isEmployee || store.isAdmin" class="mb-3">
    <ul class="nav nav-tabs">
      <li class="nav-item">
        <a
          class="nav-link"
          :class="filterMode === 'favorites' ? 'active' : ''"
          href="#"
          @click.prevent="changeFilterMode('favorites')"
        >
          <img src="@/components/icons/star_solid.svg" class="category_icon" />
          Favoritter
        </a>
      </li>
      <li class="nav-item">
        <a
          class="nav-link"
          :class="filterMode === 'personal' ? 'active' : ''"
          href="#"
          @click.prevent="changeFilterMode('personal')"
        >
          <img src="@/components/icons/user_outline.svg" class="category_icon" />
          Personlige
        </a>
      </li>
      <li class="nav-item">
        <a
          class="nav-link"
          :class="filterMode === 'library' ? 'active' : ''"
          href="#"
          @click.prevent="changeFilterMode('library')"
        >
          <img src="@/components/icons/books.svg" class="category_icon" />
          Bibliotek
        </a>
      </li>
      <!-- Push following items to the right -->
      <li class="ms-auto"></li>
      <li v-if="enableCreateBot && filterMode === 'library'" class="ms-1">
        <RouterLink :to="{ name: 'newbot', params: { method: 'newlib' } }">
          <img
            src="@/components/icons/plus.svg"
            class="icon"
            role="button"
            alt="Ny bibliotekbot"
            title="Opprett ny bibliotekbot"
          />
        </RouterLink>
      </li>
      <li v-if="enableCreateBot && filterMode === 'personal'" class="ms-1">
        <RouterLink :to="{ name: 'newbot', params: { method: 'new' } }">
          <img src="@/components/icons/plus.svg" class="icon" alt="Ny bot" title="Opprett ny bot" />
        </RouterLink>
      </li>
      <li v-if="filterMode === 'library' && props.isBotFilteringEnabled">
        <a role="button" href="#" @click.prevent="isFilterSelected = !isFilterSelected">
          <img
            v-if="isFilterSelected"
            src="@/components/icons/filter_off.svg"
            class="icon"
            role="button"
            alt="Skjul filter"
            title="Skjul filter"
          />
          <img
            v-else
            src="@/components/icons/filter.svg"
            class="icon"
            role="button"
            alt="Vis filter"
            title="Vis filter"
          />
        </a>
      </li>
      <li class="ms-1">
        <a role="button" href="#" @click.prevent="toggleIsListView">
          <img
            v-if="isListView"
            src="@/components/icons/grid.svg"
            class="icon"
            role="button"
            alt="Rutenettvisning"
            title="Rutenettvisning"
          />
          <img
            v-else
            src="@/components/icons/list.svg"
            class="icon"
            role="button"
            alt="Listevisning"
            title="Listevisning"
          />
        </a>
      </li>
    </ul>
  </div>
  <!-- For students -->
  <div v-else class="mb-3">
    <ul class="nav nav-tabs">
      <!-- Push following items to the right -->
      <li class="ms-auto mb-3">
        <a role="button" href="#" @click.prevent="toggleIsListView">
          <img
            v-if="isListView"
            src="@/components/icons/grid.svg"
            class="icon"
            role="button"
            alt="Rutenettvisning"
            title="Rutenettvisning"
          />
          <img
            v-else
            src="@/components/icons/list.svg"
            class="icon"
            role="button"
            alt="Listevisning"
            title="Listevisning"
          />
        </a>
      </li>
    </ul>
  </div>

  <div v-if="filterMode === 'library' && props.isBotFilteringEnabled" class="mb-2">
    <span v-for="tagCategory in tagCategoriesSorted">
      <span v-for="tagItem in tagItemSorted(tagCategory)" :key="tagItem.id">
        <span
          v-if="tagItem.checked"
          class="badge bg-secondary me-1 mb-1"
          style="font-size: 0.8em"
          data-bs-theme="dark"
        >
          {{ tagItem.label }}
          <button
            type="button"
            class="btn-close btn-sm"
            aria-label="Close"
            @click.prevent="tagItem.checked = false"
          ></button>
        </span>
      </span>
    </span>
  </div>

  <div class="row align-items-stretch">
    <!-- sidebar filter -->
    <div v-if="showSideBar" class="col-xxl-2 col-xl-2 col-lg-3 col-md-3 col-12 mb-2">
      <div class="card card-body">
        <div v-for="tagCategory in tagCategoriesSorted" :key="tagCategory.id">
          <div>{{ tagCategory.label }}</div>
          <div v-for="tagItem in tagItemSorted(tagCategory)" :key="tagItem.id" class="form-check">
            <input
              class="form-check-input"
              type="checkbox"
              v-model="tagItem.checked"
              :id="`filterCheck${tagCategory.id}:${tagItem.id}`"
            />
            <label class="form-check-label" :for="`filterCheck${tagCategory.id}:${tagItem.id}`">
              {{ tagItem.label }}
            </label>
          </div>
        </div>
      </div>
    </div>

    <ListView
      v-if="isListView"
      :filteredBots="filteredBots"
      :botLink="botLink"
      :toggleFavorite="toggleFavorite"
      :isFavoriteView="filterMode === 'favorites'"
    />
    <GridView
      v-else
      :filteredBots="filteredBots"
      :setActiveBot="setActiveBot"
      :botLink="botLink"
      :toggleFavorite="toggleFavorite"
      :showSideBar="showSideBar"
      :isFavoriteView="filterMode === 'favorites'"
    />
  </div>
</template>

<style>
.category_icon {
  width: 20px;
}
</style>
