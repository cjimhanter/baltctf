<script setup>
import { useI18n } from "../../i18n";

defineProps({
  loginForm: {
    type: Object,
    required: true
  },
  registerForm: {
    type: Object,
    required: true
  },
  reservationForm: {
    type: Object,
    required: true
  },
  registrationSettings: {
    type: Object,
    required: true
  },
  isAuthLoading: {
    type: Boolean,
    default: false
  },
  isReservationLoading: {
    type: Boolean,
    default: false
  },
  maxTeamMembers: {
    type: Number,
    required: true
  },
  canAddParticipant: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits([
  "login",
  "register",
  "reserve-team-name",
  "add-participant",
  "remove-participant"
]);

const { t } = useI18n();
</script>

<template>
  <section class="guest-access">
    <div class="guest-access__intro">
      <p class="guest-access__panel-kicker">{{ t("guest.accessKicker") }}</p>
      <h2 class="guest-access__panel-title">{{ t("guest.accessTitle") }}</h2>
      <p>{{ t("guest.accessCopy") }}</p>
    </div>

    <article class="panel-card guest-access__panel guest-access__panel--login">
      <div class="guest-access__panel-header">
        <div class="guest-access__panel-copy">
          <p class="guest-access__panel-kicker">{{ t("guest.authKicker") }}</p>
          <h2 class="guest-access__panel-title">{{ t("guest.signInTitle") }}</h2>
        </div>
      </div>

      <form class="guest-access__form guest-access__form--login" @submit.prevent="emit('login')">
        <label class="field">
          <span class="field__label">{{ t("guest.username") }}</span>
          <input
            v-model="loginForm.username"
            class="field__control"
            type="text"
            autocomplete="username"
          />
        </label>

        <label class="field">
          <span class="field__label">{{ t("guest.password") }}</span>
          <input
            v-model="loginForm.password"
            class="field__control"
            type="password"
            autocomplete="current-password"
          />
        </label>

        <button class="button" type="submit" :disabled="isAuthLoading">
          {{ isAuthLoading ? t("guest.signingIn") : t("guest.signIn") }}
        </button>
      </form>
    </article>

    <article class="panel-card guest-access__panel guest-access__panel--reservation">
      <div class="guest-access__panel-header">
        <div class="guest-access__panel-copy">
          <p class="guest-access__panel-kicker">{{ t("guest.reservationKicker") }}</p>
          <h2 class="guest-access__panel-title">{{ t("guest.reservationTitle") }}</h2>
        </div>
        <span class="guest-access__panel-note">
          {{
            registrationSettings.registration_available
              ? t("guest.windowOpen")
              : t("guest.windowClosed")
          }}
        </span>
      </div>

      <div class="guest-access__status-card">
        <p class="guest-access__status-copy">
          {{
            registrationSettings.reservation_required_for_registration
              ? t("guest.reservationRequired")
              : t("guest.reservationOptional")
          }}
        </p>
      </div>

      <form class="guest-access__form" @submit.prevent="emit('reserve-team-name')">
        <div class="guest-access__fields">
          <label class="field">
            <span class="field__label">{{ t("guest.teamName") }}</span>
            <input v-model="reservationForm.team_name" class="field__control" type="text" />
          </label>

          <label class="field">
            <span class="field__label">{{ t("guest.preferredSlug") }}</span>
            <input v-model="reservationForm.team_slug" class="field__control" type="text" />
          </label>

          <label class="field">
            <span class="field__label">{{ t("guest.captainUsername") }}</span>
            <input
              v-model="reservationForm.captain_username"
              class="field__control"
              type="text"
            />
          </label>

          <label class="field">
            <span class="field__label">{{ t("guest.contactEmail") }}</span>
            <input
              v-model="reservationForm.contact_email"
              class="field__control"
              type="email"
            />
          </label>
        </div>

        <button
          class="button button--secondary"
          type="submit"
          :disabled="isReservationLoading || !registrationSettings.registration_available"
        >
          {{
            isReservationLoading
              ? t("guest.submitting")
              : t("guest.requestReservation")
          }}
        </button>
      </form>
    </article>

    <article class="panel-card guest-access__panel guest-access__panel--register">
      <div class="guest-access__panel-header">
        <div class="guest-access__panel-copy">
          <p class="guest-access__panel-kicker">{{ t("guest.registrationKicker") }}</p>
          <h2 class="guest-access__panel-title">{{ t("guest.createTeamTitle") }}</h2>
        </div>
        <span class="guest-access__panel-note">
          {{ t("guest.maxMembers", { count: maxTeamMembers }) }}
        </span>
      </div>

      <div class="guest-access__status-card">
        <p v-if="!registrationSettings.registration_available" class="guest-access__status-copy">
          {{ t("guest.registrationClosedHint") }}
        </p>
        <p
          v-else-if="registrationSettings.reservation_required_for_registration"
          class="guest-access__status-copy"
        >
          {{ t("guest.reservationTokenRequiredHint") }}
        </p>
      </div>

      <form class="guest-access__form" @submit.prevent="emit('register')">
        <div class="guest-access__fields">
          <label class="field">
            <span class="field__label">{{ t("guest.teamName") }}</span>
            <input v-model="registerForm.team_name" class="field__control" type="text" />
          </label>

          <label class="field">
            <span class="field__label">{{ t("guest.teamSlug") }}</span>
            <input v-model="registerForm.team_slug" class="field__control" type="text" />
          </label>

          <label class="field">
            <span class="field__label">{{ t("guest.affiliation") }}</span>
            <input v-model="registerForm.affiliation" class="field__control" type="text" />
          </label>

          <label class="field">
            <span class="field__label">{{ t("guest.contactEmail") }}</span>
            <input v-model="registerForm.contact_email" class="field__control" type="email" />
          </label>

          <label class="field field--full">
            <span class="field__label">{{ t("guest.reservationToken") }}</span>
            <input
              v-model="registerForm.reservation_token"
              class="field__control"
              type="text"
              :placeholder="t('guest.reservationTokenPlaceholder')"
            />
          </label>
        </div>

        <div class="guest-access__section guest-access__section--captain">
          <div class="guest-access__section-head">
            <h3 class="guest-access__section-title">{{ t("guest.captain") }}</h3>
          </div>

          <div class="guest-access__fields">
            <label class="field">
              <span class="field__label">{{ t("guest.username") }}</span>
              <input v-model="registerForm.captain.username" class="field__control" type="text" />
            </label>

            <label class="field">
              <span class="field__label">{{ t("guest.password") }}</span>
              <input
                v-model="registerForm.captain.password"
                class="field__control"
                type="password"
              />
            </label>

            <label class="field">
              <span class="field__label">{{ t("guest.email") }}</span>
              <input v-model="registerForm.captain.email" class="field__control" type="email" />
            </label>

            <label class="field">
              <span class="field__label">{{ t("guest.firstName") }}</span>
              <input
                v-model="registerForm.captain.first_name"
                class="field__control"
                type="text"
              />
            </label>

            <label class="field">
              <span class="field__label">{{ t("guest.lastName") }}</span>
              <input
                v-model="registerForm.captain.last_name"
                class="field__control"
                type="text"
              />
            </label>
          </div>
        </div>

        <div class="guest-access__section guest-access__section--participants">
          <div class="guest-access__section-head">
            <h3 class="guest-access__section-title">{{ t("guest.participants") }}</h3>
            <button
              class="button button--ghost guest-access__section-action"
              type="button"
              :disabled="!canAddParticipant || isAuthLoading"
              @click="emit('add-participant')"
            >
              {{ t("guest.addParticipant") }}
            </button>
          </div>

          <div
            v-if="registerForm.participants.length === 0"
            class="guest-access__empty"
          >
            {{ t("guest.participantsHint") }}
          </div>

          <article
            v-for="(participant, index) in registerForm.participants"
            :key="index"
            class="guest-access__participant"
          >
            <div class="guest-access__participant-header">
              <strong class="guest-access__participant-title">
                {{ t("guest.playerLabel", { index: index + 1 }) }}
              </strong>
              <button
                class="button button--ghost button--danger guest-access__participant-remove"
                type="button"
                @click="emit('remove-participant', index)"
              >
                {{ t("guest.remove") }}
              </button>
            </div>

            <div class="guest-access__participant-fields">
              <label class="field">
                <span class="field__label">{{ t("guest.username") }}</span>
                <input v-model="participant.username" class="field__control" type="text" />
              </label>

              <label class="field">
                <span class="field__label">{{ t("guest.password") }}</span>
                <input v-model="participant.password" class="field__control" type="password" />
              </label>

              <label class="field">
                <span class="field__label">{{ t("guest.email") }}</span>
                <input v-model="participant.email" class="field__control" type="email" />
              </label>

              <label class="field">
                <span class="field__label">{{ t("guest.firstName") }}</span>
                <input v-model="participant.first_name" class="field__control" type="text" />
              </label>

              <label class="field">
                <span class="field__label">{{ t("guest.lastName") }}</span>
                <input v-model="participant.last_name" class="field__control" type="text" />
              </label>
            </div>
          </article>
        </div>

        <button
          class="button guest-access__submit"
          type="submit"
          :disabled="isAuthLoading || !registrationSettings.registration_available"
        >
          {{ isAuthLoading ? t("guest.creatingTeam") : t("guest.registerTeam") }}
        </button>
      </form>
    </article>
  </section>
</template>
