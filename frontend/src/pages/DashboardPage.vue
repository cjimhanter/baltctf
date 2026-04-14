<script setup>
import CompetitionBoard from "../components/dashboard/CompetitionBoard.vue";
import DashboardHero from "../components/dashboard/DashboardHero.vue";
import RoundsTimeline from "../components/dashboard/RoundsTimeline.vue";
import ServiceTimeline from "../components/dashboard/ServiceTimeline.vue";
import SummaryMetrics from "../components/dashboard/SummaryMetrics.vue";
import SubmissionHistory from "../components/dashboard/SubmissionHistory.vue";
import StatePanel from "../components/common/StatePanel.vue";
import { useCompetitionContext } from "../composables/useCompetitionContext";
import { useI18n } from "../i18n";

const page = useCompetitionContext();
const { t } = useI18n();
</script>

<template>
  <section class="page-shell dashboard-page">
    <DashboardHero
      :current-round-title="page.currentRoundTitle"
      :current-round-meta="page.currentRoundMeta"
      :leaderboard-leader="page.leaderboardLeader"
      :summary-cards="page.summaryCards"
      :is-busy="page.isLoading || page.isRefreshing"
      @refresh="page.loadDashboard({ refresh: true })"
    />

    <SummaryMetrics :cards="page.summaryCards" />

    <div class="dashboard-page__content">
      <StatePanel
        v-if="!page.isDashboardReady || page.isLoading"
        mode="loading"
        :message="t('dashboard.stateLoading')"
      />

      <StatePanel
        v-else-if="page.dashboardErrorMessage && !page.hasScoreboard"
        mode="error"
        :title="t('dashboard.stateErrorTitle')"
        :message="page.dashboardErrorMessage"
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

        <div class="dashboard-page__ops-grid">
          <ServiceTimeline
            :history="page.dashboard.service_status_history"
            :format-date-time="page.formatDateTime"
          />

          <SubmissionHistory
            :submissions="page.dashboard.submission_history"
            :format-date-time="page.formatDateTime"
          />
        </div>

        <RoundsTimeline
          :rounds="page.recentRounds"
          :format-date-time="page.formatDateTime"
        />
      </template>
    </div>
  </section>
</template>
