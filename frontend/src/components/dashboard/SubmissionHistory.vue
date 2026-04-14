<script setup>
import { useI18n } from "../../i18n";

defineProps({
  submissions: {
    type: Array,
    default: () => []
  },
  formatDateTime: {
    type: Function,
    required: true
  }
});

const { t } = useI18n();
</script>

<template>
  <section class="panel-card submission-history">
    <div class="panel-card__header">
      <div>
        <p class="panel-card__kicker">{{ t("submissionHistory.kicker") }}</p>
        <h2 class="panel-card__title">{{ t("submissionHistory.title") }}</h2>
      </div>
    </div>

    <div v-if="submissions.length === 0" class="empty-hint">
      {{ t("submissionHistory.noData") }}
    </div>

    <div v-else class="submission-history__table-wrap">
      <table class="submission-history__table">
        <thead>
          <tr>
            <th>{{ t("submissionHistory.team") }}</th>
            <th>{{ t("submissionHistory.service") }}</th>
            <th>{{ t("submissionHistory.status") }}</th>
            <th>{{ t("submissionHistory.points") }}</th>
            <th>{{ t("submissionHistory.time") }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="submission in submissions" :key="submission.id">
            <td>
              <div class="submission-history__primary">
                <strong>{{ submission.submitting_team?.name || t("common.unknownTeam") }}</strong>
                <span>
                  {{
                    submission.submitted_by?.username
                      ? t("submissionHistory.player", {
                          username: submission.submitted_by.username
                        })
                      : t("common.noData")
                  }}
                </span>
              </div>
            </td>
            <td>
              <div class="submission-history__primary">
                <strong>{{ submission.service?.name || t("common.unknownService") }}</strong>
                <span>
                  {{
                    submission.round
                      ? t("common.roundLabel", { number: submission.round.number })
                      : t("common.noData")
                  }}
                </span>
              </div>
            </td>
            <td>
              <span class="tag" :data-state="submission.status">
                {{ t(`submissionState.${submission.status}`) }}
              </span>
            </td>
            <td class="submission-history__points">
              {{ t("common.points", { count: submission.points_awarded }) }}
            </td>
            <td>{{ formatDateTime(submission.submitted_at) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
