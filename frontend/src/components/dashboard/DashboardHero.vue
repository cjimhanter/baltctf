<script setup>
import { useI18n } from "../../i18n";

defineProps({
  currentRoundTitle: {
    type: String,
    required: true
  },
  currentRoundMeta: {
    type: String,
    required: true
  },
  isBusy: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(["refresh"]);
const { t } = useI18n();
</script>

<template>
  <section class="hero">
    <div class="hero__copy">
      <p class="hero__eyebrow">{{ t("dashboard.heroEyebrow") }}</p>
      <h1 class="hero__title">{{ t("dashboard.heroTitle") }}</h1>
      <p class="hero__lead">{{ t("dashboard.heroLead") }}</p>
    </div>

    <div class="hero__card">
      <span class="hero__label">{{ currentRoundTitle }}</span>
      <strong class="hero__meta">{{ currentRoundMeta }}</strong>
      <button
        class="button hero__refresh"
        type="button"
        :disabled="isBusy"
        @click="emit('refresh')"
      >
        {{ isBusy ? t("dashboard.refreshing") : t("dashboard.refresh") }}
      </button>
    </div>
  </section>
</template>
