<script setup>
import AdminConsole from "../components/admin/AdminConsole.vue";
import StatePanel from "../components/common/StatePanel.vue";
import { useCompetitionContext } from "../composables/useCompetitionContext";
import { useI18n } from "../i18n";

const page = useCompetitionContext();
const { t } = useI18n();
</script>

<template>
  <section class="route-page route-page--admin">
    <header class="route-page__header">
      <div>
        <p class="route-page__kicker">{{ t("pages.admin.kicker") }}</p>
        <h1 class="route-page__title">{{ t("pages.admin.title") }}</h1>
      </div>
      <p class="route-page__meta">{{ t("pages.admin.meta") }}</p>
    </header>

    <StatePanel
      v-if="!page.session.authenticated"
      mode="empty"
      :title="t('pages.admin.authTitle')"
      :message="t('pages.admin.authMessage')"
    />

    <StatePanel
      v-else-if="!page.isAdmin"
      mode="empty"
      :title="t('pages.admin.staffTitle')"
      :message="t('pages.admin.staffMessage')"
    />

    <AdminConsole
      v-else
      :admin-state="page.adminState"
      :admin-team-form="page.adminTeamForm"
      :admin-service-form="page.adminServiceForm"
      :admin-round-form="page.adminRoundForm"
      :admin-settings-form="page.adminSettingsForm"
      :admin-schedule-form="page.adminScheduleForm"
      :admin-running-round="page.adminRunningRound"
      :checker-status-cards="page.checkerStatusCards"
      :is-admin-loading="page.isAdminLoading"
      :format-date-time="page.formatDateTime"
      @create-team="page.handleAdminTeamCreate"
      @set-team-moderation="page.setTeamModeration"
      @toggle-team="page.toggleTeamActive"
      @delete-team="page.deleteTeam"
      @create-service="page.handleAdminServiceCreate"
      @toggle-service="page.toggleServiceActive"
      @delete-service="page.deleteService"
      @create-round="page.handleAdminRoundCreate"
      @schedule-rounds="page.handleAdminRoundSchedule"
      @update-settings="page.handleAdminSettingsUpdate"
      @approve-reservation="page.approveReservation"
      @reject-reservation="page.rejectReservation"
      @start-round="page.startRound"
      @finish-round="page.finishRound"
      @generate-flags="page.generateFlags"
      @run-checker-tick="page.runCheckerTick"
    />
  </section>
</template>
