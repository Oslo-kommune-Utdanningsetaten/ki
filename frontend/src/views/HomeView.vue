<script setup>
import { RouterLink } from 'vue-router';
import axios from 'axios';
import { ref, onMounted, watchEffect } from 'vue'
import { store } from '../store.js';

const bots = ref([]);
const status = ref(null);
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

</script>

<template>
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
    <div v-if="bots.length === 0" >
      <div class="card">
        <div class="card-body">
          <h5 class="card-text">Du har ikke fått tilgang til noen boter</h5>
        </div>
      </div>
    </div>
    <div class="row align-items-stretch">
      <div v-for="bot in bots" :key="bot.bot_nr" class="col-lg-3 col-md-4 col-sm-6 mb-3">
        <div class="card text-center h-100" >
          <RouterLink v-if="bot.bot_nr === 0" active-class="active" class="bot_tile" to="editbot/">
            <div class="card-img-top text-center pt-3">
              <img :src="'/static/img/'+bot.bot_img" alt="Ny bot">
            </div>
            <div class="card-body d-flex flex-column">
              <h5 class="card-title">{{ bot.bot_title }}</h5>
            </div>
          </RouterLink>
          <RouterLink v-else active-class="active" class="bot_tile" :to="'bot/'+bot.bot_nr">
            <div class="card-img-top text-center pt-3">
              <img :src="'/static/img/'+bot.bot_img" :alt="'Åpne '+bot.bot_title">
            </div>
            <div class="card-body d-flex flex-column">
              <h5 class="card-title">{{ bot.bot_title }}</h5>
            </div>
          </RouterLink>
        </div>
      </div>
    </div>
  </div>
  
</template>
