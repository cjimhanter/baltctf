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
  leaderboardLeader: {
    type: Object,
    default: null
  },
  summaryCards: {
    type: Array,
    default: () => []
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
      <button
        class="button hero__refresh"
        type="button"
        :disabled="isBusy"
        @click="emit('refresh')"
      >
        {{ isBusy ? t("dashboard.refreshing") : t("dashboard.refresh") }}
      </button>
    </div>

    <div class="hero__ops">
      <article class="hero__round">
        <span class="hero__label">{{ currentRoundTitle }}</span>
        <strong class="hero__meta">{{ currentRoundMeta }}</strong>
      </article>

      <article class="hero__leader" v-if="leaderboardLeader">
        <span>{{ t("board.leader") }}</span>
        <strong>{{ leaderboardLeader.team.name }}</strong>
        <small>{{ t("common.points", { count: leaderboardLeader.total_points }) }}</small>
      </article>

      <div class="hero__signals">
        <article
          v-for="card in summaryCards.slice(0, 3)"
          :key="card.label"
          class="hero__signal"
        >
          <span>{{ card.label }}</span>
          <strong>{{ card.value }}</strong>
        </article>
      </div>
    </div>
  </section>
</template>
