<script setup>
import { useI18n } from "../../i18n";

defineProps({
  adminState: {
    type: Object,
    required: true
  },
  adminTeamForm: {
    type: Object,
    required: true
  },
  adminServiceForm: {
    type: Object,
    required: true
  },
  adminRoundForm: {
    type: Object,
    required: true
  },
  adminSettingsForm: {
    type: Object,
    required: true
  },
  adminScheduleForm: {
    type: Object,
    required: true
  },
  adminRunningRound: {
    type: Object,
    default: null
  },
  checkerStatusCards: {
    type: Array,
    required: true
  },
  isAdminLoading: {
    type: Boolean,
    default: false
  },
  formatDateTime: {
    type: Function,
    required: true
  }
});

const emit = defineEmits([
  "create-team",
  "set-team-moderation",
  "toggle-team",
  "delete-team",
  "create-service",
  "toggle-service",
  "delete-service",
  "create-round",
  "schedule-rounds",
  "update-settings",
  "approve-reservation",
  "reject-reservation",
  "start-round",
  "finish-round",
  "generate-flags",
  "run-checker-tick"
]);

const { t } = useI18n();
</script>

<template>
  <section class="admin-console">
    <article class="panel-card admin-console__panel admin-console__panel--wide">
      <div class="panel-card__header">
        <div>
          <p class="panel-card__kicker">{{ t("admin.registrationKicker") }}</p>
          <h2 class="panel-card__title">{{ t("admin.registrationTitle") }}</h2>
        </div>
      </div>

      <form class="form-stack" @submit.prevent="emit('update-settings')">
        <div class="field-grid">
          <label class="field field--checkbox">
            <input v-model="adminSettingsForm.registration_open" type="checkbox" />
            <span class="field__label">{{ t("admin.registrationOpen") }}</span>
          </label>

          <label class="field field--checkbox">
            <input
              v-model="adminSettingsForm.reservation_required_for_registration"
              type="checkbox"
            />
            <span class="field__label">{{ t("admin.reservationRequired") }}</span>
          </label>

          <label class="field field--checkbox">
            <input v-model="adminSettingsForm.auto_approve_registrations" type="checkbox" />
            <span class="field__label">{{ t("admin.autoApprove") }}</span>
          </label>

          <label class="field">
            <span class="field__label">{{ t("admin.registrationStarts") }}</span>
            <input
              v-model="adminSettingsForm.registration_starts_at"
              class="field__control"
              type="datetime-local"
            />
          </label>

          <label class="field">
            <span class="field__label">{{ t("admin.registrationEnds") }}</span>
            <input
              v-model="adminSettingsForm.registration_ends_at"
              class="field__control"
              type="datetime-local"
            />
          </label>

          <label class="field">
            <span class="field__label">{{ t("admin.roundDuration") }}</span>
            <input
              v-model="adminSettingsForm.round_duration_minutes"
              class="field__control"
              type="number"
              min="1"
            />
          </label>

          <label class="field">
            <span class="field__label">{{ t("admin.breakDuration") }}</span>
            <input
              v-model="adminSettingsForm.round_break_minutes"
              class="field__control"
              type="number"
              min="0"
            />
          </label>
        </div>

        <button class="button" type="submit" :disabled="isAdminLoading">
          {{ isAdminLoading ? t("workspace.saving") : t("admin.saveSettings") }}
        </button>
      </form>
    </article>

    <article class="panel-card admin-console__panel">
      <div class="panel-card__header">
        <div>
          <p class="panel-card__kicker">{{ t("admin.reservationsKicker") }}</p>
          <h2 class="panel-card__title">{{ t("admin.reservationsTitle") }}</h2>
        </div>
      </div>

      <div v-if="adminState.reservations.length === 0" class="empty-hint">
        {{ t("admin.reservationsEmpty") }}
      </div>

      <div v-else class="admin-console__list">
        <article
          v-for="reservation in adminState.reservations"
          :key="reservation.id"
          class="admin-console__entity"
        >
          <div class="admin-console__entity-main">
            <strong class="admin-console__entity-title">{{ reservation.name }}</strong>
            <span class="admin-console__entity-meta">
              {{ reservation.captain_username }} · {{ reservation.contact_email }}
            </span>
            <small class="admin-console__entity-copy">
              {{
                reservation.expires_at
                  ? t("common.expiresAt", { date: formatDateTime(reservation.expires_at) })
                  : t("common.noExpiration")
              }}
            </small>
          </div>

          <div class="admin-console__actions">
            <span class="tag tag--neutral">{{ t(`reservationStatus.${reservation.status}`) }}</span>
            <button
              v-if="reservation.status !== 'claimed'"
              class="button button--ghost"
              type="button"
              :disabled="isAdminLoading"
              @click="emit('approve-reservation', reservation)"
            >
              {{ t("admin.approve") }}
            </button>
            <button
              v-if="reservation.status !== 'claimed'"
              class="button button--ghost button--danger"
              type="button"
              :disabled="isAdminLoading"
              @click="emit('reject-reservation', reservation)"
            >
              {{ t("admin.reject") }}
            </button>
          </div>
        </article>
      </div>
    </article>

    <article class="panel-card admin-console__panel">
      <div class="panel-card__header">
        <div>
          <p class="panel-card__kicker">{{ t("admin.teamsKicker") }}</p>
          <h2 class="panel-card__title">{{ t("admin.teamsTitle") }}</h2>
        </div>
      </div>

      <form class="form-stack" @submit.prevent="emit('create-team')">
        <div class="field-grid">
          <label class="field">
            <span class="field__label">{{ t("admin.name") }}</span>
            <input v-model="adminTeamForm.name" class="field__control" type="text" />
          </label>

          <label class="field">
            <span class="field__label">{{ t("guest.affiliation") }}</span>
            <input v-model="adminTeamForm.affiliation" class="field__control" type="text" />
          </label>

          <label class="field">
            <span class="field__label">{{ t("guest.contactEmail") }}</span>
            <input v-model="adminTeamForm.contact_email" class="field__control" type="email" />
          </label>
        </div>

        <button class="button" type="submit" :disabled="isAdminLoading">
          {{ isAdminLoading ? t("workspace.saving") : t("admin.createTeam") }}
        </button>
      </form>

      <div class="admin-console__list">
        <article
          v-for="team in adminState.teams"
          :key="team.id"
          class="admin-console__entity"
        >
          <div class="admin-console__entity-main">
            <strong class="admin-console__entity-title">{{ team.name }}</strong>
            <span class="admin-console__entity-meta">{{ team.affiliation || t("common.independent") }}</span>
            <small class="admin-console__entity-copy">
              {{
                t("admin.teamMeta", {
                  count: team.member_count ?? 0,
                  moderation: t(`moderation.${team.moderation_status}`)
                })
              }}
            </small>
          </div>

          <div class="admin-console__actions">
            <span class="tag tag--neutral">{{ team.is_active ? t("admin.active") : t("admin.disabled") }}</span>
            <button
              class="button button--ghost"
              type="button"
              :disabled="isAdminLoading"
              @click="emit('set-team-moderation', team, 'approved')"
            >
              {{ t("admin.approve") }}
            </button>
            <button
              class="button button--ghost"
              type="button"
              :disabled="isAdminLoading"
              @click="emit('set-team-moderation', team, 'pending')"
            >
              {{ t("admin.markPending") }}
            </button>
            <button
              class="button button--ghost"
              type="button"
              :disabled="isAdminLoading"
              @click="emit('set-team-moderation', team, 'suspended')"
            >
              {{ t("admin.suspend") }}
            </button>
            <button
              class="button button--ghost"
              type="button"
              :disabled="isAdminLoading"
              @click="emit('toggle-team', team)"
            >
              {{ team.is_active ? t("admin.disable") : t("admin.enable") }}
            </button>
            <button
              class="button button--ghost button--danger"
              type="button"
              :disabled="isAdminLoading"
              @click="emit('delete-team', team)"
            >
              {{ t("admin.delete") }}
            </button>
          </div>
        </article>
      </div>
    </article>

    <article class="panel-card admin-console__panel">
      <div class="panel-card__header">
        <div>
          <p class="panel-card__kicker">{{ t("admin.servicesKicker") }}</p>
          <h2 class="panel-card__title">{{ t("admin.servicesTitle") }}</h2>
        </div>
      </div>

      <form class="form-stack" @submit.prevent="emit('create-service')">
        <div class="field-grid">
          <label class="field">
            <span class="field__label">{{ t("admin.name") }}</span>
            <input v-model="adminServiceForm.name" class="field__control" type="text" />
          </label>

          <label class="field">
            <span class="field__label">{{ t("admin.port") }}</span>
            <input v-model="adminServiceForm.port" class="field__control" type="number" min="1" />
          </label>

          <label class="field field--full">
            <span class="field__label">{{ t("admin.description") }}</span>
            <input v-model="adminServiceForm.description" class="field__control" type="text" />
          </label>
        </div>

        <button class="button" type="submit" :disabled="isAdminLoading">
          {{ isAdminLoading ? t("workspace.saving") : t("admin.createService") }}
        </button>
      </form>

      <div class="admin-console__list">
        <article
          v-for="service in adminState.services"
          :key="service.id"
          class="admin-console__entity"
        >
          <div class="admin-console__entity-main">
            <strong class="admin-console__entity-title">{{ service.name }}</strong>
            <span class="admin-console__entity-meta">
              {{ service.port ? `${t("admin.port")} ${service.port}` : t("admin.portUnset") }}
            </span>
            <small class="admin-console__entity-copy">
              {{ t("admin.serviceGeneratedFlags", { count: service.flag_count ?? 0 }) }}
            </small>
          </div>

          <div class="admin-console__actions">
            <span class="tag tag--neutral">{{ service.is_active ? t("admin.active") : t("admin.disabled") }}</span>
            <button
              class="button button--ghost"
              type="button"
              :disabled="isAdminLoading"
              @click="emit('toggle-service', service)"
            >
              {{ service.is_active ? t("admin.disable") : t("admin.enable") }}
            </button>
            <button
              class="button button--ghost button--danger"
              type="button"
              :disabled="isAdminLoading"
              @click="emit('delete-service', service)"
            >
              {{ t("admin.delete") }}
            </button>
          </div>
        </article>
      </div>
    </article>

    <article class="panel-card admin-console__panel admin-console__panel--wide">
      <div class="panel-card__header">
        <div>
          <p class="panel-card__kicker">{{ t("admin.roundsKicker") }}</p>
          <h2 class="panel-card__title">{{ t("admin.roundsTitle") }}</h2>
        </div>
        <span class="panel-card__note">
          {{ t("admin.nextSuggestedRound", { number: adminState.next_round_number }) }}
        </span>
      </div>

      <form class="form-stack" @submit.prevent="emit('create-round')">
        <div class="admin-console__checker">
          <div class="admin-console__checker-copy">
            <strong class="admin-console__checker-title">
              {{
                adminRunningRound
                  ? t("admin.runningRoundReady", { number: adminRunningRound.number })
                  : t("admin.noRunningRound")
              }}
            </strong>
            <span class="admin-console__checker-meta">
              {{
                adminState.latest_checker_report_at
                  ? t("admin.lastCheckerReport", {
                      date: formatDateTime(adminState.latest_checker_report_at)
                    })
                  : t("admin.noCheckerReport")
              }}
            </span>
          </div>

          <button
            class="button button--secondary"
            type="button"
            :disabled="isAdminLoading || !adminRunningRound"
            @click="emit('run-checker-tick')"
          >
            {{ isAdminLoading ? t("admin.working") : t("admin.runCheckerTick") }}
          </button>
        </div>

        <div class="admin-console__checker-summary">
          <article
            v-for="card in checkerStatusCards"
            :key="card.key"
            class="admin-console__checker-card"
            :data-state="card.key"
          >
            <span class="admin-console__checker-label">{{ card.label }}</span>
            <strong class="admin-console__checker-value">{{ card.value }}</strong>
          </article>
        </div>

        <div class="field-grid">
          <label class="field">
            <span class="field__label">{{ t("admin.roundNumber") }}</span>
            <input
              v-model="adminRoundForm.number"
              class="field__control"
              type="number"
              min="1"
              :placeholder="String(adminState.next_round_number || 1)"
            />
          </label>

          <label class="field">
            <span class="field__label">{{ t("admin.scheduleCount") }}</span>
            <input
              v-model="adminScheduleForm.count"
              class="field__control"
              type="number"
              min="1"
              max="10"
            />
          </label>

          <label class="field">
            <span class="field__label">{{ t("admin.scheduleStart") }}</span>
            <input
              v-model="adminScheduleForm.start_at"
              class="field__control"
              type="datetime-local"
            />
          </label>
        </div>

        <div class="admin-console__form-actions">
          <button class="button" type="submit" :disabled="isAdminLoading">
            {{ isAdminLoading ? t("workspace.saving") : t("admin.createPlannedRound") }}
          </button>
          <button
            class="button button--secondary"
            type="button"
            :disabled="isAdminLoading"
            @click="emit('schedule-rounds')"
          >
            {{ isAdminLoading ? t("workspace.saving") : t("admin.scheduleBatch") }}
          </button>
        </div>
      </form>

      <div class="admin-console__list">
        <article
          v-for="round in adminState.rounds"
          :key="round.id"
          class="admin-console__entity"
        >
          <div class="admin-console__entity-main">
            <strong class="admin-console__entity-title">{{ t("common.roundLabel", { number: round.number }) }}</strong>
            <span class="admin-console__entity-meta">{{ t(`roundState.${round.state}`) }}</span>
            <small class="admin-console__entity-copy">
              {{ t("admin.roundGeneratedFlags", { count: round.flag_count ?? 0 }) }}
            </small>
          </div>

          <div class="admin-console__actions">
            <button
              v-if="round.state === 'planned'"
              class="button button--ghost"
              type="button"
              :disabled="isAdminLoading"
              @click="emit('start-round', round)"
            >
              {{ t("admin.start") }}
            </button>
            <button
              v-if="round.state === 'running'"
              class="button button--ghost"
              type="button"
              :disabled="isAdminLoading"
              @click="emit('finish-round', round)"
            >
              {{ t("admin.finish") }}
            </button>
            <button
              class="button button--ghost"
              type="button"
              :disabled="isAdminLoading"
              @click="emit('generate-flags', round)"
            >
              {{ t("admin.generateFlags") }}
            </button>
          </div>
        </article>
      </div>
    </article>
  </section>
</template>
