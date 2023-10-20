$(document).ready(function () {
  const app = Vue.createApp({
    delimiters: ['${', '}'],
    data() {
      return {
        bot_nr: '',
        bot: null,
        message: '',
        messages: [],
        showTypeWriter: false,
        showSystemPrompt: false,
      }
    },
    computed: {
    },
    mounted() {
      this.bot_nr = $("#bot_nr").text();
    },
    methods: {
      sendMessage() {
        vm.messages.push(
          {
            "role": "user",
            "content": this.message,
          },
          {
            "role": "assistant",
            "content": "",
          }
        );
        this.message = '';
        $("#input_line").addClass("d-none")
        $(".edit-link").addClass("invisible");
        vm.showTypeWriter = true;

        callChatStream(
          "/api/send_message",
          { bot_nr: vm.bot.bot_nr, messages: vm.messages },
          vm.messages
        )
      },
      editPrompt(response_nr) {
        vm.messages.splice(response_nr + 1);
        vm.message = vm.messages.pop()["content"];
        vm.showTypeWriter = false;
      },
      newThread() {
        startpromt()
      },
      toggleStartPromt() {
        vm.showSystemPrompt = !vm.showSystemPrompt
      }
    }
  })

  function getCookie(name) {
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

  async function callChatStream(url = "", data = {}, messages) {
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
        vm.showTypeWriter = false;

        // Handle markdown parsing
        let updatedMessage = messages[messages.length - 1];
        updatedMessage.content = marked.parse(updatedMessage.content);
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

  async function postData(url = "", data = {}) {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      window.location.replace("/");
    }
    return response.json();
  }

  // get startpromt for bot
  function startpromt() {
    postData("/api/bot/" + vm.bot_nr, {}).then((data) => {
      vm.bot = data.bot;
      vm.messages = [{
        "role": "system",
        "content": vm.bot.prompt,
      }];
      vm.message = '';
    });
  }

  vm = app.mount('#bot_page')
  startpromt()

});
