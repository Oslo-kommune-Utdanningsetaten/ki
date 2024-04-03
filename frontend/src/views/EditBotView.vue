<script setup>
import { RouterLink, useRouter, useRoute } from 'vue-router';
import axios from 'axios';
import { ref, onMounted, computed, watchEffect } from 'vue'
import { store } from '../store.js';

const route = useRoute();
const $router = useRouter();
const bot = ref({
  title: '',
  ingress: '',
  prompt: '',
  prompt_visibility: true,
  bot_img: 'bot1.svg',
  temperature: '1',
  model: 'gpt-35-turbo',
  bot_nr: null});
const newBot = ref(false);
const edit_g = ref(false);
const edit_s = ref(false);
const groups = ref();
const lifeSpan = ref(0);
const schoolAccess = ref([]);
const botNr = ref();
const sort_by = ref('school_name');
const levels = [
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

const getBotInfo = async () => {
  try {
    const { data } = await axios.get('/api/bot_info/' + botNr.value);
    bot.value = data.bot;
  } catch (error) {
    console.log(error);
  }
  }
  if (edit_g.value) {
    getGroupList()
  } else if (edit_s.value) {  
    getAccessList()
  }

const getGroupList = async () => {
  var url = '/api/bot_groups/';
  if (!newBot.value) {
    url += botNr.value;
  }
  try {
    const { data } = await axios.get(url);
    groups.value = data.groups;
    lifeSpan.value = data.lifespan;
    edit_g.value = data.edit_g;
    edit_s.value = data.edit_s;
  } catch (error) {
    console.log(error);
  }
}

const getAccessList = async () => {
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

const update = async () => {
  if (newBot.value) {
    try {
      const response = await axios.post('/api/bot_info/', bot.value)
      bot.value = response.data.bot;
      botNr.value = response.data.bot.bot_nr;
      newBot.value = false;
      if (edit_g.value) {
        groupUpdate()
      }
      store.addMessage('Boten er opprettet!', 'info' );
    } catch (error) {
      console.log(error);
    }
  } else {
    try {
      const response = await axios.put('/api/bot_info/' + botNr.value, bot.value)
      if (edit_g.value) {
        groupUpdate()
      }
      store.addMessage('Endringene er lagret!', 'info' );
    } catch (error) {
      console.log(error);
    }
  }
  $router.push('/bot/' + botNr.value);
}

const groupUpdate = async () => {
  try {
    const response = await axios.put('/api/bot_groups/' + botNr.value, {'groups':groups.value})
  } catch (error) {
    console.log(error);
  }
}

const accessUpdate = async (school) => {
  if (newBot.value) {
    update();
  }
  try {
    const response = await axios.put('/api/bot_access/' + botNr.value, {
      'school_access':school.access_list,
      'org_nr':school.org_nr
    })
  } catch (error) {
    console.log(error);
  }
}

const viewToggle = (school) => {
  if (school.view_levels === false) {
    school.access_list = school.access_list.filter(access => access === '*' || access === '-');
    accessUpdate(school);
  }
}

const deleteChoice = (choice) => {
  bot.value.choices = bot.value.choices.filter(c => c.id !== choice.id);
}

const addChoice = () => {
  bot.value.choices.push({
    id: Math.random().toString(36).substring(7),
    label: '',
    text: '',
    options: [],
    selected: false
  });
}

const deleteOption = (choice, option) => {
  choice.options = choice.options.filter(o => o.id !== option.id);
}

const addOption = (choice) => {
  choice.options.push({
    id: Math.random().toString(36).substring(7),
    label: '',
    text: ''
  });
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

watchEffect(() => {
  if (route.params.id == null) {
    newBot.value = true;
  } else {
    botNr.value = route.params.id;
  }
  if (!newBot.value) {
    getBotInfo()
  }
  getGroupList()
});



</script>

<template>

  <div class="d-flex justify-content-end">
    <button @click="update" class="btn oslo-btn-primary me-2">
      Lagre
    </button>
    <RouterLink class="btn oslo-btn-secondary" :to="bot.bot_nr ? '/bot/'+bot.bot_nr : '/'">
      Avbryt
    </RouterLink>
  </div>
  <h1 class="h2 mb-4">
    {{ bot.title }}
  </h1>
  <div class="row mb-3">
    <label for="bot_title" class="col-sm-2 col-form-label">Tittel på boten</label>
    <div class="col-sm-10">
      <input v-model="bot.title" type="text" class="form-control" id="bot_title" name="title" maxlength="40">
    </div>
  </div>
  <div class="row mb-3">
    <label for="bot_ingress" class="col-sm-2 col-form-label">Ingress</label>
    <div class="col-sm-10">
      <input v-model="bot.ingress" type="text" class="form-control" id="bot_ingress" name="ingress">
    </div>
  </div>
  <div class="row mb-3">
    <label for="bot_promt" class="col-sm-2 col-form-label">Ledetekst</label>
    <div class="col-sm-10">
      <textarea v-model="bot.prompt" class="form-control" id="bot_promt" rows="5" name="prompt"></textarea>
    </div>
  </div>
  <div class="row mb-3">
    <label for="prompt_visibility" class="col-sm-2 col-form-label">Ledetekst synlig</label>
    <div class="col-sm-10">
      <div class="form-check form-check-inline">
        <input class="form-check-input" type="checkbox" id="prompt_visibility" v-model="bot.prompt_visibility">
      </div>
    </div>
  </div>
  <div class="row mb-3">
    <div class="col-sm-2 col-form-label">Farge på bot</div>
    <div class="col-sm-10">
      <div v-for="image in botImages" class="form-check form-check-inline">
        <input class="form-check-input" type="radio" :id="image.id" :value="image.id" v-model="bot.bot_img">
        <label class="form-check-label" :for="image.id">
          {{ image.text }}
        </label>
      </div>
    </div>
  </div>
  <div class="row mb-3">
    <label for="temperature" class="col-sm-2 col-form-label">Temperatur</label>
    <div class="col-sm-1">
      <input type="range" class="form-range" min="0.5" max="1.5" step="0.1" id="temperature" v-model="bot.temperature">
    </div>
    <div class="col-sm-1">
      {{ bot.temperature * 10 - 5 }}
    </div>
    <div class="col">
        Temperatur er et mål på hvor kreativ boten skal være. Høy temperatur gir mer kreative svar.
    </div>
  </div>

  <div v-if="edit_g" class="row mb-3">
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
          <input class="form-check-input" type="checkbox" name="access" v-model="group.checked" :id="'check'+group.id">
          <label class="form-check-label" :for="'check'+group.id">
            {{group.display_name}} {{ group.go_type == 'b' ? '(klasse)' : '(faggruppe)' }}
          </label>
        </div>
    </div>
  </div>

  <div v-if="edit_s" class="mb-3">
    <div class="row mb-3">
      <div class="col-sm-2 ">Modell</div>
      <div class="col-sm-10">
        <div v-for="model in models" :key="model.id" class="form-check form-check-inline">
          <input class="form-check-input" type="radio" :id="model.id" :value="model.value" v-model="bot.model">
          <label class="form-check-label" :for="model.id">{{ model.label }}</label>
        </div>
      </div>
    </div>
    <div class="row mb-3">
      <div class="col-sm-2 ">Forhåndsvalg</div>
      <div class="col-sm-10">
        <div v-for="choice in bot.choices" class="card mb-3 p-3" >
          <div class="row mb-1">
            <label :for="`choice_label${choice.id}`" class="col-sm-2 col-form-label">Etikett</label>
              <div class="col-sm-10">
                <input type="text" class="form-control" :id="`choice_label${choice.id}`" v-model="choice.label">
              </div>
          </div>
          <div class="row mb-1">
            <label :for="`choice_text${choice.id}`" class="col-sm-2 col-form-label">Tekst</label>
            <div class="col-sm-10">
              <textarea class="form-control" :id="`choice_text${choice.id}`" rows="1"  v-model="choice.text" ></textarea>
            </div>
          </div>
          <div class="row mb-1">
            <div class="col-sm-2 ">Alternativer</div>
            <div class="col-sm-10">
              <div v-for="option in choice.options">
                <div class="row mb-1">
                  <label :for="`opt_label${option.id}`" class="col-sm-2 col-form-label">Etikett</label>
                  <div class="col-sm-10">
                    <input type="text" class="form-control" :id="`opt_label${option.id}`" v-model="option.label">
                  </div>
                </div>
                <div class="row mb-1">
                  <label :for="`opt_text${option.id}`" class="col-sm-2 col-form-label">Tekst</label>
                  <div class="col-sm-10">
                    <textarea class="form-control" :id="`opt_text${option.id}`" rows="1" v-model="option.text"></textarea>
                  </div>
                </div>
                <input class="btn-check" type="radio" :id="`${choice.id}-${option.id}`" :value="option" v-model="choice.selected">
                <label class="btn oslo-btn-secondary" :for="`${choice.id}-${option.id}`">Standard</label>
                <button class="btn oslo-btn-warning" @click="deleteOption(choice, option)">Slett alternativ</button>
                <hr>
              </div>
              <button class="btn oslo-btn-primary" @click="addOption(choice)">Legg til alternativ</button>
            </div>
          </div>
          <div class="mb-1">
            <button class="btn oslo-btn-warning" @click="deleteChoice(choice)">Slett valg</button>
          </div>
        </div>
        <div class="mb-1">
          <button class="btn oslo-btn-primary" @click="addChoice">Legg til valg</button>
        </div>

      </div>
    </div>
  </div>

  <div class="d-flex flex-row-reverse mb-3">
    <RouterLink active-class="active" class="btn oslo-btn-secondary me-2" :to="bot.bot_nr ? '/bot/'+bot.bot_nr : '/'">
      Avbryt
    </RouterLink>
    <button @click="update" class="btn oslo-btn-primary me-2">
      Lagre
    </button>
  </div>

  <div v-if="bot.edit_s" class="mb-3">
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
            <input class="form-check-input" type="checkbox" :id="'check'+school.org_nr+level.id" :value="level.id" v-model="school.access_list">
            <label class="form-check-label" :for="'check'+school.org_nr+level.id">
              {{level.name}}
            </label>
          </span>
        </div>
      </div>
    </div>
  </div>


</template>
