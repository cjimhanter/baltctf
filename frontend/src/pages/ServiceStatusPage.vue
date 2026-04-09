<script setup>
import StatePanel from "../components/common/StatePanel.vue";
import ServiceStatusMatrix from "../components/services/ServiceStatusMatrix.vue";
import { useCompetitionContext } from "../composables/useCompetitionContext";
import { useI18n } from "../i18n";

const page = useCompetitionContext();
const { t } = useI18n();
</script>

<template>
  <section class="route-page route-page--services">
    <header class="route-page__header">
      <div>
        <p class="route-page__kicker">{{ t("pages.services.kicker") }}</p>
        <h1 class="route-page__title">{{ t("pages.services.title") }}</h1>
      </div>
      <p class="route-page__meta">{{ t("pages.services.meta") }}</p>
    </header>

    <StatePanel
      v-if="page.isServiceStatusLoading"
      mode="loading"
      :message="t('pages.services.loading')"
    />

    <ServiceStatusMatrix v-else :service-status="page.serviceStatus" />
  </section>
</template>
