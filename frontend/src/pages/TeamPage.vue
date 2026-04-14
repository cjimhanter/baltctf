<script setup>
import GuestAccessSection from "../components/access/GuestAccessSection.vue";
import StatePanel from "../components/common/StatePanel.vue";
import UserWorkspace from "../components/workspace/UserWorkspace.vue";
import { useCompetitionContext } from "../composables/useCompetitionContext";
import { useI18n } from "../i18n";

const page = useCompetitionContext();
const { t } = useI18n();
</script>

<template>
  <section class="page-shell team-page">
    <header class="page-shell__header">
      <div class="page-shell__intro">
        <p class="page-shell__kicker">{{ t("pages.team.kicker") }}</p>
        <h1 class="page-shell__title">{{ t("pages.team.title") }}</h1>
      </div>
      <p class="page-shell__meta">
        {{
          page.registrationSettings.registration_available
            ? t("pages.team.registrationOpen")
            : t("pages.team.registrationClosed")
        }}
      </p>
    </header>

    <div class="team-page__content">
      <StatePanel
        v-if="!page.isSessionReady"
        mode="loading"
        :message="t('pages.team.loading')"
      />

      <GuestAccessSection
        v-else-if="!page.session.authenticated"
        :login-form="page.loginForm"
        :register-form="page.registerForm"
        :reservation-form="page.reservationForm"
        :registration-settings="page.registrationSettings"
        :is-auth-loading="page.isAuthLoading"
        :is-reservation-loading="page.isReservationLoading"
        :max-team-members="page.MAX_TEAM_MEMBERS"
        :can-add-participant="page.canAddParticipant"
        @login="page.handleLogin"
        @register="page.handleRegister"
        @reserve-team-name="page.handleReservationRequest"
        @add-participant="page.addParticipant"
        @remove-participant="page.removeParticipant"
      />

      <template v-else>
        <UserWorkspace
          :session="page.session"
          :has-team="page.hasTeam"
          :is-captain="page.isCaptain"
          :team-profile-form="page.teamProfileForm"
          :team-member-form="page.teamMemberForm"
          :flag-form="page.flagForm"
          :max-team-members="page.MAX_TEAM_MEMBERS"
          :can-add-team-member="page.canAddTeamMember"
          :is-team-action-loading="page.isTeamActionLoading"
          :is-submitting-flag="page.isSubmittingFlag"
          :format-date-time="page.formatDateTime"
          @logout="page.handleLogout"
          @submit-flag="page.handleFlagSubmit"
          @update-team-profile="page.handleTeamProfileUpdate"
          @add-team-member="page.handleTeamMemberAdd"
          @update-member-role="page.updateMemberRole"
          @remove-member="page.removeMember"
        />

        <StatePanel
          v-if="!page.hasTeam"
          mode="empty"
          :title="t('pages.team.noTeamTitle')"
          :message="t('pages.team.noTeamMessage')"
        />
      </template>
    </div>
  </section>
</template>
