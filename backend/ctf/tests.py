from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.authtoken.models import Token

from .checkers import CheckerCorruptError
from .competition import run_checker_tick
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
from .views import MAX_TEAM_MEMBERS

User = get_user_model()


class BaseApiTestCase(TestCase):
    def setUp(self):
        self.now = timezone.now()

        self.red_team = Team.objects.create(
            name="Red Team",
            slug="red-team",
            affiliation="BSTU",
            contact_email="red@example.com",
        )
        self.blue_team = Team.objects.create(
            name="Blue Team",
            slug="blue-team",
            affiliation="BFU",
            contact_email="blue@example.com",
        )
        self.service = Service.objects.create(
            name="Atlas Board",
            slug="atlas-board",
            description="Demo service",
            port=8081,
        )
        self.round = Round.objects.create(
            number=7,
            state=Round.State.RUNNING,
            started_at=self.now - timedelta(minutes=10),
        )
        self.red_flag = Flag.objects.create(
            value="BALTCTF{RED_TEAM_ATLAS_BOARD_R7}",
            team=self.red_team,
            service=self.service,
            round=self.round,
            expires_at=self.now + timedelta(minutes=5),
        )
        self.blue_flag = Flag.objects.create(
            value="BALTCTF{BLUE_TEAM_ATLAS_BOARD_R7}",
            team=self.blue_team,
            service=self.service,
            round=self.round,
            expires_at=self.now + timedelta(minutes=5),
        )

        self.red_user = User.objects.create_user(
            username="red_captain",
            password="VeryStrongPass123!",
            email="red_captain@example.com",
        )
        self.blue_user = User.objects.create_user(
            username="blue_player",
            password="VeryStrongPass123!",
            email="blue_player@example.com",
        )
        self.red_membership = TeamMember.objects.create(
            user=self.red_user,
            team=self.red_team,
            role=TeamMember.Role.CAPTAIN,
        )
        self.blue_membership = TeamMember.objects.create(
            user=self.blue_user,
            team=self.blue_team,
            role=TeamMember.Role.PLAYER,
        )
        self.red_token = Token.objects.create(user=self.red_user)
        self.blue_token = Token.objects.create(user=self.blue_user)
        self.admin_user = User.objects.create_user(
            username="admin",
            password="VeryStrongPass123!",
            email="admin@example.com",
            is_staff=True,
            is_superuser=True,
        )
        self.admin_token = Token.objects.create(user=self.admin_user)

        ServiceStatus.objects.create(
            team=self.red_team,
            service=self.service,
            round=self.round,
            status=ServiceStatus.Status.UP,
            points_awarded=10,
        )
        ServiceStatus.objects.create(
            team=self.blue_team,
            service=self.service,
            round=self.round,
            status=ServiceStatus.Status.MUMBLE,
            points_awarded=5,
        )
        Submission.objects.create(
            submitting_team=self.blue_team,
            submitted_by=self.blue_user,
            flag=self.red_flag,
            submitted_value=self.red_flag.value,
            status=Submission.Status.ACCEPTED,
            points_awarded=25,
        )


class DashboardApiTests(BaseApiTestCase):
    def test_summary_endpoint_reports_counts(self):
        response = self.client.get(reverse("summary"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertEqual(payload["team_count"], 2)
        self.assertEqual(payload["service_count"], 1)
        self.assertEqual(payload["round_count"], 1)
        self.assertEqual(payload["accepted_submissions_count"], 1)
        self.assertEqual(payload["registered_users_count"], 2)
        self.assertEqual(payload["current_round_number"], 7)
        self.assertEqual(payload["attack_points_total"], 25)
        self.assertEqual(payload["defense_points_total"], 15)
        self.assertEqual(payload["checker_status_count"], 2)
        self.assertEqual(payload["acceptance_rate"], 100)

    def test_scoreboard_endpoint_orders_by_total_points(self):
        response = self.client.get(reverse("scoreboard"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertEqual(payload["current_round"]["number"], 7)
        self.assertEqual(payload["scoreboard"][0]["team"]["slug"], "blue-team")
        self.assertEqual(payload["scoreboard"][0]["total_points"], 30)
        self.assertEqual(payload["scoreboard"][0]["attack_points"], 25)
        self.assertEqual(payload["scoreboard"][0]["defense_points"], 5)
        self.assertEqual(payload["scoreboard"][0]["accepted_submission_count"], 1)
        self.assertEqual(payload["scoreboard"][0]["defense_check_count"], 1)
        self.assertEqual(payload["scoreboard"][0]["service_health"]["mumble"], 1)
        self.assertEqual(payload["scoreboard"][1]["team"]["slug"], "red-team")
        self.assertEqual(payload["scoreboard"][1]["service_breakdown"][0]["status"], "up")
        self.assertEqual(payload["summary"]["attack_points_total"], 25)
        self.assertEqual(payload["service_stats"][0]["checker_status_count"], 2)

    def test_dashboard_endpoint_includes_recent_activity(self):
        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertEqual(payload["summary"]["team_count"], 2)
        self.assertEqual(payload["services"][0]["slug"], "atlas-board")
        self.assertEqual(payload["recent_activity"][0]["service"]["slug"], "atlas-board")
        self.assertEqual(payload["submission_history"][0]["round"]["number"], 7)
        self.assertEqual(payload["service_stats"][0]["uptime_percent"], 50)
        self.assertEqual(payload["service_status_history"][0]["round"]["number"], 7)
        self.assertEqual(
            payload["service_status_history"][0]["services"][0]["status_counts"]["up"],
            1,
        )
        self.assertEqual(payload["recent_rounds"][0]["attack_points"], 25)
        self.assertEqual(payload["recent_activity"][0]["submitted_by"]["username"], "blue_player")

    def test_service_status_endpoint_returns_team_matrix(self):
        response = self.client.get(reverse("service-status"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertEqual(payload["current_round"]["number"], 7)
        self.assertEqual(payload["teams"][0]["services"][0]["service"]["slug"], "atlas-board")
        self.assertIn(payload["teams"][0]["services"][0]["status"], {"up", "mumble"})
        self.assertEqual(payload["summary"]["checked_status_count"], 2)
        self.assertEqual(payload["summary"]["status_counts"]["unknown"], 0)
        self.assertEqual(payload["history"][0]["services"][0]["checked_count"], 2)


class SeedDemoDataCommandTests(TestCase):
    def test_reset_removes_orphan_demo_users_and_can_run_repeatedly(self):
        User.objects.create_user(
            username="northern_lights_captain",
            password="old-demo-password",
            email="orphan@example.com",
        )

        call_command("seed_demo_data", reset=True, verbosity=0)
        call_command("seed_demo_data", reset=True, verbosity=0)

        self.assertEqual(
            User.objects.filter(username="northern_lights_captain").count(),
            1,
        )
        self.assertEqual(Team.objects.count(), 4)
        self.assertEqual(Service.objects.count(), 3)
        self.assertEqual(Round.objects.count(), 3)
        self.assertEqual(TeamMember.objects.count(), 12)
        self.assertTrue(
            TeamMember.objects.filter(
                user__username="northern_lights_captain",
                team__slug="northern-lights",
                role=TeamMember.Role.CAPTAIN,
            ).exists()
        )


class AuthApiTests(TestCase):
    def test_registration_settings_and_reservation_endpoints(self):
        settings_obj = CompetitionSettings.get_solo()
        settings_obj.registration_open = True
        settings_obj.reservation_required_for_registration = False
        settings_obj.save()

        settings_response = self.client.get(reverse("registration-settings"))

        self.assertEqual(settings_response.status_code, 200)
        self.assertTrue(settings_response.json()["registration_available"])

        reservation_response = self.client.post(
            reverse("team-reservation-create"),
            data={
                "team_name": "Polar Owls",
                "captain_username": "polar_captain",
                "contact_email": "polar@example.com",
            },
            content_type="application/json",
        )

        self.assertEqual(reservation_response.status_code, 201)
        payload = reservation_response.json()
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["reservation"]["status"], TeamReservation.Status.PENDING)
        self.assertEqual(TeamReservation.objects.count(), 1)

    def test_register_endpoint_creates_team_members_and_returns_token(self):
        response = self.client.post(
            reverse("register"),
            data={
                "team_name": "Aurora",
                "affiliation": "BFU",
                "contact_email": "aurora@example.com",
                "captain": {
                    "username": "aurora_captain",
                    "password": "VeryStrongPass123!",
                    "email": "captain@aurora.example.com",
                    "first_name": "Alice",
                    "last_name": "Captain",
                },
                "participants": [
                    {
                        "username": "aurora_player",
                        "password": "VeryStrongPass123!",
                        "email": "player@aurora.example.com",
                        "first_name": "Bob",
                        "last_name": "Player",
                    }
                ],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        payload = response.json()

        self.assertTrue(payload["ok"])
        self.assertTrue(payload["authenticated"])
        self.assertEqual(payload["team"]["slug"], "aurora")
        self.assertEqual(len(payload["members"]), 2)
        self.assertTrue(Token.objects.filter(key=payload["token"]).exists())
        self.assertEqual(Team.objects.count(), 1)
        self.assertEqual(TeamMember.objects.count(), 2)

    def test_register_requires_approved_reservation_when_enabled(self):
        settings_obj = CompetitionSettings.get_solo()
        settings_obj.registration_open = True
        settings_obj.reservation_required_for_registration = True
        settings_obj.auto_approve_registrations = False
        settings_obj.save()

        rejected_response = self.client.post(
            reverse("register"),
            data={
                "team_name": "Aurora",
                "contact_email": "aurora@example.com",
                "captain": {
                    "username": "aurora_captain",
                    "password": "VeryStrongPass123!",
                    "email": "captain@aurora.example.com",
                },
                "participants": [],
            },
            content_type="application/json",
        )

        self.assertEqual(rejected_response.status_code, 400)
        self.assertEqual(
            rejected_response.json()["message"],
            "An approved reservation token is required for registration.",
        )

        reservation = TeamReservation.objects.create(
            name="Aurora",
            slug="aurora",
            contact_email="aurora@example.com",
            captain_username="aurora_captain",
            token="approved-token-123",
            status=TeamReservation.Status.APPROVED,
            expires_at=timezone.now() + timedelta(days=1),
        )

        accepted_response = self.client.post(
            reverse("register"),
            data={
                "team_name": "Aurora",
                "team_slug": "aurora",
                "contact_email": "aurora@example.com",
                "reservation_token": reservation.token,
                "captain": {
                    "username": "aurora_captain",
                    "password": "VeryStrongPass123!",
                    "email": "captain@aurora.example.com",
                },
                "participants": [],
            },
            content_type="application/json",
        )

        self.assertEqual(accepted_response.status_code, 201)
        payload = accepted_response.json()
        self.assertEqual(payload["team"]["moderation_status"], Team.ModerationStatus.PENDING)
        self.assertEqual(
            payload["message"],
            "Team registered and is waiting for admin approval.",
        )
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, TeamReservation.Status.CLAIMED)

    def test_register_is_blocked_when_registration_window_closed(self):
        settings_obj = CompetitionSettings.get_solo()
        settings_obj.registration_open = False
        settings_obj.save(update_fields=["registration_open"])

        response = self.client.post(
            reverse("register"),
            data={
                "team_name": "Closed Window",
                "captain": {
                    "username": "closed_captain",
                    "password": "VeryStrongPass123!",
                    "email": "closed@example.com",
                },
                "participants": [],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["message"], "Registration is currently closed.")

    def test_login_and_me_endpoints_return_team_context(self):
        team = Team.objects.create(
            name="North",
            slug="north",
            affiliation="BSTU",
        )
        user = User.objects.create_user(
            username="north_captain",
            password="VeryStrongPass123!",
            email="north@example.com",
            first_name="Nora",
        )
        TeamMember.objects.create(
            user=user,
            team=team,
            role=TeamMember.Role.CAPTAIN,
        )

        login_response = self.client.post(
            reverse("login"),
            data={"username": "north_captain", "password": "VeryStrongPass123!"},
            content_type="application/json",
        )

        self.assertEqual(login_response.status_code, 200)
        token = login_response.json()["token"]

        me_response = self.client.get(
            reverse("me"),
            HTTP_AUTHORIZATION=f"Token {token}",
        )

        self.assertEqual(me_response.status_code, 200)
        me_payload = me_response.json()
        self.assertTrue(me_payload["authenticated"])
        self.assertEqual(me_payload["team"]["slug"], "north")
        self.assertEqual(me_payload["membership"]["role"], TeamMember.Role.CAPTAIN)

    def test_admin_user_without_team_can_fetch_me(self):
        user = User.objects.create_user(
            username="operator",
            password="VeryStrongPass123!",
            email="operator@example.com",
            is_staff=True,
        )
        token = Token.objects.create(user=user)

        me_response = self.client.get(
            reverse("me"),
            HTTP_AUTHORIZATION=f"Token {token.key}",
        )

        self.assertEqual(me_response.status_code, 200)
        payload = me_response.json()
        self.assertTrue(payload["authenticated"])
        self.assertIsNone(payload["team"])
        self.assertTrue(payload["user"]["is_staff"])


class AdminApiTests(BaseApiTestCase):
    def test_admin_state_requires_staff_and_returns_snapshot(self):
        forbidden_response = self.client.get(
            reverse("admin-state"),
            HTTP_AUTHORIZATION=f"Token {self.blue_token.key}",
        )
        self.assertEqual(forbidden_response.status_code, 403)

        response = self.client.get(
            reverse("admin-state"),
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["teams"][0]["member_count"], 1)
        self.assertEqual(payload["services"][0]["slug"], "atlas-board")
        self.assertEqual(payload["rounds"][0]["number"], 7)
        self.assertIn("settings", payload)
        self.assertIn("reservations", payload)
        self.assertEqual(payload["current_status_summary"]["up"], 1)
        self.assertEqual(payload["current_status_summary"]["mumble"], 1)
        self.assertIsNotNone(payload["latest_checker_report_at"])
        diagnostics = payload["current_checker_diagnostics"]
        self.assertEqual(diagnostics["round"]["number"], 7)
        self.assertEqual(diagnostics["active_team_count"], 2)
        self.assertEqual(diagnostics["active_service_count"], 1)
        self.assertEqual(diagnostics["expected_status_count"], 2)
        self.assertEqual(diagnostics["checked_status_count"], 2)
        self.assertEqual(diagnostics["unknown_status_count"], 0)
        self.assertEqual(diagnostics["issue_count"], 1)
        self.assertEqual(diagnostics["status_counts"]["mumble"], 1)
        self.assertEqual(diagnostics["status_counts"]["unknown"], 0)
        self.assertEqual(diagnostics["latest_issues"][0]["status"], ServiceStatus.Status.MUMBLE)
        self.assertEqual(diagnostics["latest_issues"][0]["team"]["slug"], "blue-team")
        self.assertEqual(payload["recent_submissions"][0]["submitting_team"]["slug"], "blue-team")
        self.assertEqual(payload["recent_submissions"][0]["round"]["number"], 7)

    def test_admin_can_update_settings_and_schedule_rounds(self):
        response = self.client.post(
            reverse("admin-update-settings"),
            data={
                "registration_open": True,
                "reservation_required_for_registration": True,
                "auto_approve_registrations": False,
                "round_duration_minutes": 20,
                "round_break_minutes": 3,
                "registration_starts_at": (self.now + timedelta(hours=1)).isoformat(),
                "registration_ends_at": (self.now + timedelta(days=1)).isoformat(),
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["settings"]["reservation_required_for_registration"])
        self.assertFalse(payload["settings"]["auto_approve_registrations"])
        self.assertEqual(payload["settings"]["round_duration_minutes"], 20)
        self.assertEqual(payload["settings"]["round_break_minutes"], 3)

        schedule_response = self.client.post(
            reverse("admin-schedule-rounds"),
            data={
                "count": 2,
                "start_at": (self.now + timedelta(hours=2)).isoformat(),
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
        )

        self.assertEqual(schedule_response.status_code, 201)
        schedule_payload = schedule_response.json()
        self.assertEqual(len(schedule_payload["rounds"]), 2)
        self.assertEqual(schedule_payload["rounds"][0]["state"], Round.State.PLANNED)
        self.assertEqual(schedule_payload["rounds"][0]["number"], 8)
        self.assertEqual(schedule_payload["rounds"][1]["number"], 9)

    def test_admin_can_moderate_reservations(self):
        pending = TeamReservation.objects.create(
            name="Polar Owls",
            slug="polar-owls",
            contact_email="polar@example.com",
            captain_username="polar_captain",
            token="reserve-approve-1",
            status=TeamReservation.Status.PENDING,
            expires_at=self.now + timedelta(days=7),
        )
        to_reject = TeamReservation.objects.create(
            name="Gray Bears",
            slug="gray-bears",
            contact_email="gray@example.com",
            captain_username="gray_captain",
            token="reserve-reject-1",
            status=TeamReservation.Status.PENDING,
            expires_at=self.now + timedelta(days=7),
        )

        approve_response = self.client.post(
            reverse("admin-approve-reservation", kwargs={"reservation_id": pending.id}),
            data={},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
        )

        self.assertEqual(approve_response.status_code, 200)
        pending.refresh_from_db()
        self.assertEqual(pending.status, TeamReservation.Status.APPROVED)

        reject_response = self.client.post(
            reverse("admin-reject-reservation", kwargs={"reservation_id": to_reject.id}),
            data={"note": "Duplicate application."},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
        )

        self.assertEqual(reject_response.status_code, 200)
        to_reject.refresh_from_db()
        self.assertEqual(to_reject.status, TeamReservation.Status.REJECTED)
        self.assertEqual(to_reject.note, "Duplicate application.")

    def test_admin_can_create_and_manage_round_lifecycle(self):
        create_response = self.client.post(
            reverse("admin-create-round"),
            data={},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
        )

        self.assertEqual(create_response.status_code, 201)
        round_id = create_response.json()["round"]["id"]

        start_response = self.client.post(
            reverse("admin-start-round", kwargs={"round_id": round_id}),
            data={},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
        )

        self.assertEqual(start_response.status_code, 409)

        finish_current = self.client.post(
            reverse("admin-finish-round", kwargs={"round_id": self.round.id}),
            data={},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
        )
        self.assertEqual(finish_current.status_code, 200)

        start_response = self.client.post(
            reverse("admin-start-round", kwargs={"round_id": round_id}),
            data={},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
        )

        self.assertEqual(start_response.status_code, 200)
        self.assertGreater(start_response.json()["created_flags"], 0)

        generate_response = self.client.post(
            reverse("admin-generate-flags", kwargs={"round_id": round_id}),
            data={},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
        )

        self.assertEqual(generate_response.status_code, 200)
        self.assertEqual(generate_response.json()["created_flags"], 0)

    def test_admin_can_trigger_checker_tick_for_running_round(self):
        ServiceStatus.objects.filter(round=self.round).delete()

        response = self.client.post(
            reverse("admin-checker-tick"),
            data={},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["checker_tick"]["round"]["number"], 7)
        self.assertEqual(payload["checker_tick"]["created_flags"], 0)
        self.assertEqual(payload["checker_tick"]["statuses_processed"], 2)
        self.assertEqual(sum(payload["checker_tick"]["status_breakdown"].values()), 2)
        self.assertEqual(ServiceStatus.objects.filter(round=self.round).count(), 2)
        self.assertIsNotNone(payload["admin_state"]["latest_checker_report_at"])
        self.assertEqual(
            payload["admin_state"]["current_checker_diagnostics"][
                "expected_status_count"
            ],
            2,
        )
        self.assertEqual(
            payload["admin_state"]["current_checker_diagnostics"][
                "checked_status_count"
            ],
            2,
        )
        self.assertEqual(
            payload["admin_state"]["current_checker_diagnostics"][
                "unknown_status_count"
            ],
            0,
        )
        self.assertEqual(
            sum(payload["admin_state"]["current_status_summary"].values()),
            2,
        )

    @patch("ctf.competition.run_service_checker")
    def test_checker_tick_dispatches_service_specific_checkers(self, mock_run_service_checker):
        ServiceStatus.objects.filter(round=self.round).delete()
        api_service = Service.objects.create(
            name="Signal API",
            slug="signal-api",
            description="API service",
            port=8082,
        )
        storage_service = Service.objects.create(
            name="Cold Storage",
            slug="cold-storage",
            description="Storage service",
            port=8083,
        )
        Flag.objects.create(
            value="BALTCTF{RED_SIGNAL}",
            team=self.red_team,
            service=api_service,
            round=self.round,
            expires_at=self.now + timedelta(minutes=5),
        )
        Flag.objects.create(
            value="BALTCTF{BLUE_SIGNAL}",
            team=self.blue_team,
            service=api_service,
            round=self.round,
            expires_at=self.now + timedelta(minutes=5),
        )
        Flag.objects.create(
            value="BALTCTF{RED_STORAGE}",
            team=self.red_team,
            service=storage_service,
            round=self.round,
            expires_at=self.now + timedelta(minutes=5),
        )
        Flag.objects.create(
            value="BALTCTF{BLUE_STORAGE}",
            team=self.blue_team,
            service=storage_service,
            round=self.round,
            expires_at=self.now + timedelta(minutes=5),
        )
        mock_run_service_checker.side_effect = (
            lambda service_slug, **kwargs: f"{service_slug} ok for {kwargs['team'].slug}"
        )

        result = run_checker_tick(self.round)

        self.assertEqual(result.statuses_processed, 6)
        self.assertEqual(result.status_breakdown[ServiceStatus.Status.UP], 6)
        self.assertEqual(ServiceStatus.objects.filter(round=self.round).count(), 6)
        self.assertEqual(
            {call.args[0] for call in mock_run_service_checker.call_args_list},
            {"atlas-board", "signal-api", "cold-storage"},
        )

    @patch("ctf.competition.run_service_checker")
    def test_checker_tick_maps_checker_failures_to_statuses(self, mock_run_service_checker):
        ServiceStatus.objects.filter(round=self.round).delete()

        def side_effect(service_slug, **kwargs):
            if service_slug == "atlas-board" and kwargs["team"].slug == "red-team":
                raise CheckerCorruptError("Flag body mismatched.")
            return f"{service_slug} ok"

        mock_run_service_checker.side_effect = side_effect

        result = run_checker_tick(self.round)

        self.assertEqual(result.status_breakdown[ServiceStatus.Status.CORRUPT], 1)
        self.assertEqual(result.status_breakdown[ServiceStatus.Status.UP], 1)
        red_status = ServiceStatus.objects.get(
            round=self.round,
            team=self.red_team,
            service=self.service,
        )
        self.assertEqual(red_status.status, ServiceStatus.Status.CORRUPT)
        self.assertEqual(red_status.message, "Flag body mismatched.")

    def test_admin_checker_tick_requires_running_round(self):
        self.round.state = Round.State.FINISHED
        self.round.finished_at = self.now
        self.round.save(update_fields=["state", "finished_at"])

        response = self.client.post(
            reverse("admin-checker-tick"),
            data={},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            response.json()["message"],
            "There is no running round for the checker tick.",
        )

    def test_admin_can_create_update_and_delete_teams_and_services(self):
        team_response = self.client.post(
            reverse("admin-create-team"),
            data={
                "name": "Aurora",
                "affiliation": "BFU",
                "contact_email": "aurora@example.com",
                "moderation_status": Team.ModerationStatus.PENDING,
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
        )
        self.assertEqual(team_response.status_code, 201)
        team_id = team_response.json()["team"]["id"]
        self.assertEqual(
            team_response.json()["team"]["moderation_status"],
            Team.ModerationStatus.PENDING,
        )

        update_team_response = self.client.post(
            reverse("admin-update-team", kwargs={"team_id": team_id}),
            data={
                "name": "Aurora Prime",
                "affiliation": "BFU",
                "contact_email": "aurora-prime@example.com",
                "is_active": False,
                "moderation_status": Team.ModerationStatus.SUSPENDED,
                "moderation_note": "Under review",
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
        )
        self.assertEqual(update_team_response.status_code, 200)
        self.assertFalse(update_team_response.json()["team"]["is_active"])
        self.assertEqual(
            update_team_response.json()["team"]["moderation_status"],
            Team.ModerationStatus.SUSPENDED,
        )

        service_response = self.client.post(
            reverse("admin-create-service"),
            data={
                "name": "Storage 2",
                "description": "Extra storage service",
                "port": 8084,
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
        )
        self.assertEqual(service_response.status_code, 201)
        service_id = service_response.json()["service"]["id"]

        delete_service_response = self.client.post(
            reverse("admin-delete-service", kwargs={"service_id": service_id}),
            data={},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
        )
        self.assertEqual(delete_service_response.status_code, 200)

        delete_team_response = self.client.post(
            reverse("admin-delete-team", kwargs={"team_id": team_id}),
            data={},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.admin_token.key}",
        )
        self.assertEqual(delete_team_response.status_code, 200)


class SubmissionApiTests(BaseApiTestCase):
    def test_submit_flag_accepts_valid_enemy_flag(self):
        response = self.client.post(
            reverse("submit-flag"),
            data={"flag": self.blue_flag.value},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.blue_token.key}",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["message"], "You cannot submit your own team's flag.")

        accepted_response = self.client.post(
            reverse("submit-flag"),
            data={"flag": self.red_flag.value.replace("RED_TEAM", "RED2_TEAM")},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.blue_token.key}",
        )

        self.assertEqual(accepted_response.status_code, 400)
        self.assertEqual(accepted_response.json()["message"], "Unknown flag.")

        yellow_user = User.objects.create_user(
            username="yellow_player",
            password="VeryStrongPass123!",
            email="yellow@example.com",
        )
        yellow_team = Team.objects.create(
            name="Yellow Team",
            slug="yellow-team",
            affiliation="ITMO",
        )
        TeamMember.objects.create(
            user=yellow_user,
            team=yellow_team,
            role=TeamMember.Role.PLAYER,
        )
        yellow_token = Token.objects.create(user=yellow_user)

        response = self.client.post(
            reverse("submit-flag"),
            data={"flag": self.blue_flag.value},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {yellow_token.key}",
        )

        self.assertEqual(response.status_code, 201)
        payload = response.json()

        self.assertTrue(payload["ok"])
        self.assertEqual(payload["submission"]["status"], Submission.Status.ACCEPTED)
        self.assertEqual(payload["submission"]["submitted_by"]["username"], "yellow_player")
        self.assertEqual(payload["submission"]["points_awarded"], 25)

    def test_submit_flag_rejects_duplicate_success(self):
        yellow_user = User.objects.create_user(
            username="yellow_player",
            password="VeryStrongPass123!",
            email="yellow@example.com",
        )
        yellow_team = Team.objects.create(
            name="Yellow Team",
            slug="yellow-team",
            affiliation="ITMO",
        )
        TeamMember.objects.create(
            user=yellow_user,
            team=yellow_team,
            role=TeamMember.Role.PLAYER,
        )
        yellow_token = Token.objects.create(user=yellow_user)

        response = self.client.post(
            reverse("submit-flag"),
            data={"flag": self.red_flag.value},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {yellow_token.key}",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["message"],
            "This flag has already been submitted successfully.",
        )

    def test_submit_flag_rejects_non_current_round_flag(self):
        old_round = Round.objects.create(
            number=6,
            state=Round.State.FINISHED,
            started_at=self.now - timedelta(hours=1),
            finished_at=self.now - timedelta(minutes=30),
        )
        old_flag = Flag.objects.create(
            value="BALTCTF{OLD_FLAG}",
            team=self.red_team,
            service=self.service,
            round=old_round,
        )
        yellow_user = User.objects.create_user(
            username="yellow_player",
            password="VeryStrongPass123!",
            email="yellow@example.com",
        )
        yellow_team = Team.objects.create(
            name="Yellow Team",
            slug="yellow-team",
            affiliation="ITMO",
        )
        TeamMember.objects.create(
            user=yellow_user,
            team=yellow_team,
            role=TeamMember.Role.PLAYER,
        )
        yellow_token = Token.objects.create(user=yellow_user)

        response = self.client.post(
            reverse("submit-flag"),
            data={"flag": old_flag.value},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {yellow_token.key}",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["message"],
            "This flag is not valid for the current round.",
        )

    def test_submit_flag_requires_authentication(self):
        response = self.client.post(
            reverse("submit-flag"),
            data={"flag": self.red_flag.value},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)


class TeamManagementApiTests(BaseApiTestCase):
    def test_captain_can_update_team_profile_and_manage_members(self):
        update_response = self.client.post(
            reverse("team-update"),
            data={
                "affiliation": "BSTU Finalists",
                "contact_email": "new-red@example.com",
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.red_token.key}",
        )

        self.assertEqual(update_response.status_code, 200)
        self.red_team.refresh_from_db()
        self.assertEqual(self.red_team.affiliation, "BSTU Finalists")
        self.assertEqual(self.red_team.contact_email, "new-red@example.com")

        add_response = self.client.post(
            reverse("team-add-member"),
            data={
                "username": "red_player2",
                "password": "VeryStrongPass123!",
                "email": "red_player2@example.com",
                "first_name": "Rita",
                "last_name": "Player",
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.red_token.key}",
        )

        self.assertEqual(add_response.status_code, 201)
        new_member = TeamMember.objects.get(user__username="red_player2")
        self.assertEqual(new_member.role, TeamMember.Role.PLAYER)
        self.assertEqual(len(add_response.json()["members"]), 2)

        promote_response = self.client.post(
            reverse("team-update-member-role", kwargs={"user_id": new_member.user_id}),
            data={"role": TeamMember.Role.CAPTAIN},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.red_token.key}",
        )

        self.assertEqual(promote_response.status_code, 200)
        new_member.refresh_from_db()
        self.assertEqual(new_member.role, TeamMember.Role.CAPTAIN)

        remove_response = self.client.post(
            reverse("team-remove-member", kwargs={"user_id": new_member.user_id}),
            data={},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.red_token.key}",
        )

        self.assertEqual(remove_response.status_code, 200)
        self.assertFalse(User.objects.filter(username="red_player2").exists())
        self.assertEqual(len(remove_response.json()["members"]), 1)

    def test_team_management_requires_captain_role(self):
        response = self.client.post(
            reverse("team-add-member"),
            data={
                "username": "blue_player2",
                "password": "VeryStrongPass123!",
                "email": "blue_player2@example.com",
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.blue_token.key}",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["message"], "Captain role is required for this action.")

    def test_team_management_protects_last_captain_and_self_removal(self):
        remove_self_response = self.client.post(
            reverse("team-remove-member", kwargs={"user_id": self.red_user.id}),
            data={},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.red_token.key}",
        )

        self.assertEqual(remove_self_response.status_code, 409)
        self.assertEqual(
            remove_self_response.json()["message"],
            "You cannot remove your own account through the team management API.",
        )

        demote_last_captain_response = self.client.post(
            reverse("team-update-member-role", kwargs={"user_id": self.red_user.id}),
            data={"role": TeamMember.Role.PLAYER},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.red_token.key}",
        )

        self.assertEqual(demote_last_captain_response.status_code, 409)
        self.assertEqual(
            demote_last_captain_response.json()["message"],
            "Team must always have at least one captain.",
        )

    def test_team_add_member_respects_member_limit(self):
        for index in range(MAX_TEAM_MEMBERS - 1):
            user = User.objects.create_user(
                username=f"red_extra_{index}",
                password="VeryStrongPass123!",
            )
            TeamMember.objects.create(
                user=user,
                team=self.red_team,
                role=TeamMember.Role.PLAYER,
            )

        response = self.client.post(
            reverse("team-add-member"),
            data={
                "username": "overflow_member",
                "password": "VeryStrongPass123!",
                "email": "overflow@example.com",
            },
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.red_token.key}",
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            response.json()["message"],
            f"Team size is limited to {MAX_TEAM_MEMBERS} members.",
        )
