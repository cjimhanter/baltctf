<script setup>
import { useI18n } from "../../i18n";

defineProps({
  rounds: {
    type: Array,
    required: true
  },
  formatDateTime: {
    type: Function,
    required: true
  }
});

const { t } = useI18n();
</script>

<template>
  <section class="panel-card round-timeline">
    <div class="panel-card__header">
      <div>
        <p class="panel-card__kicker">{{ t("timeline.kicker") }}</p>
        <h2 class="panel-card__title">{{ t("timeline.title") }}</h2>
      </div>
    </div>

    <div class="round-timeline__track">
      <article
        v-for="round in rounds"
        :key="round.id"
        class="round-timeline__card"
        :data-state="round.state"
      >
        <span class="round-timeline__label">{{ t("common.roundLabel", { number: round.number }) }}</span>
        <strong class="round-timeline__state">{{ t(`roundState.${round.state}`) }}</strong>
        <small class="round-timeline__time">{{ formatDateTime(round.started_at) }}</small>
        <div class="round-timeline__stats">
          <span>{{ t("timeline.attack", { count: round.attack_points || 0 }) }}</span>
          <span>{{ t("timeline.defense", { count: round.defense_points || 0 }) }}</span>
          <span>{{ t("timeline.checks", { count: round.checker_status_count || 0 }) }}</span>
        </div>
      </article>
    </div>
  </section>
</template>
