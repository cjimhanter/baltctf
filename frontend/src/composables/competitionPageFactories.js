export const MAX_TEAM_MEMBERS = 6;

export function createEmptyDashboard() {
  return {
    summary: {
      team_count: 0,
      service_count: 0,
      round_count: 0,
      accepted_submissions_count: 0,
      rejected_submissions_count: 0,
      pending_submissions_count: 0,
      submission_count: 0,
      registered_users_count: 0,
      attack_points_total: 0,
      defense_points_total: 0,
      checker_status_count: 0,
      acceptance_rate: 0,
      checker_status_breakdown: {
        up: 0,
        mumble: 0,
        corrupt: 0,
        down: 0
      },
      current_round_status_breakdown: {
        up: 0,
        mumble: 0,
        corrupt: 0,
        down: 0
      },
      latest_submission_at: null,
      latest_checker_report_at: null
    },
    current_round: null,
    services: [],
    service_stats: [],
    scoreboard: [],
    recent_rounds: [],
    recent_activity: [],
    submission_history: [],
    service_status_history: []
  };
}

export function createEmptyServiceStatus() {
  return {
    current_round: null,
    summary: {
      expected_status_count: 0,
      checked_status_count: 0,
      unknown_status_count: 0,
      status_counts: {
        up: 0,
        mumble: 0,
        corrupt: 0,
        down: 0,
        unknown: 0
      },
      latest_reported_at: null
    },
    services: [],
    teams: [],
    history: []
  };
}

export function createEmptySession() {
  return {
    authenticated: false,
    user: null,
    team: null,
    membership: null,
    members: [],
    recent_submissions: []
  };
}

export function createEmptyRegistrationSettings() {
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

export function createEmptyAdminState() {
  return {
    settings: createEmptyRegistrationSettings(),
    reservations: [],
    teams: [],
    services: [],
    rounds: [],
    recent_submissions: [],
    current_round: null,
    current_status_summary: {},
    latest_checker_report_at: null,
    next_round_number: 1
  };
}

export function createBlankParticipant() {
  return {
    username: "",
    password: "",
    email: "",
    first_name: "",
    last_name: ""
  };
}

export function createLoginForm() {
  return {
    username: "",
    password: ""
  };
}

export function createRegisterForm() {
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

export function createReservationForm() {
  return {
    team_name: "",
    team_slug: "",
    captain_username: "",
    contact_email: ""
  };
}

export function createFlagForm() {
  return {
    flag: ""
  };
}

export function createTeamProfileForm() {
  return {
    affiliation: "",
    contact_email: ""
  };
}

export function createAdminTeamForm() {
  return {
    name: "",
    affiliation: "",
    contact_email: ""
  };
}

export function createAdminServiceForm() {
  return {
    name: "",
    description: "",
    port: ""
  };
}

export function createAdminRoundForm() {
  return {
    number: ""
  };
}

export function createAdminSettingsForm() {
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

export function createAdminScheduleForm() {
  return {
    count: 2,
    start_at: ""
  };
}

export function toDateTimeInputValue(value) {
  if (!value) {
    return "";
  }

  const date = new Date(value);
  const offsetMilliseconds = date.getTimezoneOffset() * 60_000;
  return new Date(date.getTime() - offsetMilliseconds).toISOString().slice(0, 16);
}

export function normalizeDateTimeInput(value) {
  if (!value) {
    return null;
  }

  return value.length === 16 ? `${value}:00` : value;
}
