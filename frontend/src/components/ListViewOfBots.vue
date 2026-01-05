<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import BotAvatar from '@/components/BotAvatar.vue'
import { store } from '@/store.js'

const props = defineProps({
  filteredBots: Array,
  botLink: Function,
  toggleFavorite: Function,
  isFavoriteView: Boolean,
})

const titleColWidth = store.isEmployee || store.isAdmin ? 'col-3' : 'col-2'
</script>

<template>
  <div class="col">
    <div
      v-for="bot in props.filteredBots"
      :key="bot.uuid"
      class="row border oslo-bg-light p-2 mb-2"
    >
      <RouterLink active-class="active" class="col-sm-1 col-2" :to="botLink(bot)">
        <div style="width: 40px">
          <BotAvatar :avatarScheme="bot.avatarScheme" />
        </div>
      </RouterLink>

      <!-- favorite & category icon -->
      <div v-if="store.isEmployee" class="col-1">
        <div v-if="!bot.isMandatory" class="mb-2">
          <a href="#" @click.prevent="props.toggleFavorite(bot)">
            <img
              v-if="bot.favorite"
              src="@/components/icons/star_solid.svg"
              alt="Fjern som favoritt"
              title="Fjern som favoritt"
              class="category_icon"
            />
            <img
              v-else
              src="@/components/icons/star.svg"
              alt="Sett som favoritt"
              title="Sett som favoritt"
              class="category_icon"
            />
          </a>
          <div v-if="bot.personal && isFavoriteView">
            <img src="@/components/icons/user_outline.svg" class="category_icon" />
          </div>
          <div v-if="!bot.isMandatory && !bot.personal && isFavoriteView">
            <img src="@/components/icons/books.svg" class="category_icon" />
          </div>
        </div>
      </div>
      <!-- distributed to -->
      <div v-if="store.isEmployee" class="col-2">
        <div v-for="group in bot.distributedTo">
          <span class="badge text-bg-secondary text-wrap">
            <span v-if="group.goType === 'b'">Klasse</span>
            {{ group.displayName }}
          </span>
        </div>
      </div>
      <!-- access count -->
      <div v-if="store.isAdmin" class="col-1">
        {{ bot.accessCount }}
      </div>
      <!-- title -->
      <div :class="titleColWidth">
        <RouterLink active-class="active" :to="botLink(bot)">
          {{ bot.botTitle }}
        </RouterLink>
      </div>
      <!-- bot info -->
      <div class="col">
        {{ bot.botInfo }}
      </div>
    </div>
  </div>
</template>
