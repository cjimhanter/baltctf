from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from ctf.models import Flag, Round, Service, ServiceStatus, Submission, Team, TeamMember

User = get_user_model()
DEMO_USER_PASSWORD = "BaltCTFdemo123!"
DEMO_ADMIN_USERNAME = "admin"
DEMO_ADMIN_PASSWORD = "BaltCTFadmin123!"


TEAM_FIXTURES = [
    {
        "name": "Northern Lights",
        "slug": "northern-lights",
        "affiliation": "BSTU",
        "contact_email": "northern.lights@example.com",
    },
    {
        "name": "Amber Byte",
        "slug": "amber-byte",
        "affiliation": "BFU",
        "contact_email": "amber.byte@example.com",
    },
    {
        "name": "Zero Cool",
        "slug": "zero-cool",
        "affiliation": "ITMO",
        "contact_email": "zero.cool@example.com",
    },
    {
        "name": "Icebreakers",
        "slug": "icebreakers",
        "affiliation": "SPbPU",
        "contact_email": "icebreakers@example.com",
    },
]

SERVICE_FIXTURES = [
    {
        "name": "Atlas Board",
        "slug": "atlas-board",
        "description": "Web dashboard used as the vulnerable portal service.",
        "port": 8081,
    },
    {
        "name": "Signal API",
        "slug": "signal-api",
        "description": "Internal JSON API with intentionally weak access control.",
        "port": 8082,
    },
    {
        "name": "Cold Storage",
        "slug": "cold-storage",
        "description": "File storage service with simplified checker integration.",
        "port": 8083,
    },
]

ROUND_STATUS_FIXTURES = {
    1: {
        "northern-lights": {
            "atlas-board": ServiceStatus.Status.UP,
            "signal-api": ServiceStatus.Status.UP,
            "cold-storage": ServiceStatus.Status.MUMBLE,
        },
        "amber-byte": {
            "atlas-board": ServiceStatus.Status.UP,
            "signal-api": ServiceStatus.Status.CORRUPT,
            "cold-storage": ServiceStatus.Status.UP,
        },
        "zero-cool": {
            "atlas-board": ServiceStatus.Status.DOWN,
            "signal-api": ServiceStatus.Status.UP,
            "cold-storage": ServiceStatus.Status.UP,
        },
        "icebreakers": {
            "atlas-board": ServiceStatus.Status.UP,
            "signal-api": ServiceStatus.Status.MUMBLE,
            "cold-storage": ServiceStatus.Status.DOWN,
        },
    },
    2: {
        "northern-lights": {
            "atlas-board": ServiceStatus.Status.UP,
            "signal-api": ServiceStatus.Status.CORRUPT,
            "cold-storage": ServiceStatus.Status.UP,
        },
        "amber-byte": {
            "atlas-board": ServiceStatus.Status.UP,
            "signal-api": ServiceStatus.Status.UP,
            "cold-storage": ServiceStatus.Status.MUMBLE,
        },
        "zero-cool": {
            "atlas-board": ServiceStatus.Status.MUMBLE,
            "signal-api": ServiceStatus.Status.UP,
            "cold-storage": ServiceStatus.Status.UP,
        },
        "icebreakers": {
            "atlas-board": ServiceStatus.Status.UP,
            "signal-api": ServiceStatus.Status.DOWN,
            "cold-storage": ServiceStatus.Status.UP,
        },
    },
    3: {
        "northern-lights": {
            "atlas-board": ServiceStatus.Status.UP,
            "signal-api": ServiceStatus.Status.UP,
            "cold-storage": ServiceStatus.Status.UP,
        },
        "amber-byte": {
            "atlas-board": ServiceStatus.Status.UP,
            "signal-api": ServiceStatus.Status.MUMBLE,
            "cold-storage": ServiceStatus.Status.UP,
        },
        "zero-cool": {
            "atlas-board": ServiceStatus.Status.CORRUPT,
            "signal-api": ServiceStatus.Status.UP,
            "cold-storage": ServiceStatus.Status.UP,
        },
        "icebreakers": {
            "atlas-board": ServiceStatus.Status.UP,
            "signal-api": ServiceStatus.Status.UP,
            "cold-storage": ServiceStatus.Status.DOWN,
        },
    },
}


def make_flag_value(team_slug: str, service_slug: str, round_number: int) -> str:
    token = f"{team_slug}_{service_slug}_r{round_number}".replace("-", "_").upper()
    return f"BALTCTF{{{token}}}"


def build_team_user_specs(team_slug: str, affiliation: str) -> list[dict]:
    prefix = team_slug.replace("-", "_")
    return [
        {
            "username": f"{prefix}_captain",
            "role": TeamMember.Role.CAPTAIN,
            "email": f"{prefix}_captain@example.com",
            "first_name": affiliation,
            "last_name": "Captain",
        },
        {
            "username": f"{prefix}_player1",
            "role": TeamMember.Role.PLAYER,
            "email": f"{prefix}_player1@example.com",
            "first_name": affiliation,
            "last_name": "Player One",
        },
        {
            "username": f"{prefix}_player2",
            "role": TeamMember.Role.PLAYER,
            "email": f"{prefix}_player2@example.com",
            "first_name": affiliation,
            "last_name": "Player Two",
        },
    ]


class Command(BaseCommand):
    help = "Populate the database with demo teams, rounds, services, flags, and submissions."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing CTF data before seeding demo records.",
        )

    def handle(self, *args, **options):
        should_reset = options["reset"]

        if Team.objects.exists() and not should_reset:
            self.stdout.write(
                self.style.WARNING(
                    "CTF data already exists. Re-run with --reset to recreate demo fixtures."
                )
            )
            return

        with transaction.atomic():
            if should_reset:
                member_user_ids = list(
                    TeamMember.objects.values_list("user_id", flat=True)
                )
                TeamMember.objects.all().delete()
                User.objects.filter(id__in=member_user_ids).delete()
                Submission.objects.all().delete()
                ServiceStatus.objects.all().delete()
                Flag.objects.all().delete()
                Round.objects.all().delete()
                Service.objects.all().delete()
                Team.objects.all().delete()

            self._seed()

        self.stdout.write(self.style.SUCCESS("Demo data created successfully."))
        self.stdout.write(
            f"Teams: {Team.objects.count()}, services: {Service.objects.count()}, rounds: {Round.objects.count()}"
        )
        self.stdout.write(
            f"Demo user password for all seeded participants: {DEMO_USER_PASSWORD}"
        )
        self.stdout.write(
            f"Demo admin credentials: {DEMO_ADMIN_USERNAME} / {DEMO_ADMIN_PASSWORD}"
        )

    def _seed(self):
        now = timezone.now().replace(second=0, microsecond=0)

        admin_user, _ = User.objects.get_or_create(
            username=DEMO_ADMIN_USERNAME,
            defaults={
                "email": "admin@baltctf.local",
                "is_staff": True,
                "is_superuser": True,
                "first_name": "BaltCTF",
                "last_name": "Admin",
            },
        )
        admin_user.email = "admin@baltctf.local"
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.first_name = "BaltCTF"
        admin_user.last_name = "Admin"
        admin_user.set_password(DEMO_ADMIN_PASSWORD)
        admin_user.save()

        teams = {
            team.slug: team
            for team in [Team.objects.create(**team_data) for team_data in TEAM_FIXTURES]
        }
        team_users = {}
        for team_slug, team in teams.items():
            user_specs = build_team_user_specs(team_slug, team.affiliation or team.name)
            for user_spec in user_specs:
                user = User.objects.create_user(
                    username=user_spec["username"],
                    email=user_spec["email"],
                    password=DEMO_USER_PASSWORD,
                    first_name=user_spec["first_name"],
                    last_name=user_spec["last_name"],
                )
                TeamMember.objects.create(
                    user=user,
                    team=team,
                    role=user_spec["role"],
                )
                team_users[(team_slug, user_spec["username"])] = user

        services = {
            service.slug: service
            for service in [
                Service.objects.create(**service_data)
                for service_data in SERVICE_FIXTURES
            ]
        }

        round_fixtures = [
            {
                "number": 1,
                "state": Round.State.FINISHED,
                "started_at": now - timedelta(minutes=45),
                "finished_at": now - timedelta(minutes=30),
            },
            {
                "number": 2,
                "state": Round.State.FINISHED,
                "started_at": now - timedelta(minutes=30),
                "finished_at": now - timedelta(minutes=15),
            },
            {
                "number": 3,
                "state": Round.State.RUNNING,
                "started_at": now - timedelta(minutes=15),
                "finished_at": None,
            },
        ]

        rounds = {
            round_obj.number: round_obj
            for round_obj in [
                Round.objects.create(**round_data) for round_data in round_fixtures
            ]
        }

        flags = {}
        for round_number, round_obj in rounds.items():
            for team_slug, team in teams.items():
                for service_slug, service in services.items():
                    flag = Flag.objects.create(
                        value=make_flag_value(team_slug, service_slug, round_number),
                        team=team,
                        service=service,
                        round=round_obj,
                        expires_at=(
                            round_obj.finished_at + timedelta(minutes=15)
                            if round_obj.finished_at
                            else None
                        ),
                    )
                    flags[(team_slug, service_slug, round_number)] = flag

        for round_number, team_map in ROUND_STATUS_FIXTURES.items():
            for team_slug, service_map in team_map.items():
                for service_slug, status in service_map.items():
                    ServiceStatus.objects.create(
                        team=teams[team_slug],
                        service=services[service_slug],
                        round=rounds[round_number],
                        status=status,
                        points_awarded=ServiceStatus.suggested_points(status),
                        message=f"{status.title()} during automated checker pass.",
                    )

        submissions = [
            {
                "team_slug": "amber-byte",
                "submitted_by": "amber_byte_player1",
                "target": ("northern-lights", "atlas-board", 1),
                "status": Submission.Status.ACCEPTED,
                "points": 25,
                "message": "Exploit chain against dashboard upload endpoint.",
                "submitted_at": rounds[1].finished_at - timedelta(minutes=4),
            },
            {
                "team_slug": "zero-cool",
                "submitted_by": "zero_cool_player1",
                "target": ("amber-byte", "signal-api", 1),
                "status": Submission.Status.ACCEPTED,
                "points": 25,
                "message": "Recovered API flag through predictable token flow.",
                "submitted_at": rounds[1].finished_at - timedelta(minutes=2),
            },
            {
                "team_slug": "icebreakers",
                "submitted_by": "icebreakers_player1",
                "target": ("zero-cool", "cold-storage", 1),
                "status": Submission.Status.REJECTED,
                "points": 0,
                "message": "Duplicate or expired flag.",
                "submitted_at": rounds[1].finished_at - timedelta(minutes=1),
            },
            {
                "team_slug": "northern-lights",
                "submitted_by": "northern_lights_captain",
                "target": ("icebreakers", "atlas-board", 2),
                "status": Submission.Status.ACCEPTED,
                "points": 25,
                "message": "Stored XSS chain captured the portal flag.",
                "submitted_at": rounds[2].finished_at - timedelta(minutes=5),
            },
            {
                "team_slug": "amber-byte",
                "submitted_by": "amber_byte_player2",
                "target": ("zero-cool", "cold-storage", 2),
                "status": Submission.Status.ACCEPTED,
                "points": 25,
                "message": "Archive traversal reached the round secret.",
                "submitted_at": rounds[2].finished_at - timedelta(minutes=3),
            },
            {
                "team_slug": "zero-cool",
                "submitted_by": "zero_cool_captain",
                "target": ("icebreakers", "signal-api", 2),
                "status": Submission.Status.REJECTED,
                "points": 0,
                "message": "Malformed flag format.",
                "submitted_at": rounds[2].finished_at - timedelta(minutes=1),
            },
            {
                "team_slug": "northern-lights",
                "submitted_by": "northern_lights_player1",
                "target": ("amber-byte", "signal-api", 3),
                "status": Submission.Status.ACCEPTED,
                "points": 25,
                "message": "Leaked session token reused during active round.",
                "submitted_at": now - timedelta(minutes=9),
            },
            {
                "team_slug": "icebreakers",
                "submitted_by": "icebreakers_captain",
                "target": ("northern-lights", "cold-storage", 3),
                "status": Submission.Status.ACCEPTED,
                "points": 25,
                "message": "Weak file permissions exposed the active flag.",
                "submitted_at": now - timedelta(minutes=6),
            },
            {
                "team_slug": "amber-byte",
                "submitted_by": "amber_byte_captain",
                "target": ("zero-cool", "atlas-board", 3),
                "status": Submission.Status.REJECTED,
                "points": 0,
                "message": "Service patched before flag extraction completed.",
                "submitted_at": now - timedelta(minutes=3),
            },
        ]

        for submission_data in submissions:
            team = teams[submission_data["team_slug"]]
            target_key = submission_data["target"]
            flag = flags[target_key]

            submission = Submission.objects.create(
                submitting_team=team,
                submitted_by=team_users[(submission_data["team_slug"], submission_data["submitted_by"])],
                flag=flag if submission_data["status"] == Submission.Status.ACCEPTED else None,
                submitted_value=(
                    flag.value
                    if submission_data["status"] == Submission.Status.ACCEPTED
                    else f"INVALID-{flag.value}"
                ),
                status=submission_data["status"],
                points_awarded=submission_data["points"],
                message=submission_data["message"],
                processed_at=submission_data["submitted_at"] + timedelta(seconds=20),
            )
            Submission.objects.filter(pk=submission.pk).update(
                submitted_at=submission_data["submitted_at"],
                processed_at=submission_data["submitted_at"] + timedelta(seconds=20),
            )
