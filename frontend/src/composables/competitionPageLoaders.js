import { apiRequest } from "../api";
import { createEmptyAdminState } from "./competitionPageFactories";

export function createCompetitionPageLoaders(context) {
  async function loadDashboard({ refresh = false } = {}) {
    if (refresh && (context.isLoading.value || context.isRefreshing.value)) {
      return false;
    }

    const loadingRef = refresh ? context.isRefreshing : context.isLoading;
    context.dashboardErrorMessage.value = "";

    return context.withLoading(loadingRef, async () => {
      try {
        context.dashboard.value = await apiRequest("/dashboard/");
        return true;
      } catch (error) {
        context.dashboardErrorMessage.value = context.getErrorMessage(
          error,
          context.t("messages.dashboardLoadFailed")
        );
        return false;
      } finally {
        context.isDashboardReady.value = true;
      }
    });
  }

  async function loadServiceStatus() {
    context.serviceStatusErrorMessage.value = "";

    return context.withLoading(context.isServiceStatusLoading, async () => {
      try {
        context.serviceStatus.value = await apiRequest("/service-status/");
        return true;
      } catch (error) {
        context.serviceStatusErrorMessage.value = context.getErrorMessage(
          error,
          context.t("messages.servicesLoadFailed")
        );
        return false;
      } finally {
        context.isServiceStatusReady.value = true;
      }
    });
  }

  async function loadRegistrationSettings() {
    try {
      context.registrationSettings.value = await apiRequest("/registration/settings/");
      return true;
    } catch (error) {
      context.reservationMessage.value = context.getErrorMessage(
        error,
        context.t("messages.registrationSettingsFailed")
      );
      return false;
    }
  }

  async function loadSession() {
    return context.withLoading(context.isSessionLoading, async () => {
      if (!context.token.value) {
        context.clearAuthState();
        return true;
      }

      try {
        const payload = await apiRequest("/auth/me/", { token: context.token.value });

        if (!payload.authenticated) {
          context.clearAuthState();
          return false;
        }

        context.applyAuthenticatedState(payload);
        return true;
      } catch (error) {
        if (error?.status === 401) {
          context.expireSession();
          return false;
        }

        context.authMessage.value = context.getErrorMessage(
          error,
          context.t("messages.authRestoreFailed")
        );
        return false;
      } finally {
        context.isSessionReady.value = true;
      }
    });
  }

  async function loadAdminState() {
    if (!context.token.value || !context.isAdmin.value) {
      context.adminState.value = createEmptyAdminState();
      context.isAdminStateReady.value = true;
      context.syncAdminFormsFromState();
      return true;
    }

    context.isAdminStateReady.value = false;

    return context.withLoading(context.isAdminLoading, async () => {
      try {
        const payload = await apiRequest("/admin/state/", { token: context.token.value });
        context.applyAdminState(payload);
        return true;
      } catch (error) {
        context.isAdminStateReady.value = true;
        context.handleProtectedActionError(
          error,
          context.adminMessage,
          "messages.adminStateFailed"
        );
        return false;
      }
    });
  }

  return {
    loadDashboard,
    loadServiceStatus,
    loadRegistrationSettings,
    loadSession,
    loadAdminState
  };
}
