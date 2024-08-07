<script setup>
import { RouterLink, useRouter, useRoute } from 'vue-router';
import axios from 'axios';
import { ref, onMounted, computed, watchEffect, watch } from 'vue'
import { store } from '../store.js';
import router from '@/router/index.js';

const route = useRoute();
const $router = useRouter();
const bot = ref({
  title: '',
  ingress: '',
  prompt: '',
  prompt_visibility: false,
  bot_img: 'bot1.svg',
  temperature: 1,
  model: 'gpt-35-turbo',
  mandatory: false,
  allow_distribution: false,
  bot_info: '',
  tags: {},
  tag_categories: [],
  choices: [],
  schoolAccesses: [],
  groups: [],
  library: false
});
const edit = ref(false);
const distribute = ref(false);
const newBot = ref(false);
const method = ref('edit');
const lifeSpan = ref(0);
const botId = ref();
const sort_by = ref('school_name');
const filter_list = ref([]);
const access_options = [
    { value: 'none', label: 'Ingen' },
    { value: 'emp', label: 'Ansatte' },
    { value: 'all', label: 'Alle' },
    { value: 'levels', label: 'Trinn' },
];
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
  var url = '';
  if (method.value == 'new') {
    url = '/api/empty_bot/personal';
  } else if (method.value == 'newlib') {
    url = '/api/empty_bot/library';
  } else {
    url = '/api/bot_info/' + botId.value;
  }
  try {
    const { data } = await axios.get(url);
    bot.value = data.bot;
    lifeSpan.value = data.lifespan;
  } catch (error) {
    console.log(error);
  }  
  }

const update = async () => {
  if (newBot.value) {
    try {
      const { data } = await axios.post('/api/bot_info/', bot.value)
      botId.value = data.bot.uuid;
      store.addMessage('Boten er opprettet!', 'info' );
    } catch (error) {
      console.log(error);
    }
  } else if (method.value == 'edit') {
    try {
      await axios.put('/api/bot_info/' + botId.value, bot.value)
      store.addMessage('Endringene er lagret!', 'info' );
    } catch (error) {
      console.log(error);
    }
  } else if (method.value == 'distribute') {
    try {
      await axios.patch('/api/bot_info/' + botId.value, { groups: bot.value.groups })
      store.addMessage('Endringene er lagret!', 'info' );
    } catch (error) {
      console.log(error);
    }
  }

  $router.push('/bot/' + botId.value);
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
    selected: false,
    order: Math.max(...bot.value.choices.map(c => c.order), -1) + 1
  });
}

const notFirstChoice = (choice) => {
  return choice.order > 0;
}

const notLastChoice = (choice) => {
  return choice.order < bot.value.choices.length - 1;
}

const notFirstOption = (_, option) => {
  return option.order > 0;
}

const notLastOption = (choice, option) => {
  return option.order < choice.options.length - 1;
}

const choiceOrderUp = (choice) => {
  if (choice.order > 0) {
    const other = bot.value.choices.find(c => c.order === choice.order - 1);
    other.order++;
    choice.order--;
  }
}

const choiceOrderDown = (choice) => {
  if (choice.order < bot.value.choices.length - 1) {
    const other = bot.value.choices.find(c => c.order === choice.order + 1);
    other.order--;
    choice.order++;
  }
}

const optionOrderUp = (choice, option) => {
  if (option.order > 0) {
    const other = choice.options.find(o => o.order === option.order - 1);
    other.order++;
    option.order--;
  }
}

const optionOrderDown = (choice, option) => {
  if (option.order < choice.options.length - 1) {
    const other = choice.options.find(o => o.order === option.order + 1);
    other.order--;
    option.order++;
  }
}

const deleteOption = (choice, option) => {
  choice.options = choice.options.filter(o => o.id !== option.id);
}

const addOption = (choice) => {
  choice.options.push({
    id: Math.random().toString(36).substring(7),
    label: '',
    text: '',
    order: Math.max(...choice.options.map(o => o.order), -1) + 1
  });
}

const setAllAccesses = (access) => {
  bot.value.schoolAccesses.forEach(school => {
    school.access = access;
  });
}

const choicesSorted = computed(() => {
  if (!bot.value.choices) {
    return [];
  }
  return bot.value.choices.sort((a, b) => a.order - b.order);
});

const optionsSorted = (choice) => {
  return choice.options.sort((a, b) => a.order - b.order);
}

const superuser = computed(() => {
  return (store.isAdmin || store.isAuthor) && bot.value.library;
});

const schoolAccessFiltered = computed(() => {
  let filtered_list = [];
  if (filter_list.value.length > 0) {
    filtered_list = bot.value.schoolAccesses.filter((school) => (filter_list.value.includes(school.access)));
  } else {
    filtered_list = bot.value.schoolAccesses || [];
  }

  return filtered_list.sort((a, b) => {
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
  if (method.value == 'new' || method.value == 'newlib') {
    newBot.value = true;
  } else {
    botId.value = route.params.id;
  }
  if (method.value == 'distribute') {
    distribute.value = true;
    edit.value = false;
  } else {
    edit.value = true;
    if (bot.value.library) {
      distribute.value = false;
    } else {
      distribute.value = true;
    }
  }
});

watch(route, () => {
  const legalMethods = ['edit', 'distribute', 'new', 'newlib'];
  if (legalMethods.includes(route.params.method)) {
    method.value = route.params.method;
  } else {
    router.push('/');
  }
  getBotInfo() 
}, { immediate: true });

</script>

<template>

  <div class="d-flex justify-content-end">
    <button @click="update" class="btn oslo-btn-primary">
      Lagre
    </button>
    <RouterLink class="btn oslo-btn-secondary" :to="bot.uuid ? '/bot/'+bot.uuid : '/'">
      Avbryt
    </RouterLink>
  </div>
  <h1 class="h2 mb-4">
    {{ bot.title }}
  </h1>
  <div v-if="edit">
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
    
    <div v-if="store.isAdmin" class="mb-3">
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
        <div class="col-sm-2 ">Tvungen visning</div>
        <div class="col-sm-10">
          <div class="form-check form-check-inline">
            <input class="form-check-input" type="checkbox" id="mandatory" v-model="bot.mandatory">
            <label class="form-check-label" for="mandatory">Ja</label>
          </div>
        </div>
      </div>
    </div>
    <div v-if="superuser">
      <div class="row mb-3">
        <div class="col-sm-2 ">Tillat distribusjon til elever</div>
        <div class="col-sm-10">
          <div class="form-check form-check-inline">
            <input class="form-check-input" type="checkbox" id="allow_distribution" v-model="bot.allow_distribution">
            <label class="form-check-label" for="allow_distribution">Ja</label>
          </div>
        </div>
      </div>
      <div class="row mb-3">
        <label for="bot_info" class="col-sm-2 col-form-label">Informasjon (vises på startsiden)</label>
        <div class="col-sm-10">
          <textarea v-model="bot.bot_info" class="form-control" id="bot_info" rows="5" name="bot_info"></textarea>
        </div>
      </div>
      <div class="row mb-3">
      <div class="col-sm-2 ">Filtertag for</div>
      <div class="col-sm-10">
        <div v-for="(tagCategory, catName, catIndex) in bot.tag_categories" :key="catIndex">
          <div> {{catName}} </div>
          <div v-for="(tagName, tagIndex) in tagCategory" :key="tagIndex" class="form-check form-check-inline">
            <input
              class="form-check-input"
              type="checkbox"
              v-model="bot.tags[catIndex]"
              :value="tagIndex"
              :id="`filterCheck${catIndex}:${tagIndex}`"
            />
            <label class="form-check-label" :for="`filterCheck${catIndex}:${tagIndex}`">
              {{ tagName }}
            </label>
          </div>
        </div>
      </div>
    </div>
      <div class="row mb-3">
        <div class="col-sm-2 ">Forhåndsvalg</div>
        <div class="col-sm-10">
          <div v-for="choice in choicesSorted" class="card mb-3 p-3" >
            <div class="row mb-1">
              <label :for="`choice_label${choice.id}`" class="col-sm-2 col-form-label">Spørsmål</label>
                <div class="col-sm-10">
                  <input type="text" class="form-control" :id="`choice_label${choice.id}`" v-model="choice.label">
                </div>
            </div>
            <div class="row mb-1">
              <div class="col-sm-2 ">Alternativer</div>
              <div class="col-sm-10">
                <div v-for="option in optionsSorted(choice)">
                  <div class="row mb-1">
                    <label :for="`opt_label${option.id}`" class="col-sm-2 col-form-label">Knapp</label>
                    <div class="col-sm-10">
                      <input type="text" class="form-control" :id="`opt_label${option.id}`" v-model="option.label">
                    </div>
                  </div>
                  <div class="row mb-1">
                    <label :for="`opt_text${option.id}`" class="col-sm-2 col-form-label">Ledetekst</label>
                    <div class="col-sm-10">
                      <textarea class="form-control" :id="`opt_text${option.id}`" rows="1" v-model="option.text"></textarea>
                    </div>
                  </div>
                  <input class="btn-check" type="radio" :id="`${choice.id}-${option.id}`" :value="option" v-model="choice.selected">
                  <label class="btn oslo-btn-secondary" :for="`${choice.id}-${option.id}`">Valgt</label>
                  <button class="btn oslo-btn-warning" @click="deleteOption(choice, option)">Slett alternativ</button>
                  <button v-if="notFirstOption(choice, option)" class="btn oslo-btn-secondary" @click="optionOrderUp(choice, option)">
                    <img src="@/components/icons/move_up.svg" alt="flytt opp">
                  </button>
                  <button v-if="notLastOption(choice, option)" class="btn oslo-btn-secondary" @click="optionOrderDown(choice, option)">
                    <img src="@/components/icons/move_down.svg" alt="flytt ned">
                  </button>
                  <!-- {{ option.order }} -->
                  <hr>
                </div>
                <button class="btn oslo-btn-primary" @click="addOption(choice)">Legg til alternativ</button>
              </div>
            </div>
            <div class="mb-1">
              <button class="btn oslo-btn-warning" @click="deleteChoice(choice)">Slett spørsmål</button>
              <button v-if="notFirstChoice(choice)" class="btn oslo-btn-secondary" @click="choiceOrderUp(choice)">
                <img src="@/components/icons/move_up.svg" alt="flytt opp">
              </button>
              <button v-if="notLastChoice(choice)" class="btn oslo-btn-secondary" @click="choiceOrderDown(choice)">
                <img src="@/components/icons/move_down.svg" alt="flytt ned">
              </button>
              <!-- {{ choice.order }} -->
            </div>
          </div>
          <div class="mb-1">
            <button class="btn oslo-btn-primary" @click="addChoice">Legg til spørsmål</button>
          </div>
        </div>
      </div>
    </div>
</div>
<div v-else>
  <div class="row mb-3">
    <div class="col-sm-2 col-form-label">Ingress</div>
    <div class="col-sm-10">
      {{ bot.ingress }}
    </div>
  </div>
  <div class="row mb-3">
    <div class="col-sm-2 col-form-label">Ledetekst</div>
    <div class="col-sm-10">
      {{ bot.prompt }}
    </div>
  </div>
</div>

  <div v-if="distribute && bot.groups" class="row mb-3">
    <div >
      <hr/>
      <p>
        Elevene dine kan få tilgang til denne boten ved at du huker av for klasser eller faggrupper nedenfor. Merk at dette gjelder kun for elever som har fått tilgang til ki.osloskolen.no.<br>
        Tilgangen til boten varer i {{ lifeSpan }} timer fra du lagrer.
      </p>
    </div>
    <div class="col-sm-2">
      Grupper som har tilgang
    </div>
    <div class="col-sm-10">
      <div v-for="group in bot.groups" class="form-check">
        <input class="form-check-input" type="checkbox" name="access" v-model="group.checked" :id="'check'+group.id">
        <label class="form-check-label" :for="'check'+group.id">
          {{group.display_name}} {{ group.go_type == 'b' ? '(klasse)' : '(faggruppe)' }}
        </label>
      </div>
    </div>
  </div>

  <div class="d-flex flex-row-reverse mb-3">
    <RouterLink active-class="active" class="btn oslo-btn-secondary" :to="bot.uuid ? '/bot/'+bot.uuid : '/'">
      Avbryt
    </RouterLink>
    <button @click="update" class="btn oslo-btn-primary">
      Lagre
    </button>
  </div>

  <div v-if="(store.isAdmin || store.isAuthor) && bot.library  && edit" class="mb-3">
    <hr/>
    <div class="row mb-3">
      <div class="col-sm-2 ">Tilgang</div>
      <div class="card col mb-3 p-3" >

        <ul class="list-group list-group-flush">
            <li v-if="store.isAdmin" class="list-group-item">
              <div class="row">
                <div class="col-4">
                  Sett alle skoler til:
                </div>
                <div v-for="option in access_options" :key="option.value" class="e col-1">
                  <button class="btn oslo-btn-secondary" @click="setAllAccesses(option.value)">
                    {{ option.label }}
                  </button>
                </div>
              </div>
              <div class="row">
                  <div class="col-4">
                      Filtrer på tilgang:
                  </div>
                  <div v-for="option in access_options" :key="option.value" class="form-check form-check-inline col-1">
                      <input
                          class="form-check-input"
                          :id="'filter' + option.value"
                          :value="option.value"
                          type="checkbox"
                          v-model="filter_list"
                      />
                      <label class="form-check-label" :for="'filter' + option.value">{{ option.label }}</label>
                  </div>
              </div>
            </li>
            <li v-for="school in schoolAccessFiltered" class="list-group-item">
                <div class="row">
                    <div class="col-4">
                        {{ school.school_name }}
                    </div>
                    <div v-for="option in access_options" :key="option.value" class="form-check form-check-inline col-1">
                        <input
                            class="form-check-input"
                            :id="school.org_nr + option.value"
                            :value="option.value"
                            type="radio"
                            v-model="school.access"
                        />
                        <label class="form-check-label" :for="option.value">{{ option.label }}</label>
                    </div>
                </div>
                <div v-if="school.access == 'levels'" class="row">
                    <div class="col-2">
                        Trinn:
                    </div>
                    <div class="col">
                        <span v-for="level in levels" class="form-check form-check-inline">
                            <input 
                                class="form-check-input" 
                                type="checkbox" 
                                :id="'level'+school.org_nr+level.id" 
                                :value="level.id" 
                                v-model="school.access_list" 
                            />
                            <label class="form-check-label" :for="'level'+school.org_nr+level.id">
                                {{level.name}}
                            </label>
                        </span>
                    </div>
                </div>

            </li>
        </ul>
      </div>
    </div>

    <div class="d-flex flex-row-reverse mb-3">
      <RouterLink active-class="active" class="btn oslo-btn-secondary" :to="bot.uuid ? '/bot/'+bot.uuid : '/'">
        Avbryt
      </RouterLink>
      <button @click="update" class="btn oslo-btn-primary">
        Lagre
      </button>
    </div>
  </div>


</template>
