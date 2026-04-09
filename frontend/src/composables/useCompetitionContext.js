import { inject, provide } from "vue";

const competitionPageKey = Symbol("competitionPage");

export function provideCompetitionPage(page) {
  provide(competitionPageKey, page);
}

export function useCompetitionContext() {
  const page = inject(competitionPageKey, null);
  if (!page) {
    throw new Error("Competition page context is not available.");
  }
  return page;
}
