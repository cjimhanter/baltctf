<script setup>
import { computed } from "vue";

import SubmissionHistory from "../components/dashboard/SubmissionHistory.vue";
import StatePanel from "../components/common/StatePanel.vue";
import { useCompetitionContext } from "../composables/useCompetitionContext";
import { useI18n } from "../i18n";

const page = useCompetitionContext();
const { t } = useI18n();

const scoreboardRows = computed(() => page.dashboard.scoreboard || []);
const topTeams = computed(() => scoreboardRows.value.slice(0, 3));
const currentRound = computed(() => page.dashboard.current_round);
const summary = computed(() => page.dashboard.summary || {});
const serviceStats = computed(() => page.dashboard.service_stats || []);
const submissionHistory = computed(() => page.dashboard.submission_history || []);
const statusKeys = ["up", "mumble", "corrupt", "down"];
</script>

<template>
  <section class="page-shell scoreboard-page">
    <header class="page-shell__header scoreboard-page__header">
      <div class="page-shell__intro">
        <p class="page-shell__kicker">{{ t("pages.scoreboard.kicker") }}</p>
        <h1 class="page-shell__title">{{ t("pages.scoreboard.title") }}</h1>
      </div>

      <div class="scoreboard-page__header-side">
        <p class="page-shell__meta">
          {{
            currentRound
              ? t("pages.scoreboard.metaRound", {
                  number: currentRound.number,
                  state: t(`roundState.${currentRound.state}`)
                })
              : t("pages.scoreboard.metaWaiting")
          }}
        </p>
        <button
          class="button button--secondary"
          type="button"
          :disabled="page.isLoading || page.isRefreshing"
          @click="page.loadDashboard({ refresh: true })"
        >
          {{ page.isRefreshing ? t("dashboard.refreshing") : t("dashboard.refresh") }}
        </button>
      </div>
    </header>

    <StatePanel
      v-if="!page.isDashboardReady || page.isLoading"
      mode="loading"
      :message="t('pages.scoreboard.loading')"
    />

    <StatePanel
      v-else-if="page.dashboardErrorMessage && !page.hasScoreboard"
      mode="error"
      :title="t('pages.scoreboard.errorTitle')"
      :message="page.dashboardErrorMessage"
    />

    <StatePanel
      v-else-if="!page.hasScoreboard"
      mode="empty"
      :title="t('pages.scoreboard.emptyTitle')"
      :message="t('pages.scoreboard.emptyMessage')"
    />

    <template v-else>
      <section class="scoreboard-page__podium" :aria-label="t('pages.scoreboard.podium')">
        <article
          v-for="entry in topTeams"
          :key="entry.team.slug"
          class="scoreboard-page__podium-card"
          :data-rank="entry.rank"
        >
          <span class="scoreboard-page__rank">{{ entry.rank }}</span>
          <div class="scoreboard-page__podium-copy">
            <strong>{{ entry.team.name }}</strong>
            <span>{{ entry.team.affiliation || t("common.independent") }}</span>
          </div>
          <strong class="scoreboard-page__podium-score">
            {{ t("common.points", { count: entry.total_points }) }}
          </strong>
        </article>
      </section>

      <section class="scoreboard-page__summary">
        <article class="scoreboard-page__summary-item">
          <span>{{ t("pages.scoreboard.trackedTeams") }}</span>
          <strong>{{ scoreboardRows.length }}</strong>
        </article>
        <article class="scoreboard-page__summary-item">
          <span>{{ t("pages.scoreboard.attackPoints") }}</span>
          <strong>{{ summary.attack_points_total || 0 }}</strong>
        </article>
        <article class="scoreboard-page__summary-item">
          <span>{{ t("pages.scoreboard.defensePoints") }}</span>
          <strong>{{ summary.defense_points_total || 0 }}</strong>
        </article>
        <article class="scoreboard-page__summary-item">
          <span>{{ t("pages.scoreboard.acceptedFlags") }}</span>
          <strong>{{ summary.accepted_submissions_count || 0 }}</strong>
        </article>
        <article class="scoreboard-page__summary-item">
          <span>{{ t("pages.scoreboard.rejectedFlags") }}</span>
          <strong>{{ summary.rejected_submissions_count || 0 }}</strong>
        </article>
        <article class="scoreboard-page__summary-item">
          <span>{{ t("pages.scoreboard.checkerChecks") }}</span>
          <strong>{{ summary.checker_status_count || 0 }}</strong>
        </article>
      </section>

      <section class="panel-card scoreboard-page__board">
        <div class="panel-card__header">
          <div>
            <p class="panel-card__kicker">{{ t("board.scoreboardKicker") }}</p>
            <h2 class="panel-card__title">{{ t("pages.scoreboard.tableTitle") }}</h2>
          </div>
        </div>

        <div class="scoreboard-page__table-wrap">
          <table class="scoreboard-page__table">
            <thead>
              <tr>
                <th>#</th>
                <th>{{ t("board.team") }}</th>
                <th>{{ t("board.attack") }}</th>
                <th>{{ t("board.defense") }}</th>
                <th>{{ t("pages.scoreboard.acceptedColumn") }}</th>
                <th>{{ t("pages.scoreboard.checksColumn") }}</th>
                <th>{{ t("board.total") }}</th>
                <th>{{ t("pages.scoreboard.serviceColumn") }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="entry in scoreboardRows"
                :key="entry.team.slug"
              >
                <td class="scoreboard-page__table-rank">{{ entry.rank }}</td>
                <td>
                  <div class="scoreboard-page__team">
                    <strong>{{ entry.team.name }}</strong>
                    <span>{{ entry.team.affiliation || t("common.independent") }}</span>
                  </div>
                </td>
                <td>{{ entry.attack_points }}</td>
                <td>{{ entry.defense_points }}</td>
                <td>{{ entry.accepted_submission_count }}</td>
                <td>{{ entry.defense_check_count }}</td>
                <td class="scoreboard-page__total">{{ entry.total_points }}</td>
                <td>
                  <div class="scoreboard-page__service-stack">
                    <span
                      v-for="serviceState in entry.service_breakdown"
                      :key="`${entry.team.slug}-${serviceState.service.slug}`"
                      class="scoreboard-page__service-chip"
                      :data-state="serviceState.status"
                    >
                      {{ serviceState.service.name }}
                      <strong>{{ t(`serviceState.${serviceState.status}`) }}</strong>
                    </span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="panel-card scoreboard-page__services">
        <div class="panel-card__header">
          <div>
            <p class="panel-card__kicker">{{ t("pages.scoreboard.serviceStatsKicker") }}</p>
            <h2 class="panel-card__title">{{ t("pages.scoreboard.serviceStatsTitle") }}</h2>
          </div>
        </div>

        <div class="scoreboard-page__service-grid">
          <article
            v-for="service in serviceStats"
            :key="service.service.slug"
            class="scoreboard-page__service-card"
          >
            <div class="scoreboard-page__service-head">
              <strong>{{ service.service.name }}</strong>
              <span>
                {{ t("common.percent", { count: service.uptime_percent || 0 }) }}
                {{ t("pages.scoreboard.uptime") }}
              </span>
            </div>

            <div class="scoreboard-page__service-metrics">
              <span>{{ t("pages.scoreboard.serviceFlags", { count: service.flag_count }) }}</span>
              <span>{{ t("pages.scoreboard.serviceAttacks", { count: service.accepted_submission_count }) }}</span>
              <span>{{ t("pages.scoreboard.serviceDefense", { count: service.defense_points }) }}</span>
              <span>{{ t("pages.scoreboard.serviceChecks", { count: service.checker_status_count }) }}</span>
            </div>

            <div class="scoreboard-page__service-counts">
              <span
                v-for="status in statusKeys"
                :key="`${service.service.slug}-${status}`"
                :data-state="status"
              >
                {{ t(`serviceState.${status}`) }} {{ service.status_counts?.[status] || 0 }}
              </span>
            </div>
          </article>
        </div>
      </section>

      <SubmissionHistory
        :submissions="submissionHistory"
        :format-date-time="page.formatDateTime"
      />
    </template>
  </section>
</template>
