import { apiRequest } from "../api";
import {
  createBlankParticipant,
  createRegisterForm,
  createReservationForm
} from "./competitionPageFactories";

export function createCompetitionPageAuthTeamActions(context) {
  function addParticipant() {
    if (!context.canAddParticipant.value) {
      return;
    }

    context.registerForm.value.participants.push(createBlankParticipant());
  }

  function removeParticipant(index) {
    context.registerForm.value.participants.splice(index, 1);
  }

  async function handleReservationRequest() {
    if (
      context.isReservationLoading.value ||
      !context.registrationSettings.value.registration_available
    ) {
      return false;
    }

    context.reservationMessage.value = "";

    return context.withLoading(context.isReservationLoading, async () => {
      try {
        const payload = await apiRequest("/team-reservations/", {
          method: "POST",
          body: context.reservationForm.value
        });

        const reservation = payload.reservation;
        context.registerForm.value.team_name = reservation.name;
        context.registerForm.value.team_slug = reservation.slug;
        context.registerForm.value.contact_email = reservation.contact_email;
        context.registerForm.value.reservation_token = reservation.token;
        context.registerForm.value.captain.username = reservation.captain_username;
        context.reservationForm.value = createReservationForm();
        context.reservationMessage.value = context.t("messages.reservationCreated");
        await Promise.all([context.loadRegistrationSettings(), context.loadAdminState()]);
        return true;
      } catch (error) {
        context.reservationMessage.value = context.getErrorMessage(
          error,
          context.t("messages.reservationFailed")
        );
        return false;
      }
    });
  }

  async function handleLogin() {
    context.resetAuthMessages();
    context.resetAdminMessage();
    context.resetTeamMessage();

    return context.withLoading(context.isAuthLoading, async () => {
      try {
        const payload = await apiRequest("/auth/login/", {
          method: "POST",
          body: context.loginForm.value
        });

        context.applyAuthenticatedState(payload);
        context.authMessage.value = context.t("messages.signedInAs", {
          username: payload.user.username
        });
        context.loginForm.value = { username: "", password: "" };

        await Promise.all([
          context.loadDashboard({ refresh: true }),
          context.loadServiceStatus(),
          context.loadRegistrationSettings(),
          context.loadSession(),
          context.loadAdminState()
        ]);

        return true;
      } catch (error) {
        context.authMessage.value = context.getErrorMessage(
          error,
          context.t("messages.loginFailed")
        );
        return false;
      }
    });
  }

  async function handleRegister() {
    if (
      context.isAuthLoading.value ||
      !context.registrationSettings.value.registration_available
    ) {
      return false;
    }

    context.resetAuthMessages();
    context.resetAdminMessage();
    context.resetTeamMessage();

    const participantPayload = context.registerForm.value.participants.filter((participant) =>
      Object.values(participant).some(Boolean)
    );

    return context.withLoading(context.isAuthLoading, async () => {
      try {
        const payload = await apiRequest("/auth/register/", {
          method: "POST",
          body: {
            team_name: context.registerForm.value.team_name,
            team_slug: context.registerForm.value.team_slug || undefined,
            affiliation: context.registerForm.value.affiliation,
            contact_email: context.registerForm.value.contact_email,
            reservation_token:
              context.registerForm.value.reservation_token || undefined,
            captain: context.registerForm.value.captain,
            participants: participantPayload
          }
        });

        context.applyAuthenticatedState(payload);
        context.registerForm.value = createRegisterForm();
        context.authMessage.value = context.t("messages.teamRegistered");

        await Promise.all([
          context.loadDashboard({ refresh: true }),
          context.loadServiceStatus(),
          context.loadRegistrationSettings(),
          context.loadSession(),
          context.loadAdminState()
        ]);

        return true;
      } catch (error) {
        context.authMessage.value = context.getErrorMessage(
          error,
          context.t("messages.registerFailed")
        );
        return false;
      }
    });
  }

  async function handleLogout() {
    context.resetAuthMessages();
    context.resetAdminMessage();
    context.resetTeamMessage();

    return context.withLoading(context.isAuthLoading, async () => {
      try {
        if (context.token.value) {
          await apiRequest("/auth/logout/", {
            method: "POST",
            token: context.token.value
          });
        }
      } catch {
        // local cleanup is enough here
      } finally {
        context.clearAuthState();
        context.authMessage.value = context.t("messages.sessionClosed");
      }

      return true;
    });
  }

  async function handleFlagSubmit() {
    const normalizedFlag = context.flagForm.value.flag.trim();
    if (!normalizedFlag) {
      return false;
    }

    context.submissionMessage.value = "";

    return context.withLoading(context.isSubmittingFlag, async () => {
      try {
        const payload = await apiRequest("/submit-flag/", {
          method: "POST",
          token: context.token.value,
          body: {
            flag: normalizedFlag
          }
        });

        context.submissionMessage.value =
          payload.message || context.t("messages.flagSubmitted");
        context.flagForm.value.flag = "";
        await Promise.all([
          context.loadDashboard({ refresh: true }),
          context.loadSession()
        ]);
        return true;
      } catch (error) {
        context.handleProtectedActionError(
          error,
          context.submissionMessage,
          "messages.flagSubmitFailed"
        );
        return false;
      }
    });
  }

  async function handleTeamProfileUpdate() {
    if (!context.hasTeam.value) {
      return false;
    }

    context.resetTeamMessage();

    return context.withLoading(context.isTeamActionLoading, async () => {
      try {
        const payload = await apiRequest("/team/update/", {
          method: "POST",
          token: context.token.value,
          body: context.teamProfileForm.value
        });

        context.applyAuthenticatedState(payload);
        context.teamMessage.value = context.t("messages.teamProfileUpdated");
        await context.loadDashboard({ refresh: true });
        return true;
      } catch (error) {
        context.handleProtectedActionError(
          error,
          context.teamMessage,
          "messages.teamProfileFailed"
        );
        return false;
      }
    });
  }

  async function handleTeamMemberAdd() {
    if (!context.hasTeam.value || !context.canAddTeamMember.value) {
      return false;
    }

    context.resetTeamMessage();

    return context.withLoading(context.isTeamActionLoading, async () => {
      try {
        const payload = await apiRequest("/team/members/", {
          method: "POST",
          token: context.token.value,
          body: context.teamMemberForm.value
        });

        context.applyAuthenticatedState(payload);
        context.teamMemberForm.value = createBlankParticipant();
        context.teamMessage.value = context.t("messages.teamMemberAdded");
        await context.loadDashboard({ refresh: true });
        return true;
      } catch (error) {
        context.handleProtectedActionError(
          error,
          context.teamMessage,
          "messages.addMemberFailed"
        );
        return false;
      }
    });
  }

  async function updateMemberRole(member, role) {
    context.resetTeamMessage();

    return context.withLoading(context.isTeamActionLoading, async () => {
      try {
        const payload = await apiRequest(`/team/members/${member.id}/role/`, {
          method: "POST",
          token: context.token.value,
          body: { role }
        });

        context.applyAuthenticatedState(payload);
        context.teamMessage.value = context.t("messages.memberRoleUpdated");
        return true;
      } catch (error) {
        context.handleProtectedActionError(
          error,
          context.teamMessage,
          "messages.updateRoleFailed"
        );
        return false;
      }
    });
  }

  async function removeMember(member) {
    if (
      !window.confirm(
        context.t("prompts.removeMember", {
          username: member.username
        })
      )
    ) {
      return false;
    }

    context.resetTeamMessage();

    return context.withLoading(context.isTeamActionLoading, async () => {
      try {
        const payload = await apiRequest(`/team/members/${member.id}/remove/`, {
          method: "POST",
          token: context.token.value
        });

        context.applyAuthenticatedState(payload);
        context.teamMessage.value = context.t("messages.memberRemoved");
        await context.loadDashboard({ refresh: true });
        return true;
      } catch (error) {
        context.handleProtectedActionError(
          error,
          context.teamMessage,
          "messages.removeMemberFailed"
        );
        return false;
      }
    });
  }

  return {
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
    removeMember
  };
}
