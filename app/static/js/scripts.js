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
    },
    methods: {
      formatBg(line) {
        return line.role == "assistant" ? "text-bg-light" : "";
      },
      sendMessage() {
        vm.messages.push({
          "role": "user",
          "content": this.message,
        });
        postData(
          "/api/send_message",
          { bot_nr: vm.bot.bot_nr, messages: vm.messages },
        ).then((data) => {
            vm.messages.push(data.messages);
            $("#spinner").addClass("invisible")
            $("#input_line").removeClass("invisible")
        });
        this.message = '';
        this.genSpinnerText()
        $("#input_line").addClass("invisible")
        $("#spinner").removeClass("invisible")
      },
      newThread() {
        startpromt()
      },
      genSpinnerText() {
        spinner_texts = [
          'Fint at du venter mens jeg jobber med svaret ditt.',
          'Jeg kommer straks med et svar ...',
          'Vent en litt, så får du svar.',
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
    postData("/api/bot_info/"+vm.bot_nr, {}).then((data) => {
      vm.bot = data.bot_info
      vm.messages = [{
            "role": "system",
            "content": vm.bot.prompt,
          }] 
    });
  }

  vm = app.mount('#bot_page')
  startpromt()

});