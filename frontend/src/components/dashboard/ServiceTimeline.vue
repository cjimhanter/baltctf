<script setup>
import { useI18n } from "../../i18n";

defineProps({
  history: {
    type: Array,
    default: () => []
  },
  formatDateTime: {
    type: Function,
    required: true
  }
});

const { t } = useI18n();
const statusKeys = ["up", "mumble", "corrupt", "down", "unknown"];

function countFor(entry, status) {
  return entry.status_counts?.[status] || 0;
}

function dominantState(entry) {
  if (entry.unknown > 0 || countFor(entry, "down") > 0) {
    return "down";
  }
  if (countFor(entry, "corrupt") > 0) {
    return "corrupt";
  }
  if (countFor(entry, "mumble") > 0) {
    return "mumble";
  }
  if (countFor(entry, "up") > 0) {
    return "up";
  }
  return "unknown";
}
</script>

<template>
  <section class="panel-card service-timeline">
    <div class="panel-card__header">
      <div>
        <p class="panel-card__kicker">{{ t("serviceTimeline.kicker") }}</p>
        <h2 class="panel-card__title">{{ t("serviceTimeline.title") }}</h2>
      </div>
    </div>

    <div v-if="history.length === 0" class="empty-hint">
      {{ t("serviceTimeline.noData") }}
    </div>

    <div v-else class="service-timeline__rounds">
      <article
        v-for="roundEntry in history"
        :key="roundEntry.round?.id || roundEntry.round?.number"
        class="service-timeline__round"
      >
        <div class="service-timeline__round-head">
          <div>
            <strong>
              {{ t("common.roundLabel", { number: roundEntry.round?.number || "?" }) }}
            </strong>
            <span>
              {{
                roundEntry.round
                  ? t("common.since", {
                      state: t(`roundState.${roundEntry.round.state}`),
                      date: formatDateTime(roundEntry.round.started_at)
                    })
                  : t("common.noData")
              }}
            </span>
          </div>
        </div>

        <div class="service-timeline__services">
          <article
            v-for="serviceEntry in roundEntry.services"
            :key="`${roundEntry.round?.id}-${serviceEntry.service.slug}`"
            class="service-timeline__service"
            :data-state="dominantState(serviceEntry)"
          >
            <div class="service-timeline__service-head">
              <strong>{{ serviceEntry.service.name }}</strong>
              <span>
                {{ t("serviceTimeline.checked", { count: serviceEntry.checked_count }) }}
              </span>
            </div>

            <div class="service-timeline__counts">
              <span
                v-for="status in statusKeys"
                :key="status"
                class="service-timeline__count"
                :data-state="status"
              >
                {{ t(`serviceState.${status}`) }} {{ countFor(serviceEntry, status) }}
              </span>
            </div>

            <div class="service-timeline__meta">
              <span>{{ t("common.points", { count: serviceEntry.defense_points }) }}</span>
              <span>
                {{
                  serviceEntry.latest_reported_at
                    ? formatDateTime(serviceEntry.latest_reported_at)
                    : t("common.noData")
                }}
              </span>
            </div>
          </article>
        </div>
      </article>
    </div>
  </section>
</template>
