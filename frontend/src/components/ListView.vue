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

      <div class="col-1">
        <div v-if="store.isEmployee">
          <div v-if="!bot.mandatory" class="mb-2">
            <a href="#" @click.prevent="props.toggleFavorite(bot)">
              <img
                v-if="bot.favorite"
                src="@/components/icons/star_solid.svg"
                alt="Fjern som favoritt"
                title="Fjern som favoritt"
                style="width: 20px"
              />
              <img
                v-else
                src="@/components/icons/star.svg"
                alt="Sett som favoritt"
                title="Sett som favoritt"
                style="width: 20px"
              />
            </a>
          </div>
          <div v-if="bot.mandatory && isFavoriteView"><p class="oslo-text-light"></p></div>
          <div v-if="bot.personal && isFavoriteView">
            <img src="@/components/icons/user_outline.svg" style="width: 20px" />
          </div>
          <div v-if="!bot.mandatory && !bot.personal && isFavoriteView">
            <img src="@/components/icons/books.svg" style="width: 20px" />
          </div>
        </div>
        <div v-if="store.isAdmin" class="col-2 px-0">
          <span class="badge text-bg-secondary">
            {{ bot.accessCount }}
          </span>
        </div>
      </div>
      <RouterLink active-class="active" class="col-4" :to="botLink(bot)">
        {{ bot.botTitle }}
      </RouterLink>
      <div class="col">
        {{ bot.botInfo }}
      </div>
    </div>
  </div>
</template>
