# Generated by Django 5.2.1 on 2025-06-20 05:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("learning_sessions", "0005_alter_sessionparticipant_options_and_more"),
        ("recommendations", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="recommendationinteraction",
            name="recommendation",
        ),
        migrations.RemoveField(
            model_name="recommendationinteraction",
            name="session",
        ),
        migrations.RemoveField(
            model_name="recommendationinteraction",
            name="user",
        ),
        migrations.CreateModel(
            name="PopularityMetric",
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
                ("view_count", models.IntegerField(default=0)),
                ("booking_count", models.IntegerField(default=0)),
                ("completion_rate", models.FloatField(default=0.0)),
                ("rating_average", models.FloatField(default=0.0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "session",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="popularity",
                        to="learning_sessions.session",
                    ),
                ),
            ],
        ),
        migrations.DeleteModel(
            name="Recommendation",
        ),
        migrations.DeleteModel(
            name="RecommendationInteraction",
        ),
    ]
