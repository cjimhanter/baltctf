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
    <article class="panel-card guest-access__panel guest-access__panel--reservation">
      <div class="panel-card__header">
        <div>
          <p class="panel-card__kicker">{{ t("guest.reservationKicker") }}</p>
          <h2 class="panel-card__title">{{ t("guest.reservationTitle") }}</h2>
        </div>
        <span class="panel-card__note">
          {{
            registrationSettings.registration_available
              ? t("guest.windowOpen")
              : t("guest.windowClosed")
          }}
        </span>
      </div>

      <div class="guest-access__status-note">
        <p>
          {{
            registrationSettings.reservation_required_for_registration
              ? t("guest.reservationRequired")
              : t("guest.reservationOptional")
          }}
        </p>
      </div>

      <form class="form-stack" @submit.prevent="emit('reserve-team-name')">
        <div class="field-grid">
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

    <article class="panel-card guest-access__panel guest-access__panel--login">
      <div class="panel-card__header">
        <div>
          <p class="panel-card__kicker">{{ t("guest.authKicker") }}</p>
          <h2 class="panel-card__title">{{ t("guest.signInTitle") }}</h2>
        </div>
      </div>

      <form class="form-stack" @submit.prevent="emit('login')">
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

    <article class="panel-card guest-access__panel guest-access__panel--register">
      <div class="panel-card__header">
        <div>
          <p class="panel-card__kicker">{{ t("guest.registrationKicker") }}</p>
          <h2 class="panel-card__title">{{ t("guest.createTeamTitle") }}</h2>
        </div>
        <span class="panel-card__note">
          {{ t("guest.maxMembers", { count: maxTeamMembers }) }}
        </span>
      </div>

      <div class="guest-access__status-note">
        <p v-if="!registrationSettings.registration_available">
          {{ t("guest.registrationClosedHint") }}
        </p>
        <p v-else-if="registrationSettings.reservation_required_for_registration">
          {{ t("guest.reservationTokenRequiredHint") }}
        </p>
      </div>

      <form class="form-stack" @submit.prevent="emit('register')">
        <div class="field-grid">
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

        <div class="guest-access__subsection">
          <div class="guest-access__subsection-head">
            <h3 class="guest-access__subsection-title">{{ t("guest.captain") }}</h3>
          </div>

          <div class="field-grid">
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

        <div class="guest-access__subsection">
          <div class="guest-access__subsection-head">
            <h3 class="guest-access__subsection-title">{{ t("guest.participants") }}</h3>
            <button
              class="button button--ghost"
              type="button"
              :disabled="!canAddParticipant"
              @click="emit('add-participant')"
            >
              {{ t("guest.addParticipant") }}
            </button>
          </div>

          <div
            v-if="registerForm.participants.length === 0"
            class="empty-hint"
          >
            {{ t("guest.participantsHint") }}
          </div>

          <article
            v-for="(participant, index) in registerForm.participants"
            :key="index"
            class="guest-access__participant"
          >
            <div class="guest-access__participant-head">
              <strong class="guest-access__participant-title">
                {{ t("guest.playerLabel", { index: index + 1 }) }}
              </strong>
              <button
                class="button button--ghost button--danger"
                type="button"
                @click="emit('remove-participant', index)"
              >
                {{ t("guest.remove") }}
              </button>
            </div>

            <div class="field-grid">
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
          class="button"
          type="submit"
          :disabled="isAuthLoading || !registrationSettings.registration_available"
        >
          {{ isAuthLoading ? t("guest.creatingTeam") : t("guest.registerTeam") }}
        </button>
      </form>
    </article>
  </section>
</template>
