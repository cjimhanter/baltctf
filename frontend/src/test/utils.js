import { mount } from "@vue/test-utils";
import { defineComponent, h } from "vue";
import { vi } from "vitest";

import { provideCompetitionPage } from "../composables/useCompetitionContext";

function isPlainObject(value) {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function merge(target, source) {
  Object.entries(source).forEach(([key, value]) => {
    if (isPlainObject(value) && isPlainObject(target[key])) {
      merge(target[key], value);
      return;
    }

    target[key] = value;
  });

  return target;
}

export function createRegistrationSettingsPayload(overrides = {}) {
  return merge(
    {
      registration_open: true,
      registration_starts_at: "2026-04-10T10:00:00Z",
      registration_ends_at: "2026-04-11T10:00:00Z",
      reservation_required_for_registration: false,
      auto_approve_registrations: true,
      round_duration_minutes: 15,
      round_break_minutes: 5,
      registration_available: true
    },
    overrides
  );
}

export function createDashboardPayload(overrides = {}) {
  return merge(
    {
      summary: {
        team_count: 2,
        service_count: 3,
        round_count: 4,
        accepted_submissions_count: 12,
        rejected_submissions_count: 3,
        pending_submissions_count: 0,
        submission_count: 15,
        registered_users_count: 8,
        attack_points_total: 300,
        defense_points_total: 390,
        checker_status_count: 18,
        acceptance_rate: 80,
        checker_status_breakdown: {
          up: 12,
          mumble: 3,
          corrupt: 2,
          down: 1
        },
        current_round_status_breakdown: {
          up: 4,
          mumble: 1,
          corrupt: 0,
          down: 1
        },
        latest_submission_at: "2026-04-10T10:05:00Z",
        latest_checker_report_at: "2026-04-10T10:06:00Z"
      },
      current_round: {
        id: 7,
        number: 4,
        state: "running",
        started_at: "2026-04-10T10:00:00Z"
      },
      services: [
        {
          id: 1,
          name: "Atlas Board",
          slug: "atlas-board"
        },
        {
          id: 2,
          name: "Signal API",
          slug: "signal-api"
        }
      ],
      service_stats: [
        {
          service: {
            id: 1,
            name: "Atlas Board",
            slug: "atlas-board"
          },
          flag_count: 8,
          accepted_submission_count: 7,
          attack_points: 175,
          defense_points: 210,
          checker_status_count: 10,
          uptime_percent: 80,
          status_counts: {
            up: 8,
            mumble: 1,
            corrupt: 1,
            down: 0
          }
        }
      ],
      scoreboard: [
        {
          rank: 1,
          attack_points: 120,
          defense_points: 210,
          total_points: 330,
          submission_count: 6,
          accepted_submission_count: 5,
          rejected_submission_count: 1,
          pending_submission_count: 0,
          defense_check_count: 8,
          current_round_defense_points: 20,
          service_health: {
            up: 1,
            mumble: 1,
            corrupt: 0,
            down: 0,
            unknown: 0,
            checked_count: 2,
            issue_count: 1
          },
          team: {
            id: 1,
            name: "Northern Lights",
            slug: "northern-lights",
            affiliation: "BSUIR"
          },
          service_breakdown: [
            {
              service: {
                id: 1,
                name: "Atlas Board",
                slug: "atlas-board"
              },
              status: "up",
              points_awarded: 100
            },
            {
              service: {
                id: 2,
                name: "Signal API",
                slug: "signal-api"
              },
              status: "mumble",
              points_awarded: 80
            }
          ]
        },
        {
          rank: 2,
          attack_points: 95,
          defense_points: 180,
          total_points: 275,
          submission_count: 5,
          accepted_submission_count: 4,
          rejected_submission_count: 1,
          pending_submission_count: 0,
          defense_check_count: 7,
          current_round_defense_points: 10,
          service_health: {
            up: 1,
            mumble: 0,
            corrupt: 0,
            down: 0,
            unknown: 1,
            checked_count: 1,
            issue_count: 1
          },
          team: {
            id: 2,
            name: "Amber Byte",
            slug: "amber-byte",
            affiliation: "KBTU"
          },
          service_breakdown: [
            {
              service: {
                id: 1,
                name: "Atlas Board",
                slug: "atlas-board"
              },
              status: "up",
              points_awarded: 90
            }
          ]
        }
      ],
      recent_rounds: [
        {
          id: 7,
          number: 4,
          state: "running",
          started_at: "2026-04-10T10:00:00Z",
          accepted_submission_count: 3,
          attack_points: 75,
          defense_points: 45,
          checker_status_count: 6,
          status_counts: {
            up: 4,
            mumble: 1,
            corrupt: 0,
            down: 1
          },
          unknown_status_count: 0
        },
        {
          id: 6,
          number: 3,
          state: "finished",
          started_at: "2026-04-10T09:30:00Z",
          accepted_submission_count: 4,
          attack_points: 100,
          defense_points: 60,
          checker_status_count: 6,
          status_counts: {
            up: 5,
            mumble: 1,
            corrupt: 0,
            down: 0
          },
          unknown_status_count: 0
        }
      ],
      recent_activity: [
        {
          id: 11,
          submitting_team: {
            name: "Amber Byte"
          },
          target_team: {
            name: "Northern Lights"
          },
          service: {
            name: "Atlas Board"
          },
          round: {
            id: 7,
            number: 4,
            state: "running",
            started_at: "2026-04-10T10:00:00Z"
          },
          status: "accepted",
          points_awarded: 10,
          submitted_at: "2026-04-10T10:05:00Z"
        }
      ],
      submission_history: [
        {
          id: 11,
          submitting_team: {
            name: "Amber Byte"
          },
          target_team: {
            name: "Northern Lights"
          },
          service: {
            name: "Atlas Board"
          },
          round: {
            id: 7,
            number: 4,
            state: "running",
            started_at: "2026-04-10T10:00:00Z"
          },
          submitted_by: {
            username: "amber"
          },
          status: "accepted",
          points_awarded: 10,
          submitted_at: "2026-04-10T10:05:00Z"
        }
      ],
      service_status_history: [
        {
          round: {
            id: 7,
            number: 4,
            state: "running",
            started_at: "2026-04-10T10:00:00Z"
          },
          services: [
            {
              service: {
                id: 1,
                name: "Atlas Board",
                slug: "atlas-board"
              },
              status_counts: {
                up: 2,
                mumble: 0,
                corrupt: 0,
                down: 0,
                unknown: 0
              },
              unknown: 0,
              checked_count: 2,
              issue_count: 0,
              defense_points: 20,
              latest_reported_at: "2026-04-10T10:06:00Z"
            }
          ]
        }
      ]
    },
    overrides
  );
}

export function createServiceStatusPayload(overrides = {}) {
  return merge(
    {
      current_round: {
        id: 7,
        number: 4,
        state: "running"
      },
      summary: {
        expected_status_count: 4,
        checked_status_count: 2,
        unknown_status_count: 2,
        status_counts: {
          up: 1,
          mumble: 1,
          corrupt: 0,
          down: 0,
          unknown: 2
        },
        latest_reported_at: "2026-04-10T10:06:00Z"
      },
      services: [
        {
          id: 1,
          name: "Atlas Board"
        },
        {
          id: 2,
          name: "Signal API"
        }
      ],
      teams: [
        {
          team: {
            id: 1,
            name: "Northern Lights",
            affiliation: "BSUIR"
          },
          services: [
            {
              service: {
                id: 1
              },
              status: "up",
              points_awarded: 100,
              message: "Healthy",
              reported_at: "2026-04-10T10:06:00Z"
            },
            {
              service: {
                id: 2
              },
              status: "mumble",
              points_awarded: 80,
              message: "High latency",
              reported_at: "2026-04-10T10:06:00Z"
            }
          ]
        }
      ],
      history: [
        {
          round: {
            id: 7,
            number: 4,
            state: "running",
            started_at: "2026-04-10T10:00:00Z"
          },
          services: [
            {
              service: {
                id: 1,
                name: "Atlas Board",
                slug: "atlas-board"
              },
              status_counts: {
                up: 1,
                mumble: 0,
                corrupt: 0,
                down: 0,
                unknown: 0
              },
              unknown: 0,
              checked_count: 1,
              issue_count: 0,
              defense_points: 100,
              latest_reported_at: "2026-04-10T10:06:00Z"
            }
          ]
        }
      ]
    },
    overrides
  );
}

export function createSessionPayload(overrides = {}) {
  return merge(
    {
      authenticated: true,
      token: "token-123",
      user: {
        id: 1,
        username: "captain",
        is_staff: false
      },
      team: {
        id: 1,
        name: "Northern Lights",
        slug: "northern-lights",
        affiliation: "BSUIR",
        contact_email: "team@baltctf.test",
        moderation_status: "approved",
        moderation_note: "Ready to play"
      },
      membership: {
        role: "captain"
      },
      members: [
        {
          id: 1,
          username: "captain",
          role: "captain",
          first_name: "Nora",
          last_name: "Wave"
        },
        {
          id: 2,
          username: "player1",
          role: "player",
          first_name: "Lina",
          last_name: "Byte"
        }
      ],
      recent_submissions: [
        {
          id: 31,
          status: "accepted",
          points_awarded: 10,
          submitted_at: "2026-04-10T10:06:00Z",
          target_team: {
            name: "Amber Byte"
          },
          service: {
            name: "Atlas Board"
          },
          round: {
            id: 7,
            number: 4,
            state: "running",
            started_at: "2026-04-10T10:00:00Z"
          },
          submitted_by: {
            username: "captain"
          },
          submitting_team: {
            name: "Northern Lights"
          }
        }
      ]
    },
    overrides
  );
}

export function createAdminStatePayload(overrides = {}) {
  return merge(
    {
      settings: createRegistrationSettingsPayload(),
      reservations: [
        {
          id: 1,
          name: "Signal Wolves",
          captain_username: "wolfcapt",
          contact_email: "wolf@baltctf.test",
          expires_at: "2026-04-11T10:00:00Z",
          status: "pending",
          note: ""
        }
      ],
      teams: [
        {
          id: 1,
          name: "Northern Lights",
          slug: "northern-lights",
          affiliation: "BSUIR",
          contact_email: "team@baltctf.test",
          is_active: true,
          moderation_status: "approved",
          moderation_note: "Ready",
          member_count: 2
        }
      ],
      services: [
        {
          id: 1,
          name: "Atlas Board",
          slug: "atlas-board",
          description: "Demo web board",
          port: 8080,
          is_active: true,
          flag_count: 18
        }
      ],
      rounds: [
        {
          id: 7,
          number: 4,
          state: "running",
          flag_count: 36
        }
      ],
      current_round: {
        id: 7,
        number: 4,
        state: "running"
      },
      recent_submissions: [
        {
          id: 31,
          status: "accepted",
          points_awarded: 10,
          submitted_at: "2026-04-10T10:06:00Z",
          target_team: {
            name: "Amber Byte"
          },
          service: {
            name: "Atlas Board"
          },
          round: {
            id: 7,
            number: 4,
            state: "running",
            started_at: "2026-04-10T10:00:00Z"
          },
          submitted_by: {
            username: "captain"
          },
          submitting_team: {
            name: "Northern Lights"
          }
        }
      ],
      current_status_summary: {
        up: 3,
        mumble: 1,
        corrupt: 0,
        down: 0
      },
      current_checker_diagnostics: {
        round: {
          id: 7,
          number: 4,
          state: "running"
        },
        active_team_count: 2,
        active_service_count: 2,
        expected_status_count: 4,
        checked_status_count: 4,
        unknown_status_count: 0,
        issue_count: 1,
        status_counts: {
          up: 3,
          mumble: 1,
          corrupt: 0,
          down: 0,
          unknown: 0
        },
        latest_reported_at: "2026-04-10T10:07:00Z",
        latest_issues: [
          {
            team: {
              id: 2,
              name: "Amber Byte",
              slug: "amber-byte"
            },
            service: {
              id: 2,
              name: "Signal API",
              slug: "signal-api"
            },
            status: "mumble",
            points_awarded: 5,
            message: "High latency while reading the stored flag.",
            reported_at: "2026-04-10T10:07:00Z"
          }
        ]
      },
      latest_checker_report_at: "2026-04-10T10:07:00Z",
      next_round_number: 5
    },
    overrides
  );
}

export function createPageContext(overrides = {}) {
  const dashboard = createDashboardPayload({
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
  });

  const base = {
    MAX_TEAM_MEMBERS: 6,
    formatDateTime: () => "10 Apr 2026, 10:00",
    dashboard,
    serviceStatus: createServiceStatusPayload({
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
    }),
    registrationSettings: createRegistrationSettingsPayload(),
    adminState: createAdminStatePayload({
      reservations: [],
      teams: [],
      services: [],
      rounds: [],
      recent_submissions: [],
      current_round: null,
      current_status_summary: {},
      current_checker_diagnostics: {
        round: null,
        active_team_count: 0,
        active_service_count: 0,
        expected_status_count: 0,
        checked_status_count: 0,
        unknown_status_count: 0,
        issue_count: 0,
        status_counts: {
          up: 0,
          mumble: 0,
          corrupt: 0,
          down: 0,
          unknown: 0
        },
        latest_reported_at: null,
        latest_issues: []
      },
      latest_checker_report_at: null
    }),
    session: {
      authenticated: false,
      user: null,
      team: null,
      membership: null,
      members: [],
      recent_submissions: []
    },
    dashboardErrorMessage: "",
    serviceStatusErrorMessage: "",
    apiErrorMessage: "",
    authMessage: "",
    adminMessage: "",
    teamMessage: "",
    submissionMessage: "",
    reservationMessage: "",
    isLoading: false,
    isRefreshing: false,
    isDashboardReady: true,
    isAuthLoading: false,
    isAdminLoading: false,
    isAdminStateReady: true,
    isTeamActionLoading: false,
    isSubmittingFlag: false,
    isReservationLoading: false,
    isServiceStatusLoading: false,
    isServiceStatusReady: true,
    isSessionLoading: false,
    isSessionReady: true,
    loginForm: {
      username: "",
      password: ""
    },
    registerForm: {
      team_name: "",
      team_slug: "",
      affiliation: "",
      contact_email: "",
      reservation_token: "",
      captain: {
        username: "",
        password: "",
        email: "",
        first_name: "",
        last_name: ""
      },
      participants: []
    },
    reservationForm: {
      team_name: "",
      team_slug: "",
      captain_username: "",
      contact_email: ""
    },
    flagForm: {
      flag: ""
    },
    teamProfileForm: {
      affiliation: "",
      contact_email: ""
    },
    teamMemberForm: {
      username: "",
      password: "",
      email: "",
      first_name: "",
      last_name: ""
    },
    adminTeamForm: {
      name: "",
      affiliation: "",
      contact_email: ""
    },
    adminServiceForm: {
      name: "",
      description: "",
      port: ""
    },
    adminRoundForm: {
      number: ""
    },
    adminSettingsForm: {
      registration_open: true,
      registration_starts_at: "",
      registration_ends_at: "",
      reservation_required_for_registration: false,
      auto_approve_registrations: true,
      round_duration_minutes: 15,
      round_break_minutes: 5
    },
    adminScheduleForm: {
      count: 2,
      start_at: ""
    },
    summaryCards: [],
    currentRoundTitle: "Waiting for first round",
    currentRoundMeta: "Create rounds or load demo data.",
    hasScoreboard: false,
    leaderboardLeader: null,
    recentRounds: [],
    hasTeam: false,
    isAdmin: false,
    isCaptain: false,
    isRegistrationAvailable: true,
    hasServiceStatusData: false,
    adminRunningRound: null,
    checkerStatusCards: [],
    canAddParticipant: true,
    canAddTeamMember: true,
    loadDashboard: vi.fn(),
    loadServiceStatus: vi.fn(),
    loadRegistrationSettings: vi.fn(),
    loadSession: vi.fn(),
    handleReservationRequest: vi.fn(),
    handleLogin: vi.fn(),
    handleRegister: vi.fn(),
    handleLogout: vi.fn(),
    handleFlagSubmit: vi.fn(),
    handleTeamProfileUpdate: vi.fn(),
    handleTeamMemberAdd: vi.fn(),
    updateMemberRole: vi.fn(),
    removeMember: vi.fn(),
    addParticipant: vi.fn(),
    removeParticipant: vi.fn(),
    handleAdminTeamCreate: vi.fn(),
    setTeamModeration: vi.fn(),
    handleAdminServiceCreate: vi.fn(),
    handleAdminRoundCreate: vi.fn(),
    handleAdminSettingsUpdate: vi.fn(),
    handleAdminRoundSchedule: vi.fn(),
    approveReservation: vi.fn(),
    rejectReservation: vi.fn(),
    toggleTeamActive: vi.fn(),
    deleteTeam: vi.fn(),
    toggleServiceActive: vi.fn(),
    deleteService: vi.fn(),
    startRound: vi.fn(),
    finishRound: vi.fn(),
    generateFlags: vi.fn(),
    runCheckerTick: vi.fn()
  };

  return merge(base, overrides);
}

export function mountWithCompetitionPage(Component, page, options = {}) {
  const Wrapper = defineComponent({
    name: "CompetitionPageTestWrapper",
    setup() {
      provideCompetitionPage(page);
      return () => h(Component);
    }
  });

  return mount(Wrapper, {
    ...options,
    global: {
      ...(options.global || {}),
      stubs: {
        RouterLink: {
          props: ["to"],
          template: "<a><slot /></a>"
        },
        ...(options.global?.stubs || {})
      }
    }
  });
}

export function createJsonResponse(
  data,
  { status = 200, contentType = "application/json" } = {}
) {
  return {
    ok: status >= 200 && status < 300,
    status,
    headers: {
      get(name) {
        return name?.toLowerCase() === "content-type" ? contentType : null;
      }
    },
    json: async () => data
  };
}

export function installFetchMock(routes) {
  return vi.spyOn(global, "fetch").mockImplementation((input, options = {}) => {
    const url = typeof input === "string" ? input : input.url;
    const pathname = new URL(url).pathname.replace(/^\/api/, "");
    const method = (options.method || "GET").toUpperCase();
    const key = `${method} ${pathname}`;
    const handler = routes[key];

    if (!handler) {
      throw new Error(`Unexpected request: ${key}`);
    }

    return Promise.resolve(handler({ key, options, url }));
  });
}
