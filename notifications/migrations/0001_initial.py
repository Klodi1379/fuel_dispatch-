# Generated by Django 5.0.4 on 2025-04-13 02:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("contenttypes", "0003_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="NotificationType",
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
                ("code", models.CharField(max_length=50, unique=True)),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="Notification",
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
                ("subject", models.CharField(max_length=255)),
                ("message", models.TextField()),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("object_id", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "content_type",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "recipient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "notification_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="notifications.notificationtype",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="NotificationEvent",
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
                (
                    "event_type",
                    models.CharField(
                        choices=[
                            ("CREATED", "Krijuar"),
                            ("SENT_EMAIL", "Email i dërguar"),
                            ("SENT_SMS", "SMS i dërguar"),
                            ("READ", "Lexuar"),
                            ("CLICKED", "Klikuar"),
                        ],
                        max_length=15,
                    ),
                ),
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("details", models.TextField(blank=True)),
                (
                    "notification",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="events",
                        to="notifications.notification",
                    ),
                ),
            ],
            options={
                "ordering": ["timestamp"],
            },
        ),
        migrations.CreateModel(
            name="NotificationTemplate",
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
                ("subject_template", models.CharField(max_length=255)),
                ("email_template", models.TextField()),
                ("sms_template", models.CharField(blank=True, max_length=255)),
                (
                    "notification_type",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="template",
                        to="notifications.notificationtype",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="NotificationSetting",
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
                ("is_enabled", models.BooleanField(default=True)),
                (
                    "notification_method",
                    models.CharField(
                        choices=[
                            ("EMAIL", "Email"),
                            ("IN_APP", "In-App"),
                            ("SMS", "SMS"),
                            ("ALL", "Të gjitha"),
                        ],
                        default="ALL",
                        max_length=10,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notification_settings",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "notification_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="notifications.notificationtype",
                    ),
                ),
            ],
            options={
                "unique_together": {("user", "notification_type")},
            },
        ),
    ]
