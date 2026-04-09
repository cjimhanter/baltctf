from django.conf import settings
from django.db import models
from django.utils import timezone


class Team(models.Model):
    class ModerationStatus(models.TextChoices):
        APPROVED = "approved", "Approved"
        PENDING = "pending", "Pending"
        SUSPENDED = "suspended", "Suspended"

    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=64, unique=True)
    affiliation = models.CharField(max_length=128, blank=True)
    contact_email = models.EmailField(blank=True)
    is_active = models.BooleanField(default=True)
    moderation_status = models.CharField(
        max_length=16,
        choices=ModerationStatus.choices,
        default=ModerationStatus.APPROVED,
    )
    moderation_note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    @property
    def is_approved(self) -> bool:
        return self.moderation_status == self.ModerationStatus.APPROVED


class TeamMember(models.Model):
    class Role(models.TextChoices):
        CAPTAIN = "captain", "Captain"
        PLAYER = "player", "Player"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="team_membership",
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="members",
    )
    role = models.CharField(
        max_length=16,
        choices=Role.choices,
        default=Role.PLAYER,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["team__name", "role", "user__username"]
        constraints = [
            models.UniqueConstraint(
                fields=["team", "user"],
                name="unique_user_in_team",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} -> {self.team} ({self.role})"


class Service(models.Model):
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    port = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class CompetitionSettings(models.Model):
    registration_open = models.BooleanField(default=True)
    registration_starts_at = models.DateTimeField(null=True, blank=True)
    registration_ends_at = models.DateTimeField(null=True, blank=True)
    reservation_required_for_registration = models.BooleanField(default=False)
    auto_approve_registrations = models.BooleanField(default=True)
    round_duration_minutes = models.PositiveIntegerField(default=15)
    round_break_minutes = models.PositiveIntegerField(default=5)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "competition settings"

    def __str__(self) -> str:
        return "Competition settings"

    @classmethod
    def get_solo(cls) -> "CompetitionSettings":
        settings_obj = cls.objects.order_by("id").first()
        if settings_obj is not None:
            return settings_obj
        return cls.objects.create()

    def is_registration_available(self, now=None) -> bool:
        now = now or timezone.now()
        if not self.registration_open:
            return False
        if self.registration_starts_at and now < self.registration_starts_at:
            return False
        if self.registration_ends_at and now > self.registration_ends_at:
            return False
        return True


class TeamReservation(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        CLAIMED = "claimed", "Claimed"

    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=64, unique=True)
    contact_email = models.EmailField()
    captain_username = models.CharField(max_length=150)
    token = models.CharField(max_length=32, unique=True)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
    )
    note = models.CharField(max_length=255, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.status})"


class Round(models.Model):
    class State(models.TextChoices):
        PLANNED = "planned", "Planned"
        RUNNING = "running", "Running"
        FINISHED = "finished", "Finished"

    number = models.PositiveIntegerField(unique=True)
    state = models.CharField(
        max_length=16,
        choices=State.choices,
        default=State.PLANNED,
    )
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-number"]

    def __str__(self) -> str:
        return f"Round {self.number}"


class Flag(models.Model):
    value = models.CharField(max_length=128, unique=True)
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="flags",
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="flags",
    )
    round = models.ForeignKey(
        Round,
        on_delete=models.CASCADE,
        related_name="flags",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-round__number", "service__name", "team__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["team", "service", "round"],
                name="unique_flag_per_team_service_round",
            )
        ]

    def __str__(self) -> str:
        return self.value


class ServiceStatus(models.Model):
    class Status(models.TextChoices):
        UP = "up", "Up"
        MUMBLE = "mumble", "Mumble"
        CORRUPT = "corrupt", "Corrupt"
        DOWN = "down", "Down"

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="service_statuses",
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="service_statuses",
    )
    round = models.ForeignKey(
        Round,
        on_delete=models.CASCADE,
        related_name="service_statuses",
    )
    status = models.CharField(max_length=16, choices=Status.choices)
    points_awarded = models.PositiveIntegerField(default=0)
    message = models.CharField(max_length=255, blank=True)
    reported_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-round__number", "team__name", "service__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["team", "service", "round"],
                name="unique_service_status_per_round",
            )
        ]

    @classmethod
    def suggested_points(cls, status: str) -> int:
        return {
            cls.Status.UP: 10,
            cls.Status.MUMBLE: 5,
            cls.Status.CORRUPT: 2,
            cls.Status.DOWN: 0,
        }.get(status, 0)

    def __str__(self) -> str:
        return f"{self.team} / {self.service} / round {self.round.number}"


class Submission(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"

    submitting_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="submitted_flags",
    )
    flag = models.ForeignKey(
        Flag,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="submissions",
    )
    submitted_value = models.CharField(max_length=128)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.PENDING,
    )
    points_awarded = models.PositiveIntegerField(default=0)
    message = models.CharField(max_length=255, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self) -> str:
        return f"{self.submitting_team} submission #{self.pk}"
