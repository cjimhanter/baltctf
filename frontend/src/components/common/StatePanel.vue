<script setup>
defineProps({
  mode: {
    type: String,
    required: true
  },
  title: {
    type: String,
    default: ""
  },
  message: {
    type: String,
    required: true
  }
});
</script>

<template>
  <section class="panel-card state-panel" :class="`state-panel--${mode}`">
    <div v-if="mode === 'loading'" class="state-panel__spinner"></div>
    <h2 v-if="title" class="state-panel__title">{{ title }}</h2>
    <p class="state-panel__message">
      <slot>{{ message }}</slot>
    </p>
  </section>
</template>
