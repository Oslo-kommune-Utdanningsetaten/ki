<script setup>
import { defineProps, defineEmits } from 'vue'
import BotAvatar from '@/components/BotAvatar.vue'
import { bodyColors, hairColors } from '@/utils/botAvatar.js'

const emit = defineEmits(['update:avatarScheme'])

const props = defineProps({
  avatarScheme: {
    type: Array,
    required: true,
  },
})

const botAttributes = [
  {
    id: 1,
    text: 'Hode',
    options: [
      { id: 0, text: 'Firkant' },
      { id: 1, text: 'Høy' },
      { id: 2, text: 'Smal hake' },
      { id: 3, text: 'Bred hake' },
    ],
  },
  {
    id: 2,
    text: 'Øyne',
    options: [
      { id: 0, text: 'Sirkel' },
      { id: 1, text: 'Kvadrat' },
      { id: 2, text: 'Rektangel' },
      { id: 3, text: 'Glimt' },
      { id: 4, text: 'Diamant' },
      { id: 5, text: 'Trekant' },
    ],
  },
  {
    id: 3,
    text: 'Hår',
    options: [
      { id: 0, text: 'Ingen' },
      { id: 1, text: 'Lue' },
      { id: 2, text: 'Pannelugg' },
      { id: 3, text: 'Sideskill' },
    ],
  },
  {
    id: 4,
    text: 'Ører',
    options: [
      { id: 0, text: 'Nei' },
      { id: 1, text: 'Store' },
      { id: 2, text: 'Små' },
    ],
  },
  {
    id: 5,
    text: 'Armer',
    options: [
      { id: 0, text: 'Skulder' },
      { id: 1, text: 'Rett' },
      { id: 2, text: 'Opp' },
    ],
  },
  {
    id: 6,
    text: 'Nakke',
    options: [
      { id: 0, text: 'Tykk' },
      { id: 1, text: 'Tynn' },
      { id: 2, text: 'Trekkspill' },
      { id: 3, text: 'Skrå' },
    ],
  },
  {
    id: 0,
    text: 'Farge, kropp',
    options: bodyColors,
  },
  {
    id: 7,
    text: 'Farge, hår',
    options: hairColors,
  },
]

const randomizeAttributes = () => {
  const randomAttributes = []
  botAttributes.forEach(attr => {
    randomAttributes.push(Math.floor(Math.random() * attr.options.length))
  })
  emit('update:avatarScheme', randomAttributes)
}

const handleOptionChange = event => {
  const updatedAvatarScheme = [...props.avatarScheme]
  emit('update:avatarScheme', updatedAvatarScheme)
}
</script>

<template>
  <div class="modal-body">
    Her kan du bestemme utseendet på din bot. Eller
    <button
      class="btn oslo-btn-secondary ms-0"
      @click="randomizeAttributes"
      title="La tilfeldighetene avgjøre"
    >
      La tilfeldighetene avgjøre
    </button>
  </div>
  <div class="modal-body row">
    <div class="col-6">
      <div>
        <fieldset v-for="attribute in botAttributes">
          <div class="mt-2 border-bottom">
            <legend>{{ attribute.text }}</legend>
          </div>
          <div class="row">
            <div v-for="option in attribute.options" class="col-md-6 align-items-center">
              <input
                class="me-2"
                type="radio"
                :name="attribute.id"
                :id="`${attribute.id}:${option.id}`"
                :value="option.id"
                :disabled="attribute.id == 7 && props.avatarScheme[3] == 0"
                :text="option.text"
                v-model="props.avatarScheme[attribute.id]"
                @change="handleOptionChange"
              />
              <label :for="`${attribute.id}:${option.id}`" class="form-check-label">
                {{ option.text }}
              </label>
            </div>
          </div>
        </fieldset>
      </div>
    </div>
    <div class="col-6">
      <BotAvatar :avatarScheme="avatarScheme" />
    </div>
  </div>
</template>
