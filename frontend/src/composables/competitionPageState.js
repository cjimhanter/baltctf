import { ref } from "vue";

import { readStoredToken } from "../api";
import {
  createAdminRoundForm,
  createAdminScheduleForm,
  createAdminServiceForm,
  createAdminSettingsForm,
  createAdminTeamForm,
  createEmptyAdminState,
  createEmptyDashboard,
  createEmptyRegistrationSettings,
  createEmptyServiceStatus,
  createEmptySession,
  createFlagForm,
  createLoginForm,
  createRegisterForm,
  createReservationForm,
  createTeamProfileForm,
  createBlankParticipant
} from "./competitionPageFactories";

export function createCompetitionPageState() {
  return {
    dashboard: ref(createEmptyDashboard()),
    serviceStatus: ref(createEmptyServiceStatus()),
    adminState: ref(createEmptyAdminState()),
    registrationSettings: ref(createEmptyRegistrationSettings()),
    session: ref(createEmptySession()),
    dashboardErrorMessage: ref(""),
    serviceStatusErrorMessage: ref(""),
    authMessage: ref(""),
    adminMessage: ref(""),
    teamMessage: ref(""),
    submissionMessage: ref(""),
    reservationMessage: ref(""),
    isLoading: ref(false),
    isRefreshing: ref(false),
    isDashboardReady: ref(false),
    isAuthLoading: ref(false),
    isAdminLoading: ref(false),
    isAdminStateReady: ref(false),
    isTeamActionLoading: ref(false),
    isSubmittingFlag: ref(false),
    isReservationLoading: ref(false),
    isServiceStatusLoading: ref(false),
    isServiceStatusReady: ref(false),
    isSessionLoading: ref(false),
    isSessionReady: ref(false),
    token: ref(readStoredToken()),
    loginForm: ref(createLoginForm()),
    registerForm: ref(createRegisterForm()),
    reservationForm: ref(createReservationForm()),
    flagForm: ref(createFlagForm()),
    teamProfileForm: ref(createTeamProfileForm()),
    teamMemberForm: ref(createBlankParticipant()),
    adminTeamForm: ref(createAdminTeamForm()),
    adminServiceForm: ref(createAdminServiceForm()),
    adminRoundForm: ref(createAdminRoundForm()),
    adminSettingsForm: ref(createAdminSettingsForm()),
    adminScheduleForm: ref(createAdminScheduleForm())
  };
}
