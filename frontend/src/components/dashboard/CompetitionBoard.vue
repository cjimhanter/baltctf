<script setup>
import { useI18n } from "../../i18n";

defineProps({
  dashboard: {
    type: Object,
    required: true
  },
  leaderboardLeader: {
    type: Object,
    default: null
  },
  formatDateTime: {
    type: Function,
    required: true
  }
});

const { t } = useI18n();
</script>

<template>
  <section class="board">
    <div class="board__grid">
      <article class="panel-card board__panel board__panel--leaderboard">
        <div class="panel-card__header">
          <div>
            <p class="panel-card__kicker">{{ t("board.scoreboardKicker") }}</p>
            <h2 class="panel-card__title">{{ t("board.scoreboardTitle") }}</h2>
          </div>
          <div v-if="leaderboardLeader" class="board__leader">
            <span class="board__leader-label">{{ t("board.leader") }}</span>
            <strong class="board__leader-name">{{ leaderboardLeader.team.name }}</strong>
          </div>
        </div>

        <div class="board__table-wrap">
          <table class="board__table">
            <thead>
              <tr>
                <th>#</th>
                <th>{{ t("board.team") }}</th>
                <th>{{ t("board.attack") }}</th>
                <th>{{ t("board.defense") }}</th>
                <th>{{ t("board.total") }}</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="entry in dashboard.scoreboard"
                :key="entry.team.slug"
              >
                <td>{{ entry.rank }}</td>
                <td>
                  <div class="board__team-cell">
                    <strong>{{ entry.team.name }}</strong>
                    <span>{{ entry.team.affiliation || t("common.independent") }}</span>
                  </div>
                </td>
                <td>{{ entry.attack_points }}</td>
                <td>{{ entry.defense_points }}</td>
                <td class="board__total">{{ entry.total_points }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>

      <div class="board__sidebar">
        <article class="panel-card board__panel board__panel--matrix">
          <div class="panel-card__header">
            <div>
              <p class="panel-card__kicker">{{ t("board.serviceStatusKicker") }}</p>
              <h2 class="panel-card__title">{{ t("board.serviceStatusTitle") }}</h2>
            </div>
          </div>

          <div class="board__status-list">
            <article
              v-for="entry in dashboard.scoreboard"
              :key="`${entry.team.slug}-services`"
              class="board__status-card"
            >
              <div class="board__status-head">
                <div>
                  <strong>{{ entry.team.name }}</strong>
                  <span>{{ t("board.rankOnBoard", { rank: entry.rank }) }}</span>
                </div>
                <strong>{{ t("common.points", { count: entry.total_points }) }}</strong>
              </div>

              <div class="board__service-pills">
                <div
                  v-for="serviceState in entry.service_breakdown"
                  :key="`${entry.team.slug}-${serviceState.service.slug}`"
                  class="board__service-pill"
                  :data-state="serviceState.status"
                >
                  <span>{{ serviceState.service.name }}</span>
                  <strong>{{ t(`serviceState.${serviceState.status}`) }}</strong>
                  <small>{{ t("common.points", { count: serviceState.points_awarded }) }}</small>
                </div>
              </div>
            </article>
          </div>
        </article>

        <article class="panel-card board__panel board__panel--activity">
          <div class="panel-card__header">
            <div>
              <p class="panel-card__kicker">{{ t("board.attackFeedKicker") }}</p>
              <h2 class="panel-card__title">{{ t("board.attackFeedTitle") }}</h2>
            </div>
          </div>

          <div class="board__feed">
            <article
              v-for="activity in dashboard.recent_activity"
              :key="activity.id"
              class="board__feed-item"
            >
              <div class="board__feed-topline">
                <strong>{{ activity.submitting_team.name }}</strong>
                <span class="tag" :data-state="activity.status">
                  {{ t(`submissionState.${activity.status}`) }}
                </span>
              </div>
              <p class="board__feed-copy">
                {{
                  t("board.targetVia", {
                    team: activity.target_team?.name || t("common.unknownTeam"),
                    service: activity.service?.name || t("common.unknownService")
                  })
                }}
              </p>
              <div class="board__feed-meta">
                <span>{{ t("common.points", { count: activity.points_awarded }) }}</span>
                <span>{{ formatDateTime(activity.submitted_at) }}</span>
              </div>
            </article>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>
