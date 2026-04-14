<script setup>
import { useI18n } from "../../i18n";

defineProps({
  serviceStatus: {
    type: Object,
    required: true
  }
});

const { t } = useI18n();
const statusKeys = ["up", "mumble", "corrupt", "down", "unknown"];
</script>

<template>
  <section class="status-matrix">
    <article class="panel-card">
      <div class="panel-card__header">
        <div>
          <p class="panel-card__kicker">{{ t("serviceMatrix.kicker") }}</p>
          <h2 class="panel-card__title">
            {{
              serviceStatus.current_round
                ? t("serviceMatrix.titleWithRound", { number: serviceStatus.current_round.number })
                : t("serviceMatrix.titleWaiting")
            }}
          </h2>
        </div>
      </div>

      <div v-if="serviceStatus.teams.length === 0" class="empty-hint">
        {{ t("serviceMatrix.noData") }}
      </div>

      <template v-else>
        <div class="status-matrix__summary">
          <article
            v-for="status in statusKeys"
            :key="status"
            class="status-matrix__summary-card"
            :data-state="status"
          >
            <span>{{ t(`serviceState.${status}`) }}</span>
            <strong>{{ serviceStatus.summary?.status_counts?.[status] || 0 }}</strong>
          </article>
        </div>

        <div class="status-matrix__table-wrap">
          <table class="status-matrix__table">
            <thead>
              <tr>
                <th>{{ t("serviceMatrix.team") }}</th>
                <th v-for="service in serviceStatus.services" :key="service.id">
                  {{ service.name }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="entry in serviceStatus.teams" :key="entry.team.id">
                <td class="status-matrix__team-cell">
                  <strong>{{ entry.team.name }}</strong>
                  <span>{{ entry.team.affiliation || t("common.independent") }}</span>
                </td>
                <td v-for="serviceEntry in entry.services" :key="serviceEntry.service.id">
                  <article
                    class="status-matrix__cell"
                    :data-state="serviceEntry.status"
                  >
                    <strong>{{ t(`serviceState.${serviceEntry.status}`) }}</strong>
                    <small>{{ t("common.points", { count: serviceEntry.points_awarded }) }}</small>
                    <p>{{ serviceEntry.message || t("common.noCheckerNote") }}</p>
                  </article>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </article>
  </section>
</template>
