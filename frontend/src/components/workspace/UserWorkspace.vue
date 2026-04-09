<script setup>
import { useI18n } from "../../i18n";

defineProps({
  session: {
    type: Object,
    required: true
  },
  hasTeam: {
    type: Boolean,
    default: false
  },
  isCaptain: {
    type: Boolean,
    default: false
  },
  teamProfileForm: {
    type: Object,
    required: true
  },
  teamMemberForm: {
    type: Object,
    required: true
  },
  flagForm: {
    type: Object,
    required: true
  },
  maxTeamMembers: {
    type: Number,
    required: true
  },
  canAddTeamMember: {
    type: Boolean,
    default: false
  },
  isTeamActionLoading: {
    type: Boolean,
    default: false
  },
  isSubmittingFlag: {
    type: Boolean,
    default: false
  },
  formatDateTime: {
    type: Function,
    required: true
  }
});

const emit = defineEmits([
  "logout",
  "submit-flag",
  "update-team-profile",
  "add-team-member",
  "update-member-role",
  "remove-member"
]);

const { t } = useI18n();
</script>

<template>
  <section class="workspace">
    <article class="panel-card workspace__panel workspace__panel--session">
      <div class="panel-card__header">
        <div>
          <p class="panel-card__kicker">
            {{ hasTeam ? t("workspace.teamSession") : t("workspace.operatorSession") }}
          </p>
          <h2 class="panel-card__title">{{ hasTeam ? session.team?.name : session.user?.username }}</h2>
        </div>
        <button class="button button--ghost" type="button" @click="emit('logout')">
          {{ t("workspace.logout") }}
        </button>
      </div>

      <div v-if="hasTeam" class="workspace__summary">
        <div class="workspace__summary-card">
          <span class="workspace__summary-label">{{ t("workspace.signedInAs") }}</span>
          <strong class="workspace__summary-value">{{ session.user?.username }}</strong>
          <p class="workspace__summary-note">
            {{
              t("workspace.signedInSummary", {
                role: t(`role.${session.membership?.role || "player"}`),
                affiliation: session.team?.affiliation || t("common.independent")
              })
            }}
          </p>
        </div>

        <div class="workspace__summary-card">
          <span class="workspace__summary-label">{{ t("workspace.contact") }}</span>
          <strong class="workspace__summary-value">
            {{ session.team?.contact_email || t("common.notSet") }}
          </strong>
          <p class="workspace__summary-note">
            {{ t("common.membersCount", { count: session.members.length }) }}
          </p>
        </div>

        <div class="workspace__summary-card">
          <span class="workspace__summary-label">{{ t("workspace.moderation") }}</span>
          <strong class="workspace__summary-value">
            {{ t(`moderation.${session.team?.moderation_status || "pending"}`) }}
          </strong>
          <p class="workspace__summary-note">
            {{ session.team?.moderation_note || t("workspace.moderationNoteFallback") }}
          </p>
        </div>
      </div>

      <div v-else class="empty-hint">
        {{ t("workspace.noTeamAccount") }}
      </div>

      <div v-if="hasTeam" class="workspace__section">
        <div class="workspace__section-head">
          <h3 class="workspace__section-title">{{ t("workspace.roster") }}</h3>
        </div>

        <div class="workspace__roster">
          <article
            v-for="member in session.members"
            :key="member.id"
            class="workspace__member"
          >
            <div class="workspace__member-main">
              <strong class="workspace__member-name">{{ member.username }}</strong>
              <span class="workspace__member-meta">
                {{ member.first_name }} {{ member.last_name }}
              </span>
            </div>

            <div class="workspace__member-side">
              <span class="tag tag--neutral">{{ t(`role.${member.role}`) }}</span>

              <div v-if="isCaptain" class="workspace__member-actions">
                <button
                  v-if="member.role === 'player'"
                  class="button button--ghost"
                  type="button"
                  :disabled="isTeamActionLoading"
                  @click="emit('update-member-role', member, 'captain')"
                >
                  {{ t("workspace.promote") }}
                </button>
                <button
                  v-else-if="member.id !== session.user?.id"
                  class="button button--ghost"
                  type="button"
                  :disabled="isTeamActionLoading"
                  @click="emit('update-member-role', member, 'player')"
                >
                  {{ t("workspace.demote") }}
                </button>
                <button
                  v-if="member.id !== session.user?.id"
                  class="button button--ghost button--danger"
                  type="button"
                  :disabled="isTeamActionLoading"
                  @click="emit('remove-member', member)"
                >
                  {{ t("guest.remove") }}
                </button>
              </div>
            </div>
          </article>
        </div>
      </div>

      <div v-if="hasTeam && isCaptain" class="workspace__section">
        <div class="workspace__section-head">
          <h3 class="workspace__section-title">{{ t("workspace.captainTools") }}</h3>
        </div>

        <div class="workspace__tools">
          <article class="workspace__tool-card">
            <div class="workspace__section-head workspace__section-head--compact">
              <h3 class="workspace__section-title">{{ t("workspace.teamProfile") }}</h3>
            </div>

            <form class="form-stack" @submit.prevent="emit('update-team-profile')">
              <div class="field-grid">
                <label class="field">
                  <span class="field__label">{{ t("guest.affiliation") }}</span>
                  <input
                    v-model="teamProfileForm.affiliation"
                    class="field__control"
                    type="text"
                  />
                </label>

                <label class="field">
                  <span class="field__label">{{ t("guest.contactEmail") }}</span>
                  <input
                    v-model="teamProfileForm.contact_email"
                    class="field__control"
                    type="email"
                  />
                </label>
              </div>

              <button class="button" type="submit" :disabled="isTeamActionLoading">
                {{ isTeamActionLoading ? t("workspace.saving") : t("workspace.updateTeamProfile") }}
              </button>
            </form>
          </article>

          <article class="workspace__tool-card">
            <div class="workspace__section-head workspace__section-head--compact">
              <h3 class="workspace__section-title">{{ t("workspace.addMember") }}</h3>
              <span class="panel-card__note">
                {{ t("workspace.memberCounter", { current: session.members.length, max: maxTeamMembers }) }}
              </span>
            </div>

            <form class="form-stack" @submit.prevent="emit('add-team-member')">
              <div v-if="!canAddTeamMember" class="empty-hint">
                {{ t("workspace.teamLimitReached") }}
              </div>

              <div class="field-grid">
                <label class="field">
                  <span class="field__label">{{ t("guest.username") }}</span>
                  <input v-model="teamMemberForm.username" class="field__control" type="text" />
                </label>

                <label class="field">
                  <span class="field__label">{{ t("guest.password") }}</span>
                  <input
                    v-model="teamMemberForm.password"
                    class="field__control"
                    type="password"
                  />
                </label>

                <label class="field">
                  <span class="field__label">{{ t("guest.email") }}</span>
                  <input v-model="teamMemberForm.email" class="field__control" type="email" />
                </label>

                <label class="field">
                  <span class="field__label">{{ t("guest.firstName") }}</span>
                  <input
                    v-model="teamMemberForm.first_name"
                    class="field__control"
                    type="text"
                  />
                </label>

                <label class="field">
                  <span class="field__label">{{ t("guest.lastName") }}</span>
                  <input
                    v-model="teamMemberForm.last_name"
                    class="field__control"
                    type="text"
                  />
                </label>
              </div>

              <button
                class="button"
                type="submit"
                :disabled="isTeamActionLoading || !canAddTeamMember"
              >
                {{ isTeamActionLoading ? t("workspace.adding") : t("workspace.addPlayer") }}
              </button>
            </form>
          </article>
        </div>
      </div>
    </article>

    <article class="panel-card workspace__panel workspace__panel--submit">
      <div class="panel-card__header">
        <div>
          <p class="panel-card__kicker">
            {{ hasTeam ? t("workspace.flagSubmission") : t("workspace.operatorMode") }}
          </p>
          <h2 class="panel-card__title">
            {{ hasTeam ? t("workspace.submitCapturedFlags") : t("workspace.competitionControls") }}
          </h2>
        </div>
      </div>

      <template v-if="hasTeam">
        <form class="form-stack" @submit.prevent="emit('submit-flag')">
          <label class="field">
            <span class="field__label">{{ t("workspace.flagValue") }}</span>
            <input
              v-model="flagForm.flag"
              class="field__control"
              type="text"
              placeholder="BALTCTF{...}"
              autocomplete="off"
            />
          </label>

          <button class="button" type="submit" :disabled="isSubmittingFlag">
            {{ isSubmittingFlag ? t("guest.submitting") : t("workspace.submitFlag") }}
          </button>
        </form>

        <div class="workspace__section">
          <div class="workspace__section-head">
            <h3 class="workspace__section-title">{{ t("workspace.teamActivity") }}</h3>
          </div>

          <div v-if="session.recent_submissions.length === 0" class="empty-hint">
            {{ t("workspace.noSubmissions") }}
          </div>

          <div v-else class="workspace__activity-list">
            <article
              v-for="activity in session.recent_submissions"
              :key="activity.id"
              class="workspace__activity-item"
            >
              <div class="workspace__activity-topline">
                <strong class="workspace__activity-name">
                  {{ activity.submitted_by?.username || activity.submitting_team.name }}
                </strong>
                <span class="tag" :data-state="activity.status">
                  {{ t(`submissionState.${activity.status}`) }}
                </span>
              </div>
              <p class="workspace__activity-copy">
                {{
                  t("workspace.activityLine", {
                    target: activity.target_team?.name || t("common.unknownTarget"),
                    service: activity.service?.name || t("common.unknownService")
                  })
                }}
              </p>
              <div class="workspace__activity-meta">
                <span>{{ t("common.points", { count: activity.points_awarded }) }}</span>
                <span>{{ formatDateTime(activity.submitted_at) }}</span>
              </div>
            </article>
          </div>
        </div>
      </template>

      <div v-else class="empty-hint">
        {{ t("workspace.flagDisabled") }}
      </div>
    </article>
  </section>
</template>
