<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  message: {
    type: String,
    required: true
  },
  tone: {
    type: String,
    default: "info"
  }
});
</script>

<template>
  <section class="notice" :class="`notice--${tone}`">
    <strong class="notice__title">{{ title }}</strong>
    <span class="notice__message">{{ message }}</span>
  </section>
</template>
