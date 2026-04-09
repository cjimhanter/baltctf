import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ctf", "0002_teammember_team_contact_email_submission_submitted_by"),
    ]

    operations = [
        migrations.AddField(
            model_name="team",
            name="moderation_note",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="team",
            name="moderation_status",
            field=models.CharField(
                choices=[
                    ("approved", "Approved"),
                    ("pending", "Pending"),
                    ("suspended", "Suspended"),
                ],
                default="approved",
                max_length=16,
            ),
        ),
        migrations.CreateModel(
            name="CompetitionSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("registration_open", models.BooleanField(default=True)),
                ("registration_starts_at", models.DateTimeField(blank=True, null=True)),
                ("registration_ends_at", models.DateTimeField(blank=True, null=True)),
                ("reservation_required_for_registration", models.BooleanField(default=False)),
                ("auto_approve_registrations", models.BooleanField(default=True)),
                ("round_duration_minutes", models.PositiveIntegerField(default=15)),
                ("round_break_minutes", models.PositiveIntegerField(default=5)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"verbose_name_plural": "competition settings"},
        ),
        migrations.CreateModel(
            name="TeamReservation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=128, unique=True)),
                ("slug", models.SlugField(max_length=64, unique=True)),
                ("contact_email", models.EmailField(max_length=254)),
                ("captain_username", models.CharField(max_length=150)),
                ("token", models.CharField(max_length=32, unique=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                            ("claimed", "Claimed"),
                        ],
                        default="pending",
                        max_length=16,
                    ),
                ),
                ("note", models.CharField(blank=True, max_length=255)),
                ("expires_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.RunPython(
            code=lambda apps, schema_editor: apps.get_model("ctf", "CompetitionSettings").objects.get_or_create(),
            reverse_code=migrations.RunPython.noop,
        ),
    ]
