import { nextTick } from "vue";
import { describe, expect, it } from "vitest";

import DashboardPage from "./DashboardPage.vue";
import ScoreboardPage from "./ScoreboardPage.vue";
import ServiceStatusPage from "./ServiceStatusPage.vue";
import TeamPage from "./TeamPage.vue";
import AdminPage from "./AdminPage.vue";
import { setLanguage } from "../i18n";
import {
  createAdminStatePayload,
  createDashboardPayload,
  createPageContext,
  createServiceStatusPayload,
  createSessionPayload,
  mountWithCompetitionPage
} from "../test/utils";

describe("DashboardPage", () => {
  it("renders the loading state before dashboard data is ready", () => {
    const wrapper = mountWithCompetitionPage(
      DashboardPage,
      createPageContext({
        isDashboardReady: false,
        isLoading: true
      })
    );

    expect(wrapper.text()).toContain("Loading backend data");
  });

  it("renders an explicit error state when the dashboard request fails", () => {
    const wrapper = mountWithCompetitionPage(
      DashboardPage,
      createPageContext({
        dashboardErrorMessage: "Dashboard backend is offline"
      })
    );

    expect(wrapper.text()).toContain("Dashboard is temporarily unavailable");
    expect(wrapper.text()).toContain("Dashboard backend is offline");
  });

  it("renders the populated scoreboard and refresh action", async () => {
    const dashboard = createDashboardPayload();
    const page = createPageContext({
      dashboard,
      summaryCards: [
        { label: "Teams", value: 2, note: "approved squads currently competing" }
      ],
      hasScoreboard: true,
      leaderboardLeader: dashboard.scoreboard[0],
      recentRounds: dashboard.recent_rounds
    });

    const wrapper = mountWithCompetitionPage(DashboardPage, page);

    expect(wrapper.text()).toContain("Northern Lights");
    expect(wrapper.text()).toContain("Amber Byte");
    expect(wrapper.text()).toContain("Checker History");
    expect(wrapper.text()).toContain("Latest flag submissions");

    await wrapper.find(".hero__refresh").trigger("click");

    expect(page.loadDashboard).toHaveBeenCalledWith({ refresh: true });
  });
});

describe("ServiceStatusPage", () => {
  it("renders the loading state while checker data is being restored", () => {
    const wrapper = mountWithCompetitionPage(
      ServiceStatusPage,
      createPageContext({
        isServiceStatusReady: false,
        isServiceStatusLoading: true
      })
    );

    expect(wrapper.text()).toContain("Loading the latest checker results");
  });

  it("renders an explicit error state when the service matrix request fails", () => {
    const wrapper = mountWithCompetitionPage(
      ServiceStatusPage,
      createPageContext({
        serviceStatusErrorMessage: "Checker matrix timeout"
      })
    );

    expect(wrapper.text()).toContain("Service status is temporarily unavailable");
    expect(wrapper.text()).toContain("Checker matrix timeout");
  });

  it("renders the service matrix with team and service cells", () => {
    const wrapper = mountWithCompetitionPage(
      ServiceStatusPage,
      createPageContext({
        serviceStatus: createServiceStatusPayload(),
        hasServiceStatusData: true
      })
    );

    expect(wrapper.text()).toContain("Northern Lights");
    expect(wrapper.text()).toContain("Atlas Board");
    expect(wrapper.text()).toContain("Healthy");
    expect(wrapper.text()).toContain("Service timeline by round");
  });
});

describe("ScoreboardPage", () => {
  it("renders the full scoreboard route with service posture", () => {
    const dashboard = createDashboardPayload();
    const wrapper = mountWithCompetitionPage(
      ScoreboardPage,
      createPageContext({
        dashboard,
        hasScoreboard: true
      })
    );

    expect(wrapper.text()).toContain("Attack and defense standings");
    expect(wrapper.text()).toContain("Northern Lights");
    expect(wrapper.text()).toContain("Signal API");
    expect(wrapper.text()).toContain("Full ranking");
    expect(wrapper.text()).toContain("Service analytics");
    expect(wrapper.text()).toContain("Latest flag submissions");
  });

  it("refreshes dashboard data from the scoreboard route", async () => {
    const page = createPageContext({
      dashboard: createDashboardPayload(),
      hasScoreboard: true
    });
    const wrapper = mountWithCompetitionPage(ScoreboardPage, page);

    await wrapper.find(".scoreboard-page__header-side .button").trigger("click");

    expect(page.loadDashboard).toHaveBeenCalledWith({ refresh: true });
  });
});

describe("TeamPage", () => {
  it("renders a loading state while the session is being restored", () => {
    const wrapper = mountWithCompetitionPage(
      TeamPage,
      createPageContext({
        isSessionReady: false
      })
    );

    expect(wrapper.text()).toContain("Restoring account session and team workspace");
  });

  it("updates the guest route copy when the language changes", async () => {
    const wrapper = mountWithCompetitionPage(TeamPage, createPageContext());

    expect(wrapper.text()).toContain("Team Portal");
    setLanguage("ru");
    await nextTick();

    expect(wrapper.text()).toContain("Портал команды");
    expect(wrapper.text()).toContain("Регистрация");
  });

  it("renders the authenticated team workspace", () => {
    const session = createSessionPayload();
    const wrapper = mountWithCompetitionPage(
      TeamPage,
      createPageContext({
        session,
        hasTeam: true,
        isCaptain: true
      })
    );

    expect(wrapper.text()).toContain("Flag Submission");
    expect(wrapper.text()).toContain("Captain tools");
    expect(wrapper.text()).toContain("Northern Lights");
  });

  it("renders the no-team fallback for operator accounts", () => {
    const session = createSessionPayload({
      team: null,
      membership: null,
      members: [],
      recent_submissions: []
    });

    const wrapper = mountWithCompetitionPage(
      TeamPage,
      createPageContext({
        session,
        hasTeam: false
      })
    );

    expect(wrapper.text()).toContain("No team linked to this account");
    expect(wrapper.text()).toContain("Operator Session");
  });
});

describe("AdminPage", () => {
  it("blocks guest users from admin workflows", () => {
    const wrapper = mountWithCompetitionPage(AdminPage, createPageContext());

    expect(wrapper.text()).toContain("Admin access requires authentication");
  });

  it("blocks authenticated non-staff users from admin workflows", () => {
    const wrapper = mountWithCompetitionPage(
      AdminPage,
      createPageContext({
        session: createSessionPayload(),
        isAdmin: false
      })
    );

    expect(wrapper.text()).toContain("Staff access required");
  });

  it("renders the staff console and updates copy when the language changes", async () => {
    const session = createSessionPayload({
      user: {
        id: 9,
        username: "admin",
        is_staff: true
      },
      team: null,
      membership: null,
      members: [],
      recent_submissions: []
    });

    const wrapper = mountWithCompetitionPage(
      AdminPage,
      createPageContext({
        session,
        isAdmin: true,
        adminState: createAdminStatePayload(),
        adminRunningRound: {
          id: 7,
          number: 4,
          state: "running"
        },
        checkerStatusCards: [
          { key: "up", label: "Up", value: 3 }
        ]
      })
    );

    expect(wrapper.text()).toContain("Registration");
    expect(wrapper.text()).toContain("Signal Wolves");
    expect(wrapper.text()).toContain("Submissions");
    expect(wrapper.text()).toContain("Expected checks");
    expect(wrapper.text()).toContain("4 of 4 recorded");
    expect(wrapper.text()).toContain("High latency while reading the stored flag.");

    setLanguage("ru");
    await nextTick();

    expect(wrapper.text()).toContain("Админ-инструменты");
    expect(wrapper.text()).toContain("Резервирования");
    expect(wrapper.text()).toContain("Ожидаемые проверки");
  });
});
