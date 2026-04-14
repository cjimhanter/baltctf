import { afterEach, beforeEach, vi } from "vitest";

import { setLanguage } from "../i18n";

beforeEach(() => {
  window.localStorage.clear();
  setLanguage("en");
  window.confirm = vi.fn(() => true);
  window.prompt = vi.fn(() => "");
});

afterEach(() => {
  vi.restoreAllMocks();
  setLanguage("en");
});
