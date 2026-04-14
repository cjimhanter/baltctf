import { flushPromises, mount } from "@vue/test-utils";
import { defineComponent, h, proxyRefs } from "vue";
import { beforeEach, describe, expect, it } from "vitest";

import { setLanguage } from "../i18n";
import {
  createAdminStatePayload,
  createDashboardPayload,
  createJsonResponse,
  createRegistrationSettingsPayload,
  createServiceStatusPayload,
  createSessionPayload,
  installFetchMock
} from "../test/utils";
import { useCompetitionPage } from "./useCompetitionPage";

function mountCompetitionPageHarness() {
  const Harness = defineComponent({
    name: "CompetitionPageHarness",
    setup() {
      const page = proxyRefs(useCompetitionPage());
      return {
        page
      };
    },
    render() {
      return h("div");
    }
  });

  const wrapper = mount(Harness);
  return {
    wrapper,
    page: wrapper.vm.page
  };
}

function createPublicRoutes(overrides = {}) {
  return {
    "GET /dashboard/": () => createJsonResponse(createDashboardPayload()),
    "GET /service-status/": () => createJsonResponse(createServiceStatusPayload()),
    "GET /registration/settings/": () =>
      createJsonResponse(createRegistrationSettingsPayload()),
    ...overrides
  };
}

describe("useCompetitionPage", () => {
  beforeEach(() => {
    setLanguage("en");
  });

  it("loads the public dashboard, service matrix, and registration settings on mount", async () => {
    const fetchMock = installFetchMock(createPublicRoutes());

    const { page } = mountCompetitionPageHarness();
    await flushPromises();

    expect(fetchMock).toHaveBeenCalledTimes(3);
    expect(page.isDashboardReady).toBe(true);
    expect(page.isServiceStatusReady).toBe(true);
    expect(page.dashboard.summary.team_count).toBe(2);
    expect(page.serviceStatus.teams).toHaveLength(1);
    expect(page.registrationSettings.registration_available).toBe(true);
  });

  it("signs in successfully and refreshes the authenticated view", async () => {
    const loginPayload = createSessionPayload();
    installFetchMock(
      createPublicRoutes({
        "POST /auth/login/": ({ options }) => {
          expect(JSON.parse(options.body)).toEqual({
            username: "captain",
            password: "demo-pass"
          });
          return createJsonResponse(loginPayload);
        },
        "GET /auth/me/": () => createJsonResponse(createSessionPayload())
      })
    );

    const { page } = mountCompetitionPageHarness();
    await flushPromises();

    page.loginForm.username = "captain";
    page.loginForm.password = "demo-pass";

    await page.handleLogin();
    await flushPromises();

    expect(page.session.authenticated).toBe(true);
    expect(page.authMessage).toContain("Signed in as captain");
    expect(page.loginForm.username).toBe("");
    expect(page.loginForm.password).toBe("");
  });

  it("surfaces login failures without mutating the session", async () => {
    installFetchMock(
      createPublicRoutes({
        "POST /auth/login/": () =>
          createJsonResponse({ message: "Bad credentials" }, { status: 400 })
      })
    );

    const { page } = mountCompetitionPageHarness();
    await flushPromises();

    page.loginForm.username = "captain";
    page.loginForm.password = "wrong-pass";

    const succeeded = await page.handleLogin();
    await flushPromises();

    expect(succeeded).toBe(false);
    expect(page.session.authenticated).toBe(false);
    expect(page.authMessage).toBe("Bad credentials");
  });

  it("prevents duplicate sign-in requests while a login is already in flight", async () => {
    let resolveLogin;
    let loginAttempts = 0;

    installFetchMock(
      createPublicRoutes({
        "POST /auth/login/": () => {
          loginAttempts += 1;
          return new Promise((resolve) => {
            resolveLogin = () => resolve(createJsonResponse(createSessionPayload()));
          });
        },
        "GET /auth/me/": () => createJsonResponse(createSessionPayload())
      })
    );

    const { page } = mountCompetitionPageHarness();
    await flushPromises();

    page.loginForm.username = "captain";
    page.loginForm.password = "demo-pass";

    const firstRequest = page.handleLogin();
    const secondRequest = page.handleLogin();

    expect(loginAttempts).toBe(1);

    resolveLogin();
    await firstRequest;
    await secondRequest;
    await flushPromises();

    expect(page.session.authenticated).toBe(true);
  });

  it("submits a flag and refreshes team activity", async () => {
    window.localStorage.setItem("baltctf_api_token", "token-123");

    installFetchMock(
      createPublicRoutes({
        "GET /auth/me/": () => createJsonResponse(createSessionPayload()),
        "POST /submit-flag/": ({ options }) => {
          expect(JSON.parse(options.body)).toEqual({
            flag: "BALTCTF{captured-flag}"
          });
          return createJsonResponse({ message: "Accepted flag." });
        }
      })
    );

    const { page } = mountCompetitionPageHarness();
    await flushPromises();

    page.flagForm.flag = "BALTCTF{captured-flag}";

    const succeeded = await page.handleFlagSubmit();
    await flushPromises();

    expect(succeeded).toBe(true);
    expect(page.submissionMessage).toBe("Accepted flag.");
    expect(page.flagForm.flag).toBe("");
  });

  it("expires the session when a protected action returns 401", async () => {
    window.localStorage.setItem("baltctf_api_token", "token-123");

    installFetchMock(
      createPublicRoutes({
        "GET /auth/me/": () => createJsonResponse(createSessionPayload()),
        "POST /submit-flag/": () =>
          createJsonResponse({ message: "Expired token" }, { status: 401 })
      })
    );

    const { page } = mountCompetitionPageHarness();
    await flushPromises();

    page.flagForm.flag = "BALTCTF{expired}";

    const succeeded = await page.handleFlagSubmit();
    await flushPromises();

    expect(succeeded).toBe(false);
    expect(page.session.authenticated).toBe(false);
    expect(page.token).toBe("");
    expect(page.authMessage).toBe("Session expired. Sign in again.");
  });

  it("updates admin settings and refreshes derived admin state", async () => {
    window.localStorage.setItem("baltctf_api_token", "staff-token");

    let registrationSettings = createRegistrationSettingsPayload();
    const updatedSettings = createRegistrationSettingsPayload({
      registration_open: false,
      round_duration_minutes: 20
    });

    installFetchMock(
      createPublicRoutes({
        "GET /registration/settings/": () =>
          createJsonResponse(registrationSettings),
        "GET /auth/me/": () =>
          createJsonResponse(
            createSessionPayload({
              token: "staff-token",
              user: {
                id: 9,
                username: "admin",
                is_staff: true
              },
              team: null,
              membership: null,
              members: [],
              recent_submissions: []
            })
          ),
        "GET /admin/state/": () =>
          createJsonResponse(createAdminStatePayload({ settings: registrationSettings })),
        "POST /admin/settings/update/": ({ options }) => {
          const payload = JSON.parse(options.body);
          expect(payload.registration_open).toBe(false);
          expect(payload.round_duration_minutes).toBe(20);
          registrationSettings = updatedSettings;
          return createJsonResponse({
            admin_state: createAdminStatePayload({ settings: updatedSettings })
          });
        }
      })
    );

    const { page } = mountCompetitionPageHarness();
    await flushPromises();

    page.adminSettingsForm.registration_open = false;
    page.adminSettingsForm.round_duration_minutes = 20;

    const succeeded = await page.handleAdminSettingsUpdate();
    await flushPromises();

    expect(succeeded).toBeUndefined();
    expect(page.adminMessage).toBe("Competition settings updated.");
    expect(page.adminState.settings.registration_open).toBe(false);
    expect(page.registrationSettings.round_duration_minutes).toBe(20);
  });

  it("surfaces checker tick failures for staff users", async () => {
    window.localStorage.setItem("baltctf_api_token", "staff-token");

    installFetchMock(
      createPublicRoutes({
        "GET /auth/me/": () =>
          createJsonResponse(
            createSessionPayload({
              token: "staff-token",
              user: {
                id: 9,
                username: "admin",
                is_staff: true
              },
              team: null,
              membership: null,
              members: [],
              recent_submissions: []
            })
          ),
        "GET /admin/state/": () => createJsonResponse(createAdminStatePayload()),
        "POST /admin/checker/tick/": () =>
          createJsonResponse({ message: "Checker unavailable" }, { status: 500 })
      })
    );

    const { page } = mountCompetitionPageHarness();
    await flushPromises();

    const succeeded = await page.runCheckerTick();
    await flushPromises();

    expect(succeeded).toBe(false);
    expect(page.adminMessage).toBe("Checker unavailable");
  });
});
