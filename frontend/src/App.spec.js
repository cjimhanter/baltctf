import { mount } from "@vue/test-utils";
import { nextTick } from "vue";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { setLanguage } from "./i18n";

const pageMock = {
  session: {
    authenticated: false,
    user: null,
    team: null
  },
  isSessionReady: true,
  apiErrorMessage: "",
  authMessage: "",
  reservationMessage: "",
  adminMessage: "",
  submissionMessage: "",
  teamMessage: ""
};

vi.mock("./composables/useCompetitionPage", () => ({
  useCompetitionPage: () => pageMock
}));

import App from "./App.vue";

describe("App", () => {
  beforeEach(() => {
    setLanguage("en");
  });

  it("updates the navigation when the language switch changes", async () => {
    const wrapper = mount(App, {
      global: {
        stubs: {
          RouterLink: {
            props: ["to"],
            template: "<a><slot /></a>"
          },
          RouterView: {
            template: "<div />"
          },
          NoticeBanner: true
        }
      }
    });

    expect(wrapper.text()).toContain("Dashboard");
    expect(wrapper.text()).toContain("Scoreboard");
    expect(wrapper.text()).toContain("Service Status");

    const russianButton = wrapper
      .findAll("button")
      .find((button) => button.text() === "Русский");

    await russianButton.trigger("click");
    await nextTick();

    expect(wrapper.text()).toContain("Дашборд");
    expect(wrapper.text()).toContain("Таблица");
    expect(wrapper.text()).toContain("Статусы сервисов");
  });
});
