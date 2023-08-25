$(document).ready(function(){



  const app = Vue.createApp({
    delimiters: ['${', '}'],
    data() {
      return {
        bot_nr: '',
        bot: null,
        message: '',
        messages: [],
        spinner_text: '',
      }
    },
    computed: {
    },
    mounted() {
      this.bot_nr = $("#bot_nr").text();

      // Listen for responses
      const socket = io();
      socket.on('message_chunk', (data) => {
        // Append response to last message object
        let updatedMessage = this.messages[this.messages.length - 1];
        updatedMessage.content += data.message;
        this.messages[this.messages.length - 1] = updatedMessage;

        // Scroll to bottom of page
        const scrollingElement = (document.scrollingElement || document.body);
        scrollingElement.scrollTop = scrollingElement.scrollHeight;
      });
    },
    methods: {
      sendMessage() {
        vm.messages.push({
          "role": "user",
          "content": this.message,
        });
        postData(
          "/api/send_message",
          { bot_nr: vm.bot.bot_nr, messages: vm.messages },
        ).then(() => {
            $("#spinner").addClass("d-none")
            $("#input_line").removeClass("d-none")
            // $('html, body').animate({scrollTop: $("#lastline").offset().top}, 1000, "linear");
        });
        this.message = '';
        // Prepare response message object to be filled with socket response
        vm.messages.push({
          "role": "assistant",
          "content": "",
        })
        this.genSpinnerText()
        $("#input_line").addClass("d-none")
        $("#spinner").removeClass("d-none")
    },
      newThread() {
        startpromt()
      },
      genSpinnerText() {
        spinner_texts = [
          'Fint at du venter mens jeg jobber med svaret ditt.',
          'Jeg kommer straks med et svar ...',
          'Vent litt, så får du svar.',
          ];
        this.spinner_text = spinner_texts[Math.floor(Math.random() * 3)]
      },
    }
  })


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
    postData("/api/bot/"+vm.bot_nr, {}).then((data) => {
      vm.bot = data.bot
      vm.messages = [{
            "role": "system",
            "content": vm.bot.prompt,
          }] 
    });
  }

  vm = app.mount('#bot_page')
  startpromt()

});
