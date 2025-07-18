# Generated by Django 5.2.1 on 2025-06-19 03:33

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_appfeedback_feedbacknotification_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="user",
            options={},
        ),
        migrations.RenameField(
            model_name="user",
            old_name="password_reset_expires",
            new_name="premium_until",
        ),
        migrations.RemoveField(
            model_name="user",
            name="created_at",
        ),
        migrations.RemoveField(
            model_name="user",
            name="expertise",
        ),
        migrations.RemoveField(
            model_name="user",
            name="password_reset_token",
        ),
        migrations.RemoveField(
            model_name="user",
            name="updated_at",
        ),
        migrations.AddField(
            model_name="user",
            name="availability",
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name="user",
            name="date_of_birth",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="experience_years",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="user",
            name="followers_count",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="user",
            name="following_count",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="user",
            name="hourly_rate",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=10, null=True
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="is_premium",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="user",
            name="is_verified",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="user",
            name="language",
            field=models.CharField(default="en", max_length=10),
        ),
        migrations.AddField(
            model_name="user",
            name="last_active",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="user",
            name="location",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="user",
            name="phone",
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AddField(
            model_name="user",
            name="timezone",
            field=models.CharField(default="UTC", max_length=50),
        ),
        migrations.AddField(
            model_name="user",
            name="total_earnings",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name="user",
            name="total_sessions",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="user",
            name="website",
            field=models.URLField(blank=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="bio",
            field=models.TextField(blank=True, default=2, max_length=500),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="user",
            name="career_goals",
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="domain",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name="user",
            name="interests",
            field=models.TextField(blank=True, help_text="Comma-separated interests"),
        ),
        migrations.AlterField(
            model_name="user",
            name="profile_image",
            field=models.ImageField(
                blank=True,
                help_text="Profile image will be automatically resized to 200x200",
                null=True,
                upload_to="profile_images/",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("learner", "Learner"),
                    ("mentor", "Mentor"),
                    ("admin", "Admin"),
                ],
                default="learner",
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="skills",
            field=models.TextField(blank=True, help_text="Comma-separated skills"),
        ),
        migrations.AlterModelTable(
            name="user",
            table="users_user",
        ),
        migrations.CreateModel(
            name="Follow",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "follower",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="following",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "following",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="followers",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["follower", "created_at"],
                        name="users_follo_followe_229ec1_idx",
                    ),
                    models.Index(
                        fields=["following", "created_at"],
                        name="users_follo_followi_dcf251_idx",
                    ),
                ],
                "unique_together": {("follower", "following")},
            },
        ),
        migrations.CreateModel(
            name="PaymentHistory",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "payment_type",
                    models.CharField(
                        choices=[
                            ("session_booking", "Session Booking"),
                            ("gift", "Gift"),
                            ("premium_upgrade", "Premium Upgrade"),
                            ("mentor_payout", "Mentor Payout"),
                        ],
                        max_length=20,
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("currency", models.CharField(default="INR", max_length=3)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("completed", "Completed"),
                            ("failed", "Failed"),
                            ("refunded", "Refunded"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("payment_id", models.CharField(blank=True, max_length=100)),
                ("gateway", models.CharField(default="razorpay", max_length=50)),
                ("related_session_id", models.UUIDField(blank=True, null=True)),
                ("related_user_id", models.UUIDField(blank=True, null=True)),
                ("description", models.TextField(blank=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payment_history",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(
                        fields=["user", "created_at"],
                        name="users_payme_user_id_3d339b_idx",
                    ),
                    models.Index(
                        fields=["status", "created_at"],
                        name="users_payme_status_b09676_idx",
                    ),
                    models.Index(
                        fields=["payment_type", "created_at"],
                        name="users_payme_payment_63685c_idx",
                    ),
                ],
            },
        ),
        migrations.CreateModel(
            name="UserActivity",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "activity_type",
                    models.CharField(
                        choices=[
                            ("session_created", "Session Created"),
                            ("session_joined", "Session Joined"),
                            ("session_completed", "Session Completed"),
                            ("profile_updated", "Profile Updated"),
                            ("followed_user", "Followed User"),
                            ("unfollowed_user", "Unfollowed User"),
                            ("feedback_given", "Feedback Given"),
                            ("payment_made", "Payment Made"),
                            ("login", "Login"),
                            ("logout", "Logout"),
                        ],
                        max_length=30,
                    ),
                ),
                ("description", models.TextField()),
                ("related_user_id", models.UUIDField(blank=True, null=True)),
                ("related_session_id", models.UUIDField(blank=True, null=True)),
                ("ip_address", models.GenericIPAddressField(blank=True, null=True)),
                ("user_agent", models.TextField(blank=True)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="activities",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(
                        fields=["user", "created_at"],
                        name="users_usera_user_id_63b4df_idx",
                    ),
                    models.Index(
                        fields=["activity_type", "created_at"],
                        name="users_usera_activit_f7d096_idx",
                    ),
                ],
            },
        ),
    ]
