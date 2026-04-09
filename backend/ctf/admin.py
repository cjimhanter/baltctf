from django.contrib import admin

from .models import (
    CompetitionSettings,
    Flag,
    Round,
    Service,
    ServiceStatus,
    Submission,
    Team,
    TeamMember,
    TeamReservation,
)


class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 0
    autocomplete_fields = ("user",)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "affiliation",
        "contact_email",
        "is_active",
        "moderation_status",
        "created_at",
    )
    list_filter = ("is_active", "moderation_status")
    search_fields = ("name", "slug", "affiliation", "contact_email")
    inlines = (TeamMemberInline,)


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("user", "team", "role", "created_at")
    list_filter = ("role", "team")
    search_fields = ("user__username", "user__email", "team__name")
    autocomplete_fields = ("user", "team")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "port", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")


@admin.register(Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = ("number", "state", "started_at", "finished_at")
    list_filter = ("state",)
    ordering = ("-number",)


@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = ("value", "team", "service", "round", "expires_at")
    list_filter = ("service", "round")
    search_fields = ("value", "team__name", "service__name")


@admin.register(ServiceStatus)
class ServiceStatusAdmin(admin.ModelAdmin):
    list_display = (
        "team",
        "service",
        "round",
        "status",
        "points_awarded",
        "reported_at",
    )
    list_filter = ("status", "service", "round")
    search_fields = ("team__name", "service__name", "message")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "submitting_team",
        "submitted_by",
        "status",
        "points_awarded",
        "submitted_value",
        "submitted_at",
    )
    list_filter = ("status",)
    search_fields = (
        "submitting_team__name",
        "submitted_by__username",
        "submitted_value",
        "message",
    )
    autocomplete_fields = ("flag", "submitted_by", "submitting_team")


@admin.register(CompetitionSettings)
class CompetitionSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "registration_open",
        "registration_starts_at",
        "registration_ends_at",
        "reservation_required_for_registration",
        "auto_approve_registrations",
        "round_duration_minutes",
        "round_break_minutes",
        "updated_at",
    )

    def has_add_permission(self, request):
        return not CompetitionSettings.objects.exists()


@admin.register(TeamReservation)
class TeamReservationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "captain_username",
        "contact_email",
        "status",
        "expires_at",
        "created_at",
        "reviewed_at",
    )
    list_filter = ("status",)
    search_fields = ("name", "slug", "contact_email", "captain_username", "token")
