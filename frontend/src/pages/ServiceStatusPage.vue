<script setup>
import StatePanel from "../components/common/StatePanel.vue";
import ServiceTimeline from "../components/dashboard/ServiceTimeline.vue";
import ServiceStatusMatrix from "../components/services/ServiceStatusMatrix.vue";
import { useCompetitionContext } from "../composables/useCompetitionContext";
import { useI18n } from "../i18n";

const page = useCompetitionContext();
const { t } = useI18n();
</script>

<template>
  <section class="page-shell services-page">
    <header class="page-shell__header">
      <div class="page-shell__intro">
        <p class="page-shell__kicker">{{ t("pages.services.kicker") }}</p>
        <h1 class="page-shell__title">{{ t("pages.services.title") }}</h1>
      </div>
      <p class="page-shell__meta">{{ t("pages.services.meta") }}</p>
    </header>

    <div class="services-page__content">
      <StatePanel
        v-if="!page.isServiceStatusReady || page.isServiceStatusLoading"
        mode="loading"
        :message="t('pages.services.loading')"
      />

      <StatePanel
        v-else-if="page.serviceStatusErrorMessage && !page.hasServiceStatusData"
        mode="error"
        :title="t('pages.services.errorTitle')"
        :message="page.serviceStatusErrorMessage"
      />

      <template v-else>
        <ServiceStatusMatrix :service-status="page.serviceStatus" />
        <ServiceTimeline
          :history="page.serviceStatus.history"
          :format-date-time="page.formatDateTime"
        />
      </template>
    </div>
  </section>
</template>
