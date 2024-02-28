<script setup>
import { RouterLink } from 'vue-router';
import axios from 'axios';
import { ref, onMounted, watchEffect } from 'vue'

const bots = ref([]);
// const route = useRoute()

watchEffect(() => {
  getBots()
});

async function getBots() {
  
  try {
    const { data } = await axios.get('/api/user_bots');
    bots.value = data.bots;
  } catch (error) {
    console.log(error);
  }
}

</script>

<template>
  <div v-if="bots.length === 0" class="mb-3">
    <p>KI i Osloskolen er en løsning for å gi lærere og elever i Osloskolens tilgang til å bruke kunstig intelligens på en trygg måte. Løsningen baserer seg på Azure OpenAI.  Azure OpenAI er Microsoft sin utgave av OpenAI sine ulike språkmodeller. Selv om løsningen er lagt bak FEIDE-pålogging, lagrer den ikke persondata. Feide-påloggingen benyttes kun til tilgangs- og kostnadskontroll, slik at elever og lærere i Osloskolen kan bruke denne teknologien på en trygg måte.
        <a href="https://aktuelt.osloskolen.no/larerik-bruk-av-laringsteknologi/informasjonssikkerhet-og-personvern/feide-tjenester/ki/" target="_blank">
          Her kan du lese mer om informasjonssikkerhet og personvern i løsningen.
        </a>
      </p>
      <p>Osloskolens løsning er inspirert av Randabergskolens AI-løsning. Løsningen utvikles av Utdanningsetaten og veilederteamet for bruk av læringsteknologi i Osloskolen.</p>
  </div>
  <div v-else class="mb-3">
    <p>Dette er en trygg og sikker måte å bruke kunstig intelligens på. Løsningen bruker ikke eller lagrer personopplysninger. Vi tester løsningen skoleåret 2023/2024. Les mer under "Om tjenesten"</p>
  </div>
  <div class="row align-items-stretch">
    <div v-for="bot in bots" :key="bot.bot_nr" class="col-lg-3 col-md-4 col-sm-6 mb-3">
      <div class="card text-center h-100" >
        <div class="card-img-top text-center">
          <RouterLink v-if="bot.bot_nr === 0" active-class="active" class="" to="editbot/0">
            <img :src="'/static/img/'+bot.bot_img" alt="Ny bot">
          </RouterLink>
          <RouterLink v-else active-class="active" class="" :to="'bot/'+bot.bot_nr">
            <img :src="'/static/img/'+bot.bot_img" :alt="'Åpne '+bot.bot_title">
          </RouterLink>
        </div>
        <div class="card-body d-flex flex-column">
          <h5 class="card-title">{{ bot.bot_title }}</h5>
        </div>
      </div>
    </div>
  </div>
</template>
