<script setup>
import { RouterLink, useRouter, useRoute } from 'vue-router';
import axios from 'axios';
import { ref, onMounted, watchEffect } from 'vue'
import $ from 'jquery'

const route = useRoute()
const router = useRouter()
const bot = ref({});
const botNr = ref(0);
const messages = ref([]);
const message = ref('');
const showTypeWriter = ref(false);
const showSystemPrompt = ref(false);
botNr.value = route.params.id;


const startpromt = async () => {
  try {
    const { data } = await axios.get('/api/bot_info/' + botNr.value);
    bot.value = data.bot;
    messages.value = [{
      "role": "system",
      "content": bot.value.prompt,
    }];

  } catch (error) {
    console.log(error);
  }
}


const sendMessage = async () => {
        messages.value.push(
          {
            "role": "user",
            "content": message.value,
          },
          {
            "role": "assistant",
            "content": "",
          }
        );
        message.value = '';
        $("#input_line").addClass("d-none")
        $(".edit-link").addClass("invisible");
        showTypeWriter.value = true;

        await callChatStream(
          "/api/send_message",
          { bot_nr: bot.value.bot_nr, messages: messages.value },
          messages.value
        )
      }


const callChatStream = async (url = "", data = {}, messages) => {
  const csrf = getCookie('csrftoken');
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrf,
    },
    body: JSON.stringify(data),
  });

  if (!response.body) return;

  const reader = response.body
    .pipeThrough(new TextDecoderStream())
    .getReader();

  // Read the eventstream until done
  while (true) {
    var { value, done } = await reader.read();
    if (done) {
      $("#input_line").removeClass("d-none")
      $(".edit-link").removeClass("invisible");
      showTypeWriter.value = false;

      // Handle markdown parsing
      let updatedMessage = messages[messages.length - 1];
      // updatedMessage.content = marked.parse(updatedMessage.content);
      messages[messages.length - 1] = updatedMessage;

      break;
    }

    // Append response to last message object
    let updatedMessage = messages[messages.length - 1];
    updatedMessage.content += value;
    messages[messages.length - 1] = updatedMessage;

    // Scroll to bottom of page
    // const scrollingElement = (document.scrollingElement || document.body);
    // scrollingElement.scrollTop = scrollingElement.scrollHeight;
  }
}

const getCookie = (name) => {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const editPrompt = (response_nr) => {
  messages.value.splice(response_nr + 1);
  message.value = messages.value.pop()["content"];
  showTypeWriter.value = false;
}

const toggleStartPrompt = () => {
  showSystemPrompt.value = !showSystemPrompt.value;
}

const deleteBot = () => {
  axios.delete('/api/bot_info/' + botNr.value)
    .then(response => {
      router.push({ name: 'home' });
    })
    .catch(error => {
      console.log(error);
    });
}

watchEffect(() => {
  startpromt()
});


</script>

<template>

  <!-- Modal -->
  <div class="modal fade" id="delete_bot" tabindex="-1" aria-labelledby="delete_bot_label" aria-hidden="true">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h1 class="modal-title fs-5" id="delete_bot_label">Slette bot</h1>
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          Vi du virkelig slette denne boten?
        </div>
        <div class="modal-footer">
          <button type="button" class="btn oslo-btn-secondary" data-bs-dismiss="modal">Avbryt</button>
          <button type="button" class="btn oslo-btn-warning" data-bs-dismiss="modal" @click="deleteBot">Ja jeg vil slette</button>
        </div>
      </div>
    </div>
  </div>

<h1 class="h2">
      {{ bot.title }}
    </h1>
    <p>
      {{ bot.ingress }}
    </p>

    <div class="d-flex">
      <button class="me-auto btn oslo-btn-secondary" @click="toggleStartPrompt">
        Vis ledetekst
      </button>
      <RouterLink v-if="bot.edit" active-class="active" class="btn oslo-btn-secondary" :to="'/editbot/'+bot.bot_nr">
        Rediger
      </RouterLink>
      <button v-if="bot.edit" class="btn oslo-btn-warning" data-bs-toggle="modal" data-bs-target="#delete_bot">
        Slett
      </button>
    </div>
    
    <div class="card border-dark">
      <ul class="list-group list-group-flush">
        <span v-for="(message_line, msg_nr) in messages" :key="msg_nr">
          <li v-if="message_line.role != 'system' || showSystemPrompt" class="container-fluid list-group-item response" :class="message_line.role">
            <span class="row">
              <div class="col-1 avatar">
                <img v-if="message_line.role === 'system'" src="@/components/icons/system.svg" alt="ledetekst:">
                <img v-if="message_line.role === 'user'" src="@/components/icons/user.svg" alt="du:">
                <img v-if="message_line.role === 'assistant'" src="@/components/icons/oslobot.svg" alt="bot:">
              </div>
              <div class="col">
                <span v-html="message_line.content" class="chat" :class="msg_nr === messages.length - 1 && showTypeWriter ? 'type-writer' : ''" >
                </span>
              </div>
              <div class="col-1 edit-link invisible">
                <a v-if="message_line.role === 'user'" href="#" @click="editPrompt(msg_nr)">
                  <img src="@/components/icons/rediger.svg" alt="rediger">
                </a>
              </div>
            </span>
          </li>
        </span>
      </ul>
    </div>
    <div id="input_line" class="mt-3">
      <textarea id="text-input" type="text" rows="5" aria-label="Skriv her. Ikke legg inn personlige og sensitive opplysninger." v-model="message" class="form-control" placeholder="Skriv her. Ikke legg inn personlige og sensitive opplysninger." @keypress.enter.exact="sendMessage()"></textarea>
      <div class="card">
      <div class="card-body bg-body-tertiary">
        <button class="btn oslo-btn-primary" type="button" id="button-send" @click="sendMessage()">Send</button>
        <button class="btn oslo-btn-secondary" type="button" id="button-new" @click="startpromt()">Ny samtale</button>
        <div><small>Husk at en AI ikke er et menneske og kan skrive ting som ikke stemmer med virkeligheten, og den gir ikke beskjed om når den gjør det.</small></div>
      </div>
    </div>
  </div>
  <div>
    &nbsp;
  </div>
  <!--     
 -->



</template>
