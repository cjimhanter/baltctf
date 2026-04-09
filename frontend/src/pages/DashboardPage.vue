<script setup>
import CompetitionBoard from "../components/dashboard/CompetitionBoard.vue";
import DashboardHero from "../components/dashboard/DashboardHero.vue";
import RoundsTimeline from "../components/dashboard/RoundsTimeline.vue";
import SummaryMetrics from "../components/dashboard/SummaryMetrics.vue";
import StatePanel from "../components/common/StatePanel.vue";
import { useCompetitionContext } from "../composables/useCompetitionContext";
import { useI18n } from "../i18n";

const page = useCompetitionContext();
const { t } = useI18n();
</script>

<template>
  <section class="route-page route-page--dashboard">
    <DashboardHero
      :current-round-title="page.currentRoundTitle"
      :current-round-meta="page.currentRoundMeta"
      :is-busy="page.isLoading || page.isRefreshing"
      @refresh="page.loadDashboard({ refresh: true })"
    />

    <SummaryMetrics :cards="page.summaryCards" />

    <StatePanel
      v-if="page.isLoading && !page.hasScoreboard"
      mode="loading"
      :message="t('dashboard.stateLoading')"
    />

    <StatePanel
      v-else-if="!page.hasScoreboard"
      mode="empty"
      :title="t('dashboard.stateEmptyTitle')"
      :message="t('dashboard.stateEmptyMessage')"
    >
      {{ t("dashboard.stateEmptyMessage") }}
      <code>python manage.py seed_demo_data --reset</code>
    </StatePanel>

    <template v-else>
      <CompetitionBoard
        :dashboard="page.dashboard"
        :leaderboard-leader="page.leaderboardLeader"
        :format-date-time="page.formatDateTime"
      />

      <RoundsTimeline
        :rounds="page.recentRounds"
        :format-date-time="page.formatDateTime"
      />
    </template>
  </section>
</template>
