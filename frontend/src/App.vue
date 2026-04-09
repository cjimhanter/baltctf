<script setup>
import { computed, reactive } from "vue";
import { RouterLink, RouterView } from "vue-router";

import NoticeBanner from "./components/common/NoticeBanner.vue";
import { provideCompetitionPage } from "./composables/useCompetitionContext";
import { useCompetitionPage } from "./composables/useCompetitionPage";
import { languageOptions, useI18n } from "./i18n";

const page = reactive(useCompetitionPage());
provideCompetitionPage(page);

const { currentLanguage, setLanguage, t } = useI18n();

const navigationItems = computed(() => [
  { name: "dashboard", label: t("nav.dashboard"), to: "/" },
  { name: "services", label: t("nav.services"), to: "/services" },
  { name: "team", label: t("nav.team"), to: "/team" },
  { name: "admin", label: t("nav.admin"), to: "/admin" }
]);
</script>

<template>
  <main class="page">
    <header class="app-shell">
      <div class="app-shell__top">
        <div class="app-shell__brand">
          <p class="app-shell__eyebrow">{{ t("shell.eyebrow") }}</p>
          <h1 class="app-shell__title">{{ t("shell.title") }}</h1>
        </div>

        <div class="app-shell__controls">
          <div class="app-shell__language">
            <span class="app-shell__language-label">{{ t("shell.language") }}</span>
            <div class="app-shell__language-switch">
              <button
                v-for="option in languageOptions"
                :key="option.code"
                class="app-shell__language-button"
                :class="{ 'app-shell__language-button--active': currentLanguage === option.code }"
                type="button"
                @click="setLanguage(option.code)"
              >
                {{ option.label }}
              </button>
            </div>
          </div>

          <div class="app-shell__session">
            <strong>
              {{
                page.session.authenticated
                  ? page.session.user?.username
                  : t("shell.guestSession")
              }}
            </strong>
            <span>
              {{
                page.session.authenticated
                  ? page.session.team?.name || t("shell.operatorAccount")
                  : t("shell.guestHint")
              }}
            </span>
          </div>
        </div>
      </div>

      <nav class="app-shell__nav">
        <RouterLink
          v-for="item in navigationItems"
          :key="item.name"
          :to="item.to"
          class="app-shell__link"
        >
          {{ item.label }}
        </RouterLink>
      </nav>
    </header>

    <NoticeBanner
      v-if="page.apiErrorMessage"
      :title="t('notice.connection')"
      :message="page.apiErrorMessage"
      tone="error"
    />

    <NoticeBanner
      v-if="page.authMessage"
      :title="t('notice.account')"
      :message="page.authMessage"
      tone="info"
    />

    <NoticeBanner
      v-if="page.reservationMessage"
      :title="t('notice.reservation')"
      :message="page.reservationMessage"
      tone="team"
    />

    <NoticeBanner
      v-if="page.adminMessage"
      :title="t('notice.admin')"
      :message="page.adminMessage"
      tone="admin"
    />

    <NoticeBanner
      v-if="page.submissionMessage"
      :title="t('notice.flag')"
      :message="page.submissionMessage"
      tone="subtle"
    />

    <NoticeBanner
      v-if="page.teamMessage"
      :title="t('notice.team')"
      :message="page.teamMessage"
      tone="team"
    />

    <RouterView />
  </main>
</template>
