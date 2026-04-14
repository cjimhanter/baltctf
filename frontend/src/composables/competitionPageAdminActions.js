import { apiRequest } from "../api";
import {
  createAdminScheduleForm,
  createAdminServiceForm,
  createAdminTeamForm,
  normalizeDateTimeInput
} from "./competitionPageFactories";

export function createCompetitionPageAdminActions(context) {
  async function runAdminAction(path, body = {}, options = {}) {
    const { refreshServiceMatrix = false, successMessage = "" } = options;
    context.resetAdminMessage();

    return context.withLoading(context.isAdminLoading, async () => {
      try {
        const payload = await apiRequest(path, {
          method: "POST",
          token: context.token.value,
          body
        });

        if (payload.admin_state) {
          context.applyAdminState(payload.admin_state);
        }

        context.adminMessage.value =
          successMessage ||
          payload.message ||
          context.t("messages.adminActionCompleted");

        const refreshTasks = [
          context.loadDashboard({ refresh: true }),
          context.loadRegistrationSettings()
        ];

        if (refreshServiceMatrix) {
          refreshTasks.push(context.loadServiceStatus());
        }

        await Promise.all(refreshTasks);
        return true;
      } catch (error) {
        context.handleProtectedActionError(
          error,
          context.adminMessage,
          "messages.adminActionFailed"
        );
        return false;
      }
    });
  }

  async function handleAdminTeamCreate() {
    const succeeded = await runAdminAction("/admin/teams/", {
      ...context.adminTeamForm.value
    });

    if (succeeded) {
      context.adminMessage.value = context.t("messages.teamCreated");
      context.adminTeamForm.value = createAdminTeamForm();
    }
  }

  async function setTeamModeration(team, moderationStatus) {
    let moderationNote = team.moderation_note || "";

    if (moderationStatus === "suspended") {
      moderationNote =
        window.prompt(
          context.t("prompts.moderationNote", { name: team.name }),
          team.moderation_note || context.t("moderation.suspended")
        ) ||
        team.moderation_note ||
        context.t("moderation.suspended");
    }

    await runAdminAction(
      `/admin/teams/${team.id}/update/`,
      {
        name: team.name,
        slug: team.slug,
        affiliation: team.affiliation,
        contact_email: team.contact_email,
        is_active: team.is_active,
        moderation_status: moderationStatus,
        moderation_note: moderationNote
      },
      {
        successMessage: context.t("messages.teamUpdated")
      }
    );
  }

  async function handleAdminServiceCreate() {
    const succeeded = await runAdminAction("/admin/services/", {
      name: context.adminServiceForm.value.name,
      description: context.adminServiceForm.value.description,
      port: context.adminServiceForm.value.port
        ? Number(context.adminServiceForm.value.port)
        : null
    });

    if (succeeded) {
      context.adminMessage.value = context.t("messages.serviceCreated");
      context.adminServiceForm.value = createAdminServiceForm();
    }
  }

  async function handleAdminRoundCreate() {
    const succeeded = await runAdminAction("/admin/rounds/", {
      ...(context.adminRoundForm.value.number
        ? { number: Number(context.adminRoundForm.value.number) }
        : {})
    });

    if (succeeded) {
      context.adminMessage.value = context.t("messages.roundCreated");
      context.adminRoundForm.value = { number: "" };
    }
  }

  async function handleAdminSettingsUpdate() {
    const succeeded = await runAdminAction("/admin/settings/update/", {
      registration_open: context.adminSettingsForm.value.registration_open,
      registration_starts_at: normalizeDateTimeInput(
        context.adminSettingsForm.value.registration_starts_at
      ),
      registration_ends_at: normalizeDateTimeInput(
        context.adminSettingsForm.value.registration_ends_at
      ),
      reservation_required_for_registration:
        context.adminSettingsForm.value.reservation_required_for_registration,
      auto_approve_registrations:
        context.adminSettingsForm.value.auto_approve_registrations,
      round_duration_minutes: Number(
        context.adminSettingsForm.value.round_duration_minutes
      ),
      round_break_minutes: Number(
        context.adminSettingsForm.value.round_break_minutes
      )
    });

    if (succeeded) {
      context.adminMessage.value = context.t("messages.competitionSettingsUpdated");
    }
  }

  async function handleAdminRoundSchedule() {
    const succeeded = await runAdminAction("/admin/rounds/schedule/", {
      count: Number(context.adminScheduleForm.value.count),
      start_at: normalizeDateTimeInput(context.adminScheduleForm.value.start_at)
    });

    if (succeeded) {
      context.adminMessage.value = context.t("messages.roundsScheduled");
      context.adminScheduleForm.value = createAdminScheduleForm();
    }
  }

  async function approveReservation(reservation) {
    const succeeded = await runAdminAction(
      `/admin/reservations/${reservation.id}/approve/`
    );

    if (succeeded) {
      context.adminMessage.value = context.t("messages.reservationApproved");
    }
  }

  async function rejectReservation(reservation) {
    const note = window.prompt(
      context.t("prompts.rejectReservation", { name: reservation.name }),
      reservation.note || ""
    );

    if (note === null) {
      return false;
    }

    const succeeded = await runAdminAction(
      `/admin/reservations/${reservation.id}/reject/`,
      {
        note
      }
    );

    if (succeeded) {
      context.adminMessage.value = context.t("messages.reservationRejected");
    }
  }

  async function toggleTeamActive(team) {
    await runAdminAction(
      `/admin/teams/${team.id}/update/`,
      {
        name: team.name,
        slug: team.slug,
        affiliation: team.affiliation,
        contact_email: team.contact_email,
        is_active: !team.is_active,
        moderation_status: team.moderation_status,
        moderation_note: team.moderation_note
      },
      {
        successMessage: context.t("messages.teamUpdated")
      }
    );
  }

  async function deleteTeam(team) {
    if (!window.confirm(context.t("prompts.deleteTeam", { name: team.name }))) {
      return false;
    }

    return runAdminAction(`/admin/teams/${team.id}/delete/`);
  }

  async function toggleServiceActive(service) {
    await runAdminAction(
      `/admin/services/${service.id}/update/`,
      {
        name: service.name,
        slug: service.slug,
        description: service.description,
        port: service.port,
        is_active: !service.is_active
      },
      {
        successMessage: context.t("messages.serviceUpdated")
      }
    );
  }

  async function deleteService(service) {
    if (
      !window.confirm(context.t("prompts.deleteService", { name: service.name }))
    ) {
      return false;
    }

    return runAdminAction(`/admin/services/${service.id}/delete/`);
  }

  async function startRound(round) {
    return runAdminAction(`/admin/rounds/${round.id}/start/`, {}, {
      refreshServiceMatrix: true,
      successMessage: context.t("messages.roundStarted")
    });
  }

  async function finishRound(round) {
    return runAdminAction(`/admin/rounds/${round.id}/finish/`, {}, {
      refreshServiceMatrix: true,
      successMessage: context.t("messages.roundFinished")
    });
  }

  async function generateFlags(round) {
    return runAdminAction(`/admin/rounds/${round.id}/generate-flags/`, {}, {
      refreshServiceMatrix: true,
      successMessage: context.t("messages.flagsGenerated")
    });
  }

  async function runCheckerTick() {
    return runAdminAction("/admin/checker/tick/", {}, {
      refreshServiceMatrix: true,
      successMessage: context.t("messages.checkerTickCompleted")
    });
  }

  return {
    handleAdminTeamCreate,
    setTeamModeration,
    handleAdminServiceCreate,
    handleAdminRoundCreate,
    handleAdminSettingsUpdate,
    handleAdminRoundSchedule,
    approveReservation,
    rejectReservation,
    toggleTeamActive,
    deleteTeam,
    toggleServiceActive,
    deleteService,
    startRound,
    finishRound,
    generateFlags,
    runCheckerTick
  };
}
