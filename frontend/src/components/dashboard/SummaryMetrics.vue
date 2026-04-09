<script setup>
defineProps({
  cards: {
    type: Array,
    required: true
  }
});
</script>

<template>
  <section class="metrics metrics--five-up">
    <article
      v-for="card in cards"
      :key="card.label"
      class="metrics__card"
    >
      <span class="metrics__label">{{ card.label }}</span>
      <strong class="metrics__value">{{ card.value }}</strong>
      <p class="metrics__note">{{ card.note }}</p>
    </article>
  </section>
</template>
