import { onMounted } from "vue";

import { useI18n } from "../i18n";
import { createCompetitionPageAdminActions } from "./competitionPageAdminActions";
import { createCompetitionPageAuthTeamActions } from "./competitionPageAuthTeamActions";
import { createCompetitionPageDerivedState } from "./competitionPageDerived";
import { MAX_TEAM_MEMBERS } from "./competitionPageFactories";
import { createCompetitionPageLoaders } from "./competitionPageLoaders";
import { createCompetitionPageMutations } from "./competitionPageMutations";
import { createCompetitionPageState } from "./competitionPageState";

export function useCompetitionPage() {
  const { t, formatDateTime } = useI18n();
  const state = createCompetitionPageState();

  const context = {
    ...state,
    t,
    formatDateTime
  };

  const mutations = createCompetitionPageMutations(context);
  Object.assign(context, mutations);

  const derived = createCompetitionPageDerivedState(context);
  Object.assign(context, derived);

  const loaders = createCompetitionPageLoaders(context);
  Object.assign(context, loaders);

  const authTeamActions = createCompetitionPageAuthTeamActions(context);
  const adminActions = createCompetitionPageAdminActions(context);

  onMounted(async () => {
    await Promise.all([
      context.loadDashboard(),
      context.loadServiceStatus(),
      context.loadRegistrationSettings(),
      context.loadSession()
    ]);
    await context.loadAdminState();
  });

  return {
    MAX_TEAM_MEMBERS,
    formatDateTime,
    ...state,
    ...derived,
    ...loaders,
    ...authTeamActions,
    ...adminActions
  };
}
