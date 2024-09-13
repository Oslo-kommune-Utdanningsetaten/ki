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
const showLibrary = ref(false);
const active_bot = ref(null);
const filter = ref([]);
const tagCategories = ref([]);
// const route = useRoute()


watchEffect(() => {
  getBots()
});


async function getBots() {
  
  try {
    const { data } = await axios.get('/api/user_bots');
    bots.value = data.bots;
    status.value = data.status;
    tagCategories.value = data.tag_categories;
    filter.value = new Array(Object.keys(tagCategories.value).length).fill([]);
  } catch (error) {
    console.log(error);
  }
}

const filterBots = computed(() => {
  bots.value.sort((a, b) => b.mandatory - a.mandatory || a.bot_title.localeCompare(b.bot_title));
  if (!store.isEmployee && !store.isAdmin) {
    return bots.value; // Show all bots for students
  };
  if (showLibrary.value) {
    let botsFiltered = bots.value;
    filter.value.forEach((filterArray, i) => {
      if (filterArray.length > 0) {
        const binarySum = filterArray.reduce((partialSum, a) => partialSum + Math.pow(2, a), 0);
        botsFiltered = botsFiltered.filter((bot) => ((bot.tag[i]) & binarySum) > 0);
      }
    });
    return botsFiltered.filter(bot => !bot.personal && !bot.mandatory);
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

const botIconWidth = computed(() => (
    "col-xxl-2 col-xl-2 col-lg-3 col-md-4 col-6"
    // showLibrary.value ?
    //   "col-xxl-3 col-xl-3 col-lg-4 col-md-6 col-12" :
    //   "col-xxl-2 col-xl-2 col-lg-3 col-md-4 col-6"
  ))

const newLink = computed(() => (
  showLibrary.value ? 'editbot/newlib' : 'editbot/new'
))

const botLink = (bot) => (
  bot.img_bot ? 'imgbot/' + bot.uuid : 'bot/' + bot.uuid
)

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
    <p>Dette er en trygg og sikker måte å bruke kunstig intelligens på. Løsningen bruker ikke eller lagrer personopplysninger. Vi tester løsningen skoleårene 2023/2024 og 2024/2025. Les mer under "Om tjenesten"</p>
    <div v-if="bots.length === 0" >
      <div class="card">
        <div class="card-body">
          <h5 class="card-text">Du har ikke fått tilgang til noen boter</h5>
        </div>
      </div>
    </div>

    <!-- bibliotek -->
    <div v-if="store.isEmployee || store.isAdmin">
      <div class="form-check form-switch mb-2">
        <input class="form-check-input" type="checkbox" id="showAll" v-model="showLibrary">
        <label class="form-check form-check-label" for="showAll">Vis bibliotek</label>
      </div>
    </div>

    <div class="row align-items-stretch">
      <!-- TODO de-comment this to activate the filter -->
      <!-- <div v-if="showLibrary" class="col-xxl-3 col-lg-3 col-md-4 col-6">
        <div class="card card-body">
          <div class="card-title">
            Filtrer:
          </div>
          <div v-for="(tagCategory, catName, catIndex) in tagCategories" :key="catIndex">
            <div>{{ catName }}</div>
            <div v-for="(tagName, tagIndex) in tagCategory" :key="tagIndex" class="form-check form-check-inline">
              <input
                class="form-check-input"
                type="checkbox"
                v-model="filter[catIndex]"
                :value="tagIndex"
                :id="`filterCheck${catIndex}:${tagIndex}`"
              />
              <label class="form-check-label" :for="`filterCheck${catIndex}:${tagIndex}`">
                {{ tagName }}
              </label>
            </div>
          </div>
        </div>
      </div> -->
      <div class="col">
      <div class="row">
      <div v-for="bot in filterBots" :key="bot.uuid" :class="botIconWidth" class="mb-3">
        <RouterLink active-class="active" class="bot_tile" :to="botLink(bot)" >
          <div class="card text-center h-100" :class="bot_tile_bg(bot)">
            <span v-if="bot.personal" class="visually-hidden">Personlig bot</span>
            <div class="row text-center m-0 pt-3">
              <div class="col-2"></div>
              <div class="col-8 p-0">
                <img :src='getBotImage(bot)' :alt="'Åpne '+bot.bot_title">
              </div>

              <div  v-if="store.isEmployee"  class="col-2 px-0">
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
                <div class="col-10 ps-0">{{ bot.bot_title }}</div>
                <a v-if="bot.bot_info" class="col px-0" href="#" data-bs-toggle="modal" data-bs-target="#botinfo" @click.prevent="setActiveBot(bot)">
                  <img src="@/components/icons/information.svg" alt="Informasjon">
                </a>
              </div>
            </div>
          </div>
        </RouterLink>
      </div>
      <RouterLink v-if="(store.isAuthor || store.isAdmin || (store.isEmployee && !showLibrary))" active-class="active" :class="botIconWidth" class="mb-3" :to="newLink">
        <div  class="card oslo-bg-light text-center h-100" >
          <div class="row text-center pt-3">
            <div class="col-2"></div>
            <div class="col-8">
              <img src="@/components/icons/pluss.svg" alt="">
            </div>
          </div>
          <div class="card-body d-flex flex-column">
            <h5 v-if="showLibrary" class="card-title">Ny biblioteksbot</h5>
            <h5 v-else class="card-title">Ny bot</h5>
          </div>
        </div>
      </RouterLink>
      </div>
      </div>
    </div>
  </div>
  
</template>
