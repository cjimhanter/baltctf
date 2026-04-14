import { clearStoredToken, writeStoredToken } from "../api";
import {
  createBlankParticipant,
  createEmptyAdminState,
  createEmptyRegistrationSettings,
  createEmptySession,
  toDateTimeInputValue
} from "./competitionPageFactories";

export function createCompetitionPageMutations(context) {
  function syncTeamFormsFromSession() {
    context.teamProfileForm.value = {
      affiliation: context.session.value.team?.affiliation || "",
      contact_email: context.session.value.team?.contact_email || ""
    };
    context.teamMemberForm.value = createBlankParticipant();
  }

  function syncAdminFormsFromState() {
    const settings =
      context.adminState.value.settings || createEmptyRegistrationSettings();

    context.adminSettingsForm.value = {
      registration_open: settings.registration_open,
      registration_starts_at: toDateTimeInputValue(settings.registration_starts_at),
      registration_ends_at: toDateTimeInputValue(settings.registration_ends_at),
      reservation_required_for_registration:
        settings.reservation_required_for_registration,
      auto_approve_registrations: settings.auto_approve_registrations,
      round_duration_minutes: settings.round_duration_minutes,
      round_break_minutes: settings.round_break_minutes
    };
  }

  function clearMessages(...messageRefs) {
    messageRefs.forEach((messageRef) => {
      messageRef.value = "";
    });
  }

  function resetAuthMessages() {
    clearMessages(
      context.authMessage,
      context.submissionMessage,
      context.reservationMessage
    );
  }

  function resetAdminMessage() {
    context.adminMessage.value = "";
  }

  function resetTeamMessage() {
    context.teamMessage.value = "";
  }

  function getErrorMessage(error, fallbackMessage) {
    return error instanceof Error ? error.message : fallbackMessage;
  }

  async function withLoading(loadingRef, callback) {
    if (loadingRef.value) {
      return false;
    }

    loadingRef.value = true;

    try {
      return await callback();
    } finally {
      loadingRef.value = false;
    }
  }

  function clearAuthState() {
    clearStoredToken();
    context.token.value = "";
    context.session.value = createEmptySession();
    context.isSessionReady.value = true;
    syncTeamFormsFromSession();

    context.adminState.value = createEmptyAdminState();
    context.isAdminStateReady.value = true;
    syncAdminFormsFromState();
  }

  function expireSession() {
    clearAuthState();
    clearMessages(context.adminMessage, context.teamMessage, context.submissionMessage);
    context.authMessage.value = context.t("messages.sessionExpired");
  }

  function applyAuthenticatedState(payload) {
    if (payload.token) {
      context.token.value = payload.token;
      writeStoredToken(payload.token);
    }

    context.session.value = {
      authenticated: payload.authenticated,
      user: payload.user,
      team: payload.team,
      membership: payload.membership,
      members: payload.members || [],
      recent_submissions: payload.recent_submissions || []
    };
    context.isSessionReady.value = true;
    syncTeamFormsFromSession();

    if (!payload.user?.is_staff) {
      context.adminState.value = createEmptyAdminState();
      context.isAdminStateReady.value = true;
      syncAdminFormsFromState();
    }
  }

  function applyAdminState(payload) {
    context.adminState.value = payload;
    context.isAdminStateReady.value = true;

    if (payload.settings) {
      context.registrationSettings.value = payload.settings;
    }

    syncAdminFormsFromState();
  }

  function handleProtectedActionError(error, targetRef, fallbackKey) {
    if (error?.status === 401) {
      expireSession();
      return true;
    }

    targetRef.value = getErrorMessage(error, context.t(fallbackKey));
    return false;
  }

  return {
    syncTeamFormsFromSession,
    syncAdminFormsFromState,
    clearMessages,
    resetAuthMessages,
    resetAdminMessage,
    resetTeamMessage,
    getErrorMessage,
    withLoading,
    clearAuthState,
    expireSession,
    applyAuthenticatedState,
    applyAdminState,
    handleProtectedActionError
  };
}
