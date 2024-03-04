<script setup>
import { RouterLink, useRouter, useRoute } from 'vue-router';
import axios from 'axios';
import { ref, onMounted, computed } from 'vue'

const route = useRoute();
const bot = ref({});
const groups = ref();
const lifeSpan = ref(0);
const schoolAccess = ref([]);
const botNr = ref(0);
const sort_by = ref('school_name');
const levels = [
  // { id: '-', name: 'L' },
  // { id: '*', name: 'A' },
  { id: 'aarstrinn1', name: '1.' },
  { id: 'aarstrinn2', name: '2.' },
  { id: 'aarstrinn3', name: '3.' },
  { id: 'aarstrinn4', name: '4.' },
  { id: 'aarstrinn5', name: '5.' },
  { id: 'aarstrinn6', name: '6.' },
  { id: 'aarstrinn7', name: '7.' },
  { id: 'aarstrinn8', name: '8.' },
  { id: 'aarstrinn9', name: '9.' },
  { id: 'aarstrinn10', name: '10.' },
  { id: 'vg1', name: 'Vg1' },
  { id: 'vg2', name: 'Vg2' },
  { id: 'vg3', name: 'Vg3' },
];
const models = [
  { id: "35t", value: "gpt-35-turbo", label: "GPT-3.5 Turbo"},
  { id: "35t-16k", value: "gpt-35-turbo-16k", label: "GPT-3.5 Turbo 16k"},
  { id: "4-32k", value: "gpt-4-32k", label: "GPT-4 32k"}
];
const botImages = [
  { id: 'bot1.svg', text: 'Blå'},
  { id: 'bot2.svg', text: 'Gul'},
  { id: 'bot3.svg', text: 'Grønn'},
  { id: 'bot4.svg', text: 'Rød'},
  { id: 'bot5.svg', text: 'Grå'},
];
botNr.value = route.params.id;

onMounted(() => {
  startpromt()
});


async function startpromt() {
  try {
    const { data } = await axios.get('/api/bot_info/' + botNr.value);
    bot.value = data.bot;
  } catch (error) {
    console.log(error);
  }
  if (bot.value.edit_g) {
    getGroupList()
  } else if (bot.value.edit_s) {  
    getAccessList()
  }
}

async function getGroupList() {
  try {
    const { data } = await axios.get('/api/bot_groups/' + botNr.value);
    groups.value = data.groups;
    lifeSpan.value = data.lifespan;
  } catch (error) {
    console.log(error);
  }
}

async function getAccessList() {
  try {
    const { data } = await axios.get('/api/bot_access/' + botNr.value);
    schoolAccess.value = data.schoolAccess;
  } catch (error) {
    console.log(error);
  }
  schoolAccess.value.forEach(school => {
    if (school.access_list.some(access => levels.some(level => level.id === access))) {
      school.view_levels = true;
    }
  });
}

function update() {
  if (bot.value.bot_nr == 0) {
    axios.post('/api/bot_info/0', bot.value)
      .then(response => {
        bot.value = response.data.bot;
        botNr.value = response.data.bot.bot_nr;
      })
      .catch(error => {
        console.log(error);
      });
  } else {
    axios.put('/api/bot_info/' + botNr.value, bot.value)
    .then(response => {
      // console.log(response);
    })
    .catch(error => {
      console.log(error);
    });
  } 
}


function groupUpdate() {
  if (botNr.value == 0) {
    update();
  }
  axios.put('/api/bot_groups/' + botNr.value, {'groups':groups.value})
    .then(response => {
      // console.log(response);
    })
    .catch(error => {
      console.log(error);
    });
}

function accessUpdate(school) {
  if (botNr.value === 0) {
    update();
  }
  axios.put('/api/bot_access/' + botNr.value, {
        'school_access':school.access_list,
        'org_nr':school.org_nr
      })
    .then(response => {
      // console.log(response);
    })
    .catch(error => {
      console.log(error);
    });
}

function viewToggle(school) {
  if (school.view_levels === false) {
    school.access_list = school.access_list.filter(access => access === '*' || access === '-');
    accessUpdate(school);
  }
}

const schoolAccessSorted = computed(() => {
  return schoolAccess.value.sort((a, b) => {
    // console.log(a[sort_by.value]);
    if (a[sort_by.value] < b[sort_by.value]) {
      return -1;
    }
    if (a[sort_by.value] > b[sort_by.value]) {
      return 1;
    }
    return 0;
  });
});

</script>

<template>

  
  <h1 class="h2">
    {{ bot.title }}
  </h1>
  <div class="d-flex flex-row-reverse">
    <RouterLink active-class="active" class="btn oslo-btn-secondary" :to="'/bot/'+bot.bot_nr">
      Vis bot
    </RouterLink>
  </div>

  <div class="row mb-3">
    <label for="bot_title" class="col-sm-2 col-form-label">Tittel på boten</label>
    <div class="col-sm-10">
      <input v-model="bot.title" @change="update" type="text" class="form-control" id="bot_title" name="title" maxlength="40">
    </div>
  </div>
  <div class="row mb-3">
    <label for="bot_ingress" class="col-sm-2 col-form-label">Ingress</label>
    <div class="col-sm-10">
      <input v-model="bot.ingress" @change="update" type="text" class="form-control" id="bot_ingress" name="ingress">
    </div>
  </div>
  <div class="row mb-3">
    <label for="bot_promt" class="col-sm-2 col-form-label">Ledetekst</label>
    <div class="col-sm-10">
      <textarea v-model="bot.prompt" @change="update" class="form-control" id="bot_promt" rows="5" name="prompt"></textarea>
    </div>
  </div>
  <div class="row mb-3">
    <div class="col-sm-2 col-form-label">Farge på bot</div>
    <div class="col-sm-10">
      <div v-for="image in botImages" class="form-check form-check-inline">
        <input class="form-check-input" type="radio" :id="image.id" :value="image.id" v-model="bot.bot_img" @change="update">
        <label class="form-check-label" :for="image.id">
          {{ image.text }}
        </label>
      </div>
    </div>
  </div>
  <div class="row mb-3">
    <label for="temperature" class="col-sm-2 col-form-label">Temperatur</label>
    <div class="col-sm-1">
      <input type="range" class="form-range" min="0" max="2" step="0.1" id="temperature" v-model="bot.temperature" @change="update">
    </div>
    <div class="col-sm-1">
      {{ bot.temperature }}
    </div>
    <div class="col">
        Temperatur er et mål på hvor kreativ boten skal være. Høy temperatur gir mer kreative svar.
    </div>
  </div>

  <div v-if="bot.edit_g" class="row mb-3">
    <div >
      <p>
        Elevene dine kan få tilgang til denne boten ved at du huker av for klasser eller faggrupper nedenfor. Merk at dette gjelder kun for elever som har fått tilgang til ki.osloskolen.no.<br>
        Tilgangen til boten varer i {{ lifeSpan }} timer fra du lagrer.
      </p>
    </div>
    <div class="col-sm-2">
      Grupper som har tilgang
    </div>
    <div class="col-sm-10">
        <div v-for="group in groups" class="form-check">
          <input class="form-check-input" type="checkbox" name="access" v-model="group.checked" @change="groupUpdate" :id="'check'+group.id">
          <label class="form-check-label" :for="'check'+group.id">
            {{group.display_name}} {{ group.go_type == 'b' ? '(klasse)' : '(faggruppe)' }}
          </label>
        </div>
    </div>
  </div>

  <div v-if="bot.edit_s" class="mb-3">
    <div class="row mb-3">
      <div class="col-sm-2 ">Modell</div>
      <div class="col-sm-10">
        <div v-for="model in models" :key="model.id" class="form-check form-check-inline">
          <input class="form-check-input" type="radio" :id="model.id" :value="model.value" v-model="bot.model" @change="update">
          <label class="form-check-label" :for="model.id">{{ model.label }}</label>
        </div>
      </div>
    </div>

    <div v-for="school in schoolAccessSorted" >
      <div class="row">
        <div class="col-3">
          {{ school.school_name}}
        </div>
        <div class="col">
          <div class="form-check form-check-inline">
            <input class="form-check-input" type="checkbox" :id="'check'+school.org_nr+'-'" value="-" v-model="school.access_list" @change="accessUpdate(school)">
            <label class="form-check-label" :for="'check'+school.org_nr+'-'">
              Lærere
            </label>
          </div>
          <div class="form-check form-check-inline">
            <input class="form-check-input" type="checkbox" :id="'check'+school.org_nr+'*'" value="*" v-model="school.access_list" @change="accessUpdate(school)">
            <label class="form-check-label" :for="'check'+school.org_nr+'*'">
              Alle
            </label>
          </div>
          <div class="form-check form-check-inline">
            <input class="form-check-input" type="checkbox" :id="'check'+school.org_nr+'v'" v-model="school.view_levels" @change="viewToggle(school)">
            <label class="form-check-label" :for="'check'+school.org_nr+'v'">
              Enkelte trinn
            </label>
          </div>
        </div>
      </div>
      <div v-if="school.view_levels" class="row">
        <div class="col-4">
        </div>
        <div class="col">
          <span v-for="level in levels" class="form-check form-check-inline">
            <input class="form-check-input" type="checkbox" :id="'check'+school.org_nr+level.id" :value="level.id" v-model="school.access_list" @change="accessUpdate(school)">
            <label class="form-check-label" :for="'check'+school.org_nr+level.id">
              {{level.name}}
            </label>
          </span>
        </div>
      </div>


    </div>
  </div>

</template>
