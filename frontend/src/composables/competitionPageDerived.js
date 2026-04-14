import { computed } from "vue";

import { MAX_TEAM_MEMBERS } from "./competitionPageFactories";

export function createCompetitionPageDerivedState(context) {
  const apiErrorMessage = computed(
    () =>
      context.dashboardErrorMessage.value ||
      context.serviceStatusErrorMessage.value
  );

  const summaryCards = computed(() => [
    {
      label: context.t("dashboard.metrics.teams"),
      value: context.dashboard.value.summary.team_count,
      note: context.t("dashboard.metrics.teamsNote")
    },
    {
      label: context.t("dashboard.metrics.users"),
      value: context.dashboard.value.summary.registered_users_count,
      note: context.t("dashboard.metrics.usersNote")
    },
    {
      label: context.t("dashboard.metrics.services"),
      value: context.dashboard.value.summary.service_count,
      note: context.t("dashboard.metrics.servicesNote")
    },
    {
      label: context.t("dashboard.metrics.rounds"),
      value: context.dashboard.value.summary.round_count,
      note: context.t("dashboard.metrics.roundsNote")
    },
    {
      label: context.t("dashboard.metrics.attackPoints"),
      value: context.dashboard.value.summary.attack_points_total || 0,
      note: context.t("dashboard.metrics.attackPointsNote")
    },
    {
      label: context.t("dashboard.metrics.defensePoints"),
      value: context.dashboard.value.summary.defense_points_total || 0,
      note: context.t("dashboard.metrics.defensePointsNote")
    },
    {
      label: context.t("dashboard.metrics.acceptedFlags"),
      value: context.dashboard.value.summary.accepted_submissions_count,
      note: context.t("dashboard.metrics.acceptedFlagsNote")
    },
    {
      label: context.t("dashboard.metrics.rejectedFlags"),
      value: context.dashboard.value.summary.rejected_submissions_count || 0,
      note: context.t("dashboard.metrics.rejectedFlagsNote")
    },
    {
      label: context.t("dashboard.metrics.checkerChecks"),
      value: context.dashboard.value.summary.checker_status_count || 0,
      note: context.t("dashboard.metrics.checkerChecksNote")
    },
    {
      label: context.t("dashboard.metrics.acceptanceRate"),
      value: context.t("common.percent", {
        count: context.dashboard.value.summary.acceptance_rate || 0
      }),
      note: context.t("dashboard.metrics.acceptanceRateNote")
    }
  ]);

  const currentRoundTitle = computed(() => {
    if (!context.dashboard.value.current_round) {
      return context.t("dashboard.waitingRound");
    }

    return context.t("common.roundLabel", {
      number: context.dashboard.value.current_round.number
    });
  });

  const currentRoundMeta = computed(() => {
    if (!context.dashboard.value.current_round) {
      return context.t("dashboard.waitingRoundMeta");
    }

    return context.t("common.since", {
      state: context.t(
        `roundState.${context.dashboard.value.current_round.state}`
      ),
      date: context.formatDateTime(context.dashboard.value.current_round.started_at)
    });
  });

  const hasScoreboard = computed(() => context.dashboard.value.scoreboard.length > 0);
  const leaderboardLeader = computed(() => context.dashboard.value.scoreboard[0] || null);
  const recentRounds = computed(() => context.dashboard.value.recent_rounds.slice(0, 5));
  const hasTeam = computed(() => Boolean(context.session.value.team));
  const isAdmin = computed(() => Boolean(context.session.value.user?.is_staff));
  const isCaptain = computed(() => context.session.value.membership?.role === "captain");
  const isRegistrationAvailable = computed(
    () => context.registrationSettings.value.registration_available
  );
  const hasServiceStatusData = computed(
    () =>
      context.serviceStatus.value.teams.length > 0 ||
      context.serviceStatus.value.services.length > 0
  );
  const adminRunningRound = computed(
    () =>
      context.adminState.value.rounds.find((round) => round.state === "running") ||
      null
  );
  const checkerStatusCards = computed(() => {
    const summary = context.adminState.value.current_status_summary || {};

    return [
      { key: "up", label: context.t("serviceState.up"), value: summary.up || 0 },
      {
        key: "mumble",
        label: context.t("serviceState.mumble"),
        value: summary.mumble || 0
      },
      {
        key: "corrupt",
        label: context.t("serviceState.corrupt"),
        value: summary.corrupt || 0
      },
      {
        key: "down",
        label: context.t("serviceState.down"),
        value: summary.down || 0
      }
    ];
  });
  const canAddParticipant = computed(
    () => context.registerForm.value.participants.length + 1 < MAX_TEAM_MEMBERS
  );
  const canAddTeamMember = computed(
    () => context.session.value.members.length < MAX_TEAM_MEMBERS
  );

  return {
    apiErrorMessage,
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
    hasServiceStatusData,
    adminRunningRound,
    checkerStatusCards,
    canAddParticipant,
    canAddTeamMember
  };
}
