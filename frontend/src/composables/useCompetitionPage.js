import { computed, onMounted, ref } from "vue";

import {
  apiRequest,
  clearStoredToken,
  readStoredToken,
  writeStoredToken
} from "../api";
import { useI18n } from "../i18n";

export const MAX_TEAM_MEMBERS = 6;

function createEmptyDashboard() {
  return {
    summary: {
      team_count: 0,
      service_count: 0,
      round_count: 0,
      accepted_submissions_count: 0,
      registered_users_count: 0
    },
    current_round: null,
    services: [],
    scoreboard: [],
    recent_rounds: [],
    recent_activity: []
  };
}

function createEmptyServiceStatus() {
  return {
    current_round: null,
    services: [],
    teams: []
  };
}

function createEmptySession() {
  return {
    authenticated: false,
    user: null,
    team: null,
    membership: null,
    members: [],
    recent_submissions: []
  };
}

function createEmptyAdminState() {
  return {
    settings: {
      registration_open: true,
      registration_starts_at: null,
      registration_ends_at: null,
      reservation_required_for_registration: false,
      auto_approve_registrations: true,
      round_duration_minutes: 15,
      round_break_minutes: 5,
      registration_available: true
    },
    reservations: [],
    teams: [],
    services: [],
    rounds: [],
    current_round: null,
    current_status_summary: {},
    latest_checker_report_at: null,
    next_round_number: 1
  };
}

function createEmptyRegistrationSettings() {
  return {
    registration_open: true,
    registration_starts_at: null,
    registration_ends_at: null,
    reservation_required_for_registration: false,
    auto_approve_registrations: true,
    round_duration_minutes: 15,
    round_break_minutes: 5,
    registration_available: true
  };
}

function createBlankParticipant() {
  return {
    username: "",
    password: "",
    email: "",
    first_name: "",
    last_name: ""
  };
}

function createRegisterForm() {
  return {
    team_name: "",
    team_slug: "",
    affiliation: "",
    contact_email: "",
    reservation_token: "",
    captain: createBlankParticipant(),
    participants: []
  };
}

function createReservationForm() {
  return {
    team_name: "",
    team_slug: "",
    captain_username: "",
    contact_email: ""
  };
}

function createTeamProfileForm() {
  return {
    affiliation: "",
    contact_email: ""
  };
}

function createAdminSettingsForm() {
  return {
    registration_open: true,
    registration_starts_at: "",
    registration_ends_at: "",
    reservation_required_for_registration: false,
    auto_approve_registrations: true,
    round_duration_minutes: 15,
    round_break_minutes: 5
  };
}

function createAdminScheduleForm() {
  return {
    count: 2,
    start_at: ""
  };
}

function toDateTimeInputValue(value) {
  if (!value) {
    return "";
  }

  const date = new Date(value);
  const offsetMilliseconds = date.getTimezoneOffset() * 60_000;
  return new Date(date.getTime() - offsetMilliseconds).toISOString().slice(0, 16);
}

function normalizeDateTimeInput(value) {
  if (!value) {
    return null;
  }

  return value.length === 16 ? `${value}:00` : value;
}

export function useCompetitionPage() {
  const { t, formatDateTime } = useI18n();
  const dashboard = ref(createEmptyDashboard());
  const serviceStatus = ref(createEmptyServiceStatus());
  const adminState = ref(createEmptyAdminState());
  const registrationSettings = ref(createEmptyRegistrationSettings());
  const session = ref(createEmptySession());

  const apiErrorMessage = ref("");
  const authMessage = ref("");
  const adminMessage = ref("");
  const teamMessage = ref("");
  const submissionMessage = ref("");
  const reservationMessage = ref("");

  const isLoading = ref(true);
  const isRefreshing = ref(false);
  const isAuthLoading = ref(false);
  const isAdminLoading = ref(false);
  const isTeamActionLoading = ref(false);
  const isSubmittingFlag = ref(false);
  const isReservationLoading = ref(false);
  const isServiceStatusLoading = ref(false);

  const token = ref(readStoredToken());

  const loginForm = ref({
    username: "",
    password: ""
  });
  const registerForm = ref(createRegisterForm());
  const reservationForm = ref(createReservationForm());
  const flagForm = ref({ flag: "" });
  const teamProfileForm = ref(createTeamProfileForm());
  const teamMemberForm = ref(createBlankParticipant());
  const adminTeamForm = ref({
    name: "",
    affiliation: "",
    contact_email: ""
  });
  const adminServiceForm = ref({
    name: "",
    description: "",
    port: ""
  });
  const adminRoundForm = ref({
    number: ""
  });
  const adminSettingsForm = ref(createAdminSettingsForm());
  const adminScheduleForm = ref(createAdminScheduleForm());

  const summaryCards = computed(() => [
    {
      label: t("dashboard.metrics.teams"),
      value: dashboard.value.summary.team_count,
      note: t("dashboard.metrics.teamsNote")
    },
    {
      label: t("dashboard.metrics.users"),
      value: dashboard.value.summary.registered_users_count,
      note: t("dashboard.metrics.usersNote")
    },
    {
      label: t("dashboard.metrics.services"),
      value: dashboard.value.summary.service_count,
      note: t("dashboard.metrics.servicesNote")
    },
    {
      label: t("dashboard.metrics.rounds"),
      value: dashboard.value.summary.round_count,
      note: t("dashboard.metrics.roundsNote")
    },
    {
      label: t("dashboard.metrics.acceptedFlags"),
      value: dashboard.value.summary.accepted_submissions_count,
      note: t("dashboard.metrics.acceptedFlagsNote")
    }
  ]);

  const currentRoundTitle = computed(() => {
    if (!dashboard.value.current_round) {
      return t("dashboard.waitingRound");
    }

    return t("common.roundLabel", { number: dashboard.value.current_round.number });
  });

  const currentRoundMeta = computed(() => {
    if (!dashboard.value.current_round) {
      return t("dashboard.waitingRoundMeta");
    }

    return t("common.since", {
      state: t(`roundState.${dashboard.value.current_round.state}`),
      date: formatDateTime(dashboard.value.current_round.started_at)
    });
  });

  const hasScoreboard = computed(() => dashboard.value.scoreboard.length > 0);
  const leaderboardLeader = computed(() => dashboard.value.scoreboard[0] || null);
  const recentRounds = computed(() => dashboard.value.recent_rounds.slice(0, 5));
  const hasTeam = computed(() => Boolean(session.value.team));
  const isAdmin = computed(() => Boolean(session.value.user?.is_staff));
  const isCaptain = computed(() => session.value.membership?.role === "captain");
  const isRegistrationAvailable = computed(
    () => registrationSettings.value.registration_available
  );
  const adminRunningRound = computed(
    () => adminState.value.rounds.find((round) => round.state === "running") || null
  );
  const checkerStatusCards = computed(() => {
    const summary = adminState.value.current_status_summary || {};

    return [
      { key: "up", label: t("serviceState.up"), value: summary.up || 0 },
      { key: "mumble", label: t("serviceState.mumble"), value: summary.mumble || 0 },
      { key: "corrupt", label: t("serviceState.corrupt"), value: summary.corrupt || 0 },
      { key: "down", label: t("serviceState.down"), value: summary.down || 0 }
    ];
  });
  const canAddParticipant = computed(
    () => registerForm.value.participants.length + 1 < MAX_TEAM_MEMBERS
  );
  const canAddTeamMember = computed(
    () => session.value.members.length < MAX_TEAM_MEMBERS
  );

  function syncTeamFormsFromSession() {
    teamProfileForm.value = {
      affiliation: session.value.team?.affiliation || "",
      contact_email: session.value.team?.contact_email || ""
    };
    teamMemberForm.value = createBlankParticipant();
  }

  function syncAdminFormsFromState() {
    const settings = adminState.value.settings || createEmptyRegistrationSettings();
    adminSettingsForm.value = {
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

  function applyAuthenticatedState(payload) {
    if (payload.token) {
      token.value = payload.token;
      writeStoredToken(payload.token);
    }

    session.value = {
      authenticated: payload.authenticated,
      user: payload.user,
      team: payload.team,
      membership: payload.membership,
      members: payload.members || [],
      recent_submissions: payload.recent_submissions || []
    };
    syncTeamFormsFromSession();
  }

  function applyAdminState(payload) {
    adminState.value = payload;
    if (payload.settings) {
      registrationSettings.value = payload.settings;
    }
    syncAdminFormsFromState();
  }

  function resetAuthMessages() {
    authMessage.value = "";
    submissionMessage.value = "";
    reservationMessage.value = "";
  }

  function resetAdminMessage() {
    adminMessage.value = "";
  }

  function resetTeamMessage() {
    teamMessage.value = "";
  }

  async function loadDashboard({ refresh = false } = {}) {
    apiErrorMessage.value = "";

    if (refresh) {
      isRefreshing.value = true;
    } else {
      isLoading.value = true;
    }

    try {
      dashboard.value = await apiRequest("/dashboard/");
    } catch (error) {
      apiErrorMessage.value =
        error instanceof Error
          ? error.message
          : t("messages.dashboardLoadFailed");
    } finally {
      isLoading.value = false;
      isRefreshing.value = false;
    }
  }

  async function loadServiceStatus() {
    isServiceStatusLoading.value = true;

    try {
      serviceStatus.value = await apiRequest("/service-status/");
    } catch (error) {
      apiErrorMessage.value =
        error instanceof Error
          ? error.message
          : t("messages.servicesLoadFailed");
    } finally {
      isServiceStatusLoading.value = false;
    }
  }

  async function loadRegistrationSettings() {
    try {
      registrationSettings.value = await apiRequest("/registration/settings/");
    } catch (error) {
      reservationMessage.value =
        error instanceof Error
          ? error.message
          : t("messages.registrationSettingsFailed");
    }
  }

  async function loadSession() {
    if (!token.value) {
      session.value = createEmptySession();
      syncTeamFormsFromSession();
      adminState.value = createEmptyAdminState();
      return;
    }

    try {
      const payload = await apiRequest("/auth/me/", { token: token.value });

      if (!payload.authenticated) {
        clearStoredToken();
        token.value = "";
        session.value = createEmptySession();
        syncTeamFormsFromSession();
        adminState.value = createEmptyAdminState();
        return;
      }

      session.value = payload;
      syncTeamFormsFromSession();
      if (!payload.user?.is_staff) {
        adminState.value = createEmptyAdminState();
      }
    } catch (error) {
      authMessage.value =
        error instanceof Error ? error.message : t("messages.authRestoreFailed");
    }
  }

  async function loadAdminState() {
    if (!token.value || !isAdmin.value) {
      adminState.value = createEmptyAdminState();
      return;
    }

    isAdminLoading.value = true;

    try {
      const payload = await apiRequest("/admin/state/", { token: token.value });
      applyAdminState(payload);
    } catch (error) {
      adminMessage.value =
        error instanceof Error ? error.message : t("messages.adminStateFailed");
    } finally {
      isAdminLoading.value = false;
    }
  }

  function addParticipant() {
    if (!canAddParticipant.value) {
      return;
    }

    registerForm.value.participants.push(createBlankParticipant());
  }

  function removeParticipant(index) {
    registerForm.value.participants.splice(index, 1);
  }

  async function handleReservationRequest() {
    reservationMessage.value = "";
    isReservationLoading.value = true;

    try {
      const payload = await apiRequest("/team-reservations/", {
        method: "POST",
        body: reservationForm.value
      });

      const reservation = payload.reservation;
      registerForm.value.team_name = reservation.name;
      registerForm.value.team_slug = reservation.slug;
      registerForm.value.contact_email = reservation.contact_email;
      registerForm.value.reservation_token = reservation.token;
      registerForm.value.captain.username = reservation.captain_username;
      reservationMessage.value = t("messages.reservationCreated");
      await Promise.all([loadRegistrationSettings(), loadAdminState()]);
    } catch (error) {
      reservationMessage.value =
        error instanceof Error ? error.message : t("messages.reservationFailed");
    } finally {
      isReservationLoading.value = false;
    }
  }

  async function handleLogin() {
    resetAuthMessages();
    resetAdminMessage();
    resetTeamMessage();
    isAuthLoading.value = true;

    try {
      const payload = await apiRequest("/auth/login/", {
        method: "POST",
        body: loginForm.value
      });

      applyAuthenticatedState(payload);
      authMessage.value = t("messages.signedInAs", {
        username: payload.user.username
      });
      loginForm.value = { username: "", password: "" };
      await Promise.all([
        loadDashboard({ refresh: true }),
        loadServiceStatus(),
        loadRegistrationSettings(),
        loadSession(),
        loadAdminState()
      ]);
    } catch (error) {
      authMessage.value =
        error instanceof Error ? error.message : t("messages.loginFailed");
    } finally {
      isAuthLoading.value = false;
    }
  }

  async function handleRegister() {
    resetAuthMessages();
    resetAdminMessage();
    resetTeamMessage();
    isAuthLoading.value = true;

    const participantPayload = registerForm.value.participants.filter((participant) =>
      Object.values(participant).some(Boolean)
    );

    try {
      const payload = await apiRequest("/auth/register/", {
        method: "POST",
        body: {
          team_name: registerForm.value.team_name,
          team_slug: registerForm.value.team_slug || undefined,
          affiliation: registerForm.value.affiliation,
          contact_email: registerForm.value.contact_email,
          reservation_token: registerForm.value.reservation_token || undefined,
          captain: registerForm.value.captain,
          participants: participantPayload
        }
      });

      applyAuthenticatedState(payload);
      registerForm.value = createRegisterForm();
      authMessage.value = t("messages.teamRegistered");
      await Promise.all([
        loadDashboard({ refresh: true }),
        loadServiceStatus(),
        loadRegistrationSettings(),
        loadSession(),
        loadAdminState()
      ]);
    } catch (error) {
      authMessage.value =
        error instanceof Error ? error.message : t("messages.registerFailed");
    } finally {
      isAuthLoading.value = false;
    }
  }

  async function handleLogout() {
    resetAuthMessages();
    resetAdminMessage();
    resetTeamMessage();

    try {
      await apiRequest("/auth/logout/", {
        method: "POST",
        token: token.value
      });
    } catch {
      // local cleanup is enough here
    } finally {
      clearStoredToken();
      token.value = "";
      session.value = createEmptySession();
      syncTeamFormsFromSession();
      adminState.value = createEmptyAdminState();
      authMessage.value = t("messages.sessionClosed");
    }
  }

  async function handleFlagSubmit() {
    submissionMessage.value = "";
    isSubmittingFlag.value = true;

    try {
      const payload = await apiRequest("/submit-flag/", {
        method: "POST",
        token: token.value,
        body: {
          flag: flagForm.value.flag
        }
      });

      submissionMessage.value = payload.message || t("messages.flagSubmitted");
      flagForm.value.flag = "";
      await Promise.all([loadDashboard({ refresh: true }), loadSession()]);
    } catch (error) {
      submissionMessage.value =
        error instanceof Error ? error.message : t("messages.flagSubmitFailed");
    } finally {
      isSubmittingFlag.value = false;
    }
  }

  async function handleTeamProfileUpdate() {
    resetTeamMessage();
    isTeamActionLoading.value = true;

    try {
      const payload = await apiRequest("/team/update/", {
        method: "POST",
        token: token.value,
        body: teamProfileForm.value
      });

      applyAuthenticatedState(payload);
      teamMessage.value = t("messages.teamProfileUpdated");
      await loadDashboard({ refresh: true });
    } catch (error) {
      teamMessage.value =
        error instanceof Error ? error.message : t("messages.teamProfileFailed");
    } finally {
      isTeamActionLoading.value = false;
    }
  }

  async function handleTeamMemberAdd() {
    resetTeamMessage();
    isTeamActionLoading.value = true;

    try {
      const payload = await apiRequest("/team/members/", {
        method: "POST",
        token: token.value,
        body: teamMemberForm.value
      });

      applyAuthenticatedState(payload);
      teamMessage.value = t("messages.teamMemberAdded");
      await loadDashboard({ refresh: true });
    } catch (error) {
      teamMessage.value =
        error instanceof Error ? error.message : t("messages.addMemberFailed");
    } finally {
      isTeamActionLoading.value = false;
    }
  }

  async function updateMemberRole(member, role) {
    resetTeamMessage();
    isTeamActionLoading.value = true;

    try {
      const payload = await apiRequest(`/team/members/${member.id}/role/`, {
        method: "POST",
        token: token.value,
        body: { role }
      });

      applyAuthenticatedState(payload);
      teamMessage.value = t("messages.memberRoleUpdated");
    } catch (error) {
      teamMessage.value =
        error instanceof Error ? error.message : t("messages.updateRoleFailed");
    } finally {
      isTeamActionLoading.value = false;
    }
  }

  async function removeMember(member) {
    if (
      !window.confirm(
        t("prompts.removeMember", {
          username: member.username
        })
      )
    ) {
      return;
    }

    resetTeamMessage();
    isTeamActionLoading.value = true;

    try {
      const payload = await apiRequest(`/team/members/${member.id}/remove/`, {
        method: "POST",
        token: token.value
      });

      applyAuthenticatedState(payload);
      teamMessage.value = t("messages.memberRemoved");
      await loadDashboard({ refresh: true });
    } catch (error) {
      teamMessage.value =
        error instanceof Error ? error.message : t("messages.removeMemberFailed");
    } finally {
      isTeamActionLoading.value = false;
    }
  }

  async function runAdminAction(path, body = {}, options = {}) {
    const { refreshServiceMatrix = false, successMessage = "" } = options;
    resetAdminMessage();
    isAdminLoading.value = true;

    try {
      const payload = await apiRequest(path, {
        method: "POST",
        token: token.value,
        body
      });
      if (payload.admin_state) {
        applyAdminState(payload.admin_state);
      }
      adminMessage.value = successMessage || payload.message || t("messages.adminActionCompleted");
      const refreshTasks = [loadDashboard({ refresh: true }), loadRegistrationSettings()];
      if (refreshServiceMatrix) {
        refreshTasks.push(loadServiceStatus());
      }
      await Promise.all(refreshTasks);
      return true;
    } catch (error) {
      adminMessage.value =
        error instanceof Error ? error.message : t("messages.adminActionFailed");
      return false;
    } finally {
      isAdminLoading.value = false;
    }
  }

  async function handleAdminTeamCreate() {
    const succeeded = await runAdminAction("/admin/teams/", {
      ...adminTeamForm.value
    });
    if (succeeded) {
      adminMessage.value = t("messages.teamCreated");
      adminTeamForm.value = {
        name: "",
        affiliation: "",
        contact_email: ""
      };
    }
  }

  async function setTeamModeration(team, moderationStatus) {
    let moderationNote = team.moderation_note || "";

    if (moderationStatus === "suspended") {
      moderationNote = window.prompt(
        t("prompts.moderationNote", { name: team.name }),
        team.moderation_note || t("moderation.suspended")
      ) || team.moderation_note || t("moderation.suspended");
    }

    await runAdminAction(`/admin/teams/${team.id}/update/`, {
      name: team.name,
      slug: team.slug,
      affiliation: team.affiliation,
      contact_email: team.contact_email,
      is_active: team.is_active,
      moderation_status: moderationStatus,
      moderation_note: moderationNote
    }, {
      successMessage: t("messages.teamUpdated")
    });
  }

  async function handleAdminServiceCreate() {
    const succeeded = await runAdminAction("/admin/services/", {
      name: adminServiceForm.value.name,
      description: adminServiceForm.value.description,
      port: adminServiceForm.value.port ? Number(adminServiceForm.value.port) : null
    });
    if (succeeded) {
      adminMessage.value = t("messages.serviceCreated");
      adminServiceForm.value = {
        name: "",
        description: "",
        port: ""
      };
    }
  }

  async function handleAdminRoundCreate() {
    const succeeded = await runAdminAction("/admin/rounds/", {
      ...(adminRoundForm.value.number
        ? { number: Number(adminRoundForm.value.number) }
        : {})
    });
    if (succeeded) {
      adminMessage.value = t("messages.roundCreated");
      adminRoundForm.value = { number: "" };
    }
  }

  async function handleAdminSettingsUpdate() {
    const succeeded = await runAdminAction("/admin/settings/update/", {
      registration_open: adminSettingsForm.value.registration_open,
      registration_starts_at: normalizeDateTimeInput(
        adminSettingsForm.value.registration_starts_at
      ),
      registration_ends_at: normalizeDateTimeInput(
        adminSettingsForm.value.registration_ends_at
      ),
      reservation_required_for_registration:
        adminSettingsForm.value.reservation_required_for_registration,
      auto_approve_registrations: adminSettingsForm.value.auto_approve_registrations,
      round_duration_minutes: Number(adminSettingsForm.value.round_duration_minutes),
      round_break_minutes: Number(adminSettingsForm.value.round_break_minutes)
    });
    if (succeeded) {
      adminMessage.value = t("messages.competitionSettingsUpdated");
    }
  }

  async function handleAdminRoundSchedule() {
    const succeeded = await runAdminAction("/admin/rounds/schedule/", {
      count: Number(adminScheduleForm.value.count),
      start_at: normalizeDateTimeInput(adminScheduleForm.value.start_at)
    });
    if (succeeded) {
      adminMessage.value = t("messages.roundsScheduled");
      adminScheduleForm.value = createAdminScheduleForm();
    }
  }

  async function approveReservation(reservation) {
    const succeeded = await runAdminAction(`/admin/reservations/${reservation.id}/approve/`);
    if (succeeded) {
      adminMessage.value = t("messages.reservationApproved");
    }
  }

  async function rejectReservation(reservation) {
    const note = window.prompt(
      t("prompts.rejectReservation", { name: reservation.name }),
      reservation.note || ""
    );
    if (note === null) {
      return;
    }

    const succeeded = await runAdminAction(`/admin/reservations/${reservation.id}/reject/`, {
      note
    });
    if (succeeded) {
      adminMessage.value = t("messages.reservationRejected");
    }
  }

  async function toggleTeamActive(team) {
    await runAdminAction(`/admin/teams/${team.id}/update/`, {
      name: team.name,
      slug: team.slug,
      affiliation: team.affiliation,
      contact_email: team.contact_email,
      is_active: !team.is_active,
      moderation_status: team.moderation_status,
      moderation_note: team.moderation_note
    }, {
      successMessage: t("messages.teamUpdated")
    });
  }

  async function deleteTeam(team) {
    if (!window.confirm(t("prompts.deleteTeam", { name: team.name }))) {
      return;
    }
    await runAdminAction(`/admin/teams/${team.id}/delete/`);
  }

  async function toggleServiceActive(service) {
    await runAdminAction(`/admin/services/${service.id}/update/`, {
      name: service.name,
      slug: service.slug,
      description: service.description,
      port: service.port,
      is_active: !service.is_active
    }, {
      successMessage: t("messages.serviceUpdated")
    });
  }

  async function deleteService(service) {
    if (!window.confirm(t("prompts.deleteService", { name: service.name }))) {
      return;
    }
    await runAdminAction(`/admin/services/${service.id}/delete/`);
  }

  async function startRound(round) {
    await runAdminAction(`/admin/rounds/${round.id}/start/`, {}, {
      refreshServiceMatrix: true,
      successMessage: t("messages.roundStarted")
    });
  }

  async function finishRound(round) {
    await runAdminAction(`/admin/rounds/${round.id}/finish/`, {}, {
      refreshServiceMatrix: true,
      successMessage: t("messages.roundFinished")
    });
  }

  async function generateFlags(round) {
    await runAdminAction(
      `/admin/rounds/${round.id}/generate-flags/`,
      {},
      {
        refreshServiceMatrix: true,
        successMessage: t("messages.flagsGenerated")
      }
    );
  }

  async function runCheckerTick() {
    await runAdminAction("/admin/checker/tick/", {}, {
      refreshServiceMatrix: true,
      successMessage: t("messages.checkerTickCompleted")
    });
  }

  onMounted(async () => {
    await Promise.all([
      loadDashboard(),
      loadServiceStatus(),
      loadRegistrationSettings(),
      loadSession()
    ]);
    await loadAdminState();
  });

  return {
    MAX_TEAM_MEMBERS,
    formatDateTime,
    dashboard,
    serviceStatus,
    registrationSettings,
    adminState,
    session,
    apiErrorMessage,
    authMessage,
    adminMessage,
    teamMessage,
    submissionMessage,
    reservationMessage,
    isLoading,
    isRefreshing,
    isAuthLoading,
    isAdminLoading,
    isTeamActionLoading,
    isSubmittingFlag,
    isReservationLoading,
    isServiceStatusLoading,
    loginForm,
    registerForm,
    reservationForm,
    flagForm,
    teamProfileForm,
    teamMemberForm,
    adminTeamForm,
    adminServiceForm,
    adminRoundForm,
    adminSettingsForm,
    adminScheduleForm,
    summaryCards,
    currentRoundTitle,
    currentRoundMeta,
    hasScoreboard,
    leaderboardLeader,
    recentRounds,
    hasTeam,
    isAdmin,
    isCaptain,
    isRegistrationAvailable,
    adminRunningRound,
    checkerStatusCards,
    canAddParticipant,
    canAddTeamMember,
    loadDashboard,
    loadServiceStatus,
    loadRegistrationSettings,
    addParticipant,
    removeParticipant,
    handleReservationRequest,
    handleLogin,
    handleRegister,
    handleLogout,
    handleFlagSubmit,
    handleTeamProfileUpdate,
    handleTeamMemberAdd,
    updateMemberRole,
    removeMember,
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
