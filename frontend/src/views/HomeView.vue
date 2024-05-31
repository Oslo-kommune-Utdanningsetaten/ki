<script setup>
import { RouterLink } from 'vue-router';
import axios from 'axios';
import { ref, onMounted, watchEffect, computed } from 'vue'
import { store } from '../store.js';
import botIcon1 from '@/components/icons/bot1.svg';
import botIcon2 from '@/components/icons/bot2.svg';
import botIcon3 from '@/components/icons/bot3.svg';
import botIcon4 from '@/components/icons/bot4.svg';
import botIcon5 from '@/components/icons/bot5.svg';


const bots = ref([]);
const status = ref(null);
const showAll = ref(false);
const active_bot = ref(null);
// const route = useRoute()

watchEffect(() => {
  getBots()
});


async function getBots() {
  
  try {
    const { data } = await axios.get('/api/user_bots');
    bots.value = data.bots;
    status.value = data.status;
  } catch (error) {
    console.log(error);
  }
}

const filterFavorites = computed(() => {
  if (!store.isEmployee && !store.isAdmin) {
    return bots.value;
  };
  if (showAll.value) {
    return bots.value.filter(bot => !bot.personal && !bot.mandatory);
  } else {
    return bots.value.filter(bot => bot.mandatory || bot.personal || bot.favorite);
  };
});

const bot_tile_bg = (bot) => {
  if (bot.personal) {
    return 'oslo-bg-light';
  } else {
    return 'oslo-bg-light';
  }
}

const toggle_favorite = async (bot) => {
  try {
    const { data } = await axios.put('/api/favorite/' + bot.uuid);
    bot.favorite = data.favorite;
  } catch (error) {
    console.log(error);
  }
}

const setActiveBot = (bot) => {
  active_bot.value = bot;
};

const getBotImage = (bot) => {
  if (bot.bot_img === 'bot1.svg') {
    return botIcon1;
  } else if (bot.bot_img === 'bot2.svg') {
    return botIcon2;
  } else if (bot.bot_img === 'bot3.svg') {
    return botIcon3;
  } else if (bot.bot_img === 'bot4.svg') {
    return botIcon4;
  } else if (bot.bot_img === 'bot5.svg') {
    return botIcon5;
  } else {
    return bot.bot_img;
  }
}

</script>

<template>

  <!-- Modal -->
  <div class="modal fade" id="botinfo" tabindex="-1" aria-labelledby="bot_info_label" aria-hidden="true">
    <div class="modal-dialog">
      <div v-if="active_bot" class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5" id="bot_info_label">{{ active_bot.bot_title }}</h1>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <span v-html="active_bot.bot_info"></span>
        </div>
        <div class="modal-footer">
          <button type="button" class="btn oslo-btn-secondary" data-bs-dismiss="modal">Lukk</button>
        </div>
      </div>
    </div>
  </div>

  <div v-if="status != 'ok'" class="mb-3">
    <p>KI i Osloskolen er en løsning for å gi lærere og elever i Osloskolens tilgang til å bruke kunstig intelligens på en trygg måte. Løsningen baserer seg på Azure OpenAI.  Azure OpenAI er Microsoft sin utgave av OpenAI sine ulike språkmodeller. Selv om løsningen er lagt bak FEIDE-pålogging, lagrer den ikke persondata. Feide-påloggingen benyttes kun til tilgangs- og kostnadskontroll, slik at elever og lærere i Osloskolen kan bruke denne teknologien på en trygg måte.
      <a href="https://aktuelt.osloskolen.no/larerik-bruk-av-laringsteknologi/informasjonssikkerhet-og-personvern/feide-tjenester/ki/" target="_blank">
        Her kan du lese mer om informasjonssikkerhet og personvern i løsningen.
      </a>
    </p>
    <p>Osloskolens løsning er inspirert av Randabergskolens AI-løsning. Løsningen utvikles av Utdanningsetaten og veilederteamet for bruk av læringsteknologi i Osloskolen.</p>
    <div v-if="status === 'not_feide'">
      <a href="/auth/feidelogin" role="button" class="btn oslo-btn-primary">Logg inn </a>
    </div>
    <div v-else-if="status === 'not_school'">
      <div class="card">
        <div class="card-body">
          <h5 class="card-text">Elever på skolen din har ikke tilgang til denne tjenesten.</h5>
        </div>
      </div>
    </div>
    <div class="mt-3">
      <p>
        <a href="https://uustatus.no/nb/erklaringer/publisert/a049250e-d0fb-4510-8f7c-29427e8876e8" target="_blank">Tilgjengelighetserklæring</a>
      </p>
    </div>
  </div>
  <div v-else class="mb-3">
    <p>Dette er en trygg og sikker måte å bruke kunstig intelligens på. Løsningen bruker ikke eller lagrer personopplysninger. Vi tester løsningen skoleåret 2023/2024. Les mer under "Om tjenesten"</p>
    <div v-if="store.isEmployee || store.isAdmin" class="form-check form-switch mb-2">
      <span>
        <input class="form-check-input" type="checkbox" id="showAll" v-model="showAll">
        <label class="form-check form-check-label" for="showAll">Vis bibliotek</label>
      </span>
    </div>
    <div v-if="bots.length === 0" >
      <div class="card">
        <div class="card-body">
          <h5 class="card-text">Du har ikke fått tilgang til noen boter</h5>
        </div>
      </div>
    </div>
    <div class="row align-items-stretch">
      <div v-for="bot in filterFavorites" :key="bot.uuid" class="col-xxl-2 col-lg-3 col-md-4 col-6 mb-3">
        <RouterLink active-class="active" class="bot_tile" :to="'bot/'+bot.uuid">
          <div class="card text-center h-100" :class="bot_tile_bg(bot)">
            <span v-if="bot.personal" class="visually-hidden">Personlig bot</span>
            <div class="row text-center m-0 pt-3">
              <div class="col-2"></div>
              <div class="col-8 p-0">
                <img :src='getBotImage(bot)' :alt="'Åpne '+bot.bot_title">
              </div>

              <div  v-if="store.isEmployee"  class="col-2 ps-0">
                <div v-if="bot.mandatory"></div>
                <div v-if="bot.personal"></div>
                <div v-if="!bot.mandatory && !bot.personal">
                  <a  href="#" @click.prevent="toggle_favorite(bot)">
                    <img v-if="bot.favorite" src="@/components/icons/star_solid.svg" alt="Fjern som favoritt">
                    <img v-else src="@/components/icons/star.svg" alt="Sett som favoritt">
                  </a>
                </div>
              </div>
              <div class="card-body row m-0">
                <div class="col-10">{{ bot.bot_title }}</div>
                <a v-if="bot.bot_info" class="col-2 pe-0" href="#" data-bs-toggle="modal" data-bs-target="#botinfo" @click.prevent="setActiveBot(bot)">
                  <img src="@/components/icons/information.svg" alt="Informasjon">
                </a>
              </div>
            </div>
          </div>
        </RouterLink>
      </div>
      <RouterLink v-if="store.isEmployee || store.isAdmin" active-class="active"  class="col-xxl-2 col-lg-3 col-md-4 col-6 mb-3" to="editbot/">
        <div  class="card oslo-bg-light text-center h-100" >
          <div class="row text-center pt-3">
            <div class="col-2"></div>
            <div class="col-8">
              <img src="@/components/icons/pluss.svg" alt="Ny bot">
            </div>
          </div>
          <div class="card-body d-flex flex-column">
            <h5 class="card-title">Ny bot</h5>
          </div>
        </div>
      </RouterLink>
    </div>
  </div>
  
</template>
