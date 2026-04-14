import { createRouter, createWebHistory } from "vue-router";

import AdminPage from "../pages/AdminPage.vue";
import DashboardPage from "../pages/DashboardPage.vue";
import ScoreboardPage from "../pages/ScoreboardPage.vue";
import ServiceStatusPage from "../pages/ServiceStatusPage.vue";
import TeamPage from "../pages/TeamPage.vue";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      name: "dashboard",
      component: DashboardPage
    },
    {
      path: "/scoreboard",
      name: "scoreboard",
      component: ScoreboardPage
    },
    {
      path: "/services",
      name: "services",
      component: ServiceStatusPage
    },
    {
      path: "/team",
      name: "team",
      component: TeamPage
    },
    {
      path: "/admin",
      name: "admin",
      component: AdminPage
    }
  ],
  scrollBehavior() {
    return { top: 0 };
  }
});
