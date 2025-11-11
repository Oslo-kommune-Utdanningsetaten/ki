<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import BotAvatar from '@/components/BotAvatar.vue'
import { store } from '@/store.js'

const props = defineProps({
  filteredBots: Array,
  setActiveBot: Function,
  botLink: Function,
  toggleFavorite: Function,
  isFavoriteView: Boolean,
  showSideBar: Boolean,
})

const botIconWidth = computed(() =>
  props.showSideBar
    ? 'col-xxl-3 col-xl-3 col-lg-4 col-md-6 col-12'
    : 'col-xxl-2 col-xl-2 col-lg-3 col-md-4 col-6'
)
</script>

<template>
  <div class="col">
    <div class="row">
      <div v-for="bot in props.filteredBots" :key="bot.uuid" :class="botIconWidth" class="mb-3">
        <RouterLink active-class="active" class="bot_tile" :to="botLink(bot)">
          <div class="card text-center h-100 oslo-bg-light">
            <span v-if="bot.personal" class="visually-hidden">Personlig bot</span>
            <div class="row text-center m-0 pt-3">
              <div class="col-2"></div>
              <div class="col-8 p-0">
                <BotAvatar :avatarScheme="bot.avatarScheme" />
              </div>

              <div v-if="store.isEmployee" class="col-2 px-0">
                <div v-if="bot.mandatory"></div>
                <div v-if="bot.personal"></div>
                <div v-if="!bot.mandatory">
                  <a href="#" @click.prevent="toggleFavorite(bot)">
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
                  <div v-if="!bot.mandatory && !bot.personal && isFavoriteView">
                    <img src="@/components/icons/books.svg" class="category_icon" />
                  </div>
                </div>
              </div>
              <div class="card-body row m-0">
                <div class="col-10 ps-0">{{ bot.botTitle }}</div>
                <a
                  v-if="bot.botInfo"
                  class="col px-0"
                  href="#"
                  data-bs-toggle="modal"
                  data-bs-target="#botinfo"
                  @click.prevent="setActiveBot(bot)"
                >
                  <img src="@/components/icons/information.svg" alt="Informasjon" />
                </a>
              </div>
            </div>
          </div>
        </RouterLink>
      </div>
    </div>
  </div>
</template>
