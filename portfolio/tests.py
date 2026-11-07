from io import BytesIO, StringIO
from tempfile import TemporaryDirectory
from unittest.mock import patch

from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, transaction
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .models import Owner, Profile, Project, Passion, Skill, Certification, Qualification

TEST_STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}


@override_settings(SECURE_SSL_REDIRECT=False, STORAGES=TEST_STORAGES)
class PortfolioTests(TestCase):
    password = "Only-for-this-test-suite-73!"

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.owner = User.objects.create_superuser("owner", "owner@example.test", cls.password)
        cls.other_superuser = User.objects.create_superuser("other", "other@example.test", cls.password)
        cls.staff = User.objects.create_user("staff", password=cls.password, is_staff=True)
        Owner.objects.create(user=cls.owner)
        cls.profile = Profile.objects.create()
        cls.public_project = Project.objects.create(title="Public project", slug="public-project", summary="A public summary", published=True)
        cls.draft_project = Project.objects.create(title="Private draft project", slug="private-draft", summary="Draft-only text")

    def test_public_home_and_published_project_render(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Muhammed Faris C K")
        self.assertContains(response, "laptop-scene")
        self.assertContains(response, "Public project")
        self.assertNotContains(response, "Private draft project")
        self.assertNotContains(response, "Open your studio")
        self.assertEqual(self.client.get(self.public_project.get_absolute_url()).status_code, 200)

    def test_draft_and_unknown_project_are_not_public(self):
        self.assertEqual(self.client.get(self.draft_project.get_absolute_url()).status_code, 404)
        self.assertEqual(self.client.get("/projects/missing/").status_code, 404)
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get(self.draft_project.get_absolute_url()).status_code, 404)

    def test_each_section_honours_publish_state(self):
        specs = [(Passion, {}), (Skill, {}), (Certification, {"issuer": "Example issuer"}),
                 (Qualification, {"institution": "Example institution", "period": "2024"})]
        for model, extra in specs:
            model.objects.create(title=f"Public {model.__name__}", published=True, **extra)
            model.objects.create(title=f"Hidden {model.__name__}", **extra)
        response = self.client.get("/")
        for model, _ in specs:
            self.assertContains(response, f"Public {model.__name__}")
            self.assertNotContains(response, f"Hidden {model.__name__}")

    def test_visitors_staff_and_unbound_superusers_cannot_edit(self):
        records = [self.public_project, self.profile,
                   Passion.objects.create(title="Passion"), Skill.objects.create(title="Skill"),
                   Certification.objects.create(title="Certificate", issuer="Issuer"),
                   Qualification.objects.create(title="Qualification", institution="Institution", period="2024")]
        for user in [None, self.staff, self.other_superuser]:
            self.client.logout()
            if user:
                self.client.force_login(user)
            for item in records:
                model = item._meta.model_name
                for action in ["add", "change", "delete"]:
                    args = [] if action == "add" else [item.pk]
                    url = reverse(f"owner_admin:portfolio_{model}_{action}", args=args)
                    for method in ["get", "post"]:
                        response = getattr(self.client, method)(url)
                        with self.subTest(user=str(user), model=model, action=action, method=method):
                            self.assertEqual(response.status_code, 302)
                            self.assertIn("/admin/login/", response.url)
            self.assertEqual(self.client.post(reverse("owner_admin:portfolio_project_changelist"), {
                "action": "delete_selected", "_selected_action": self.public_project.pk, "post": "yes",
            }).status_code, 302)
        for item in records:
            self.assertTrue(type(item).objects.filter(pk=item.pk).exists())

    def test_unbound_superuser_cannot_login_to_owner_studio(self):
        response = self.client.post(reverse("owner_admin:login"), {
            "username": "other", "password": self.password, "next": "/admin/",
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_owner_login_and_dashboard(self):
        response = self.client.post(reverse("owner_admin:login"), {
            "username": "owner", "password": self.password, "next": "/admin/",
        })
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse("owner_admin:index"))
        self.assertContains(response, "Keep your story up to date.")
        self.assertContains(self.client.get("/"), "Open your studio")

    def test_owner_can_add_change_and_delete_every_content_type(self):
        self.client.force_login(self.owner)
        specs = [
            (Project, {"slug": "new-build", "summary": "A real project summary", "category": "web"}),
            (Passion, {"symbol": "</>"}), (Skill, {"category": "backend"}),
            (Certification, {"issuer": "Issuer"}),
            (Qualification, {"institution": "Institution", "period": "2024 – 2026"}),
        ]
        for model, extra in specs:
            payload = {"title": f"New {model.__name__}", "description": "First version", "position": 2, "published": "on", **extra}
            prefix = f"owner_admin:portfolio_{model._meta.model_name}_"
            response = self.client.post(reverse(prefix + "add"), payload)
            with self.subTest(model=model.__name__, action="add"):
                self.assertEqual(response.status_code, 302)
            item = model.objects.get(title=payload["title"])
            self.assertTrue(item.published)
            payload["description"] = "Updated by the owner"
            payload.pop("published")
            response = self.client.post(reverse(prefix + "change", args=[item.pk]), payload)
            self.assertEqual(response.status_code, 302)
            item.refresh_from_db()
            self.assertFalse(item.published)
            self.assertEqual(item.description, "Updated by the owner")
            response = self.client.post(reverse(prefix + "delete", args=[item.pk]), {"post": "yes"})
            self.assertEqual(response.status_code, 302)
            self.assertFalse(model.objects.filter(pk=item.pk).exists())

    def test_owner_can_edit_profile_but_cannot_delete_or_add_a_second(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("owner_admin:portfolio_profile_change", args=[1]), {
            "name": "Muhammed Faris C K", "role": "Django developer", "headline": "My next chapter",
            "intro": "New intro", "about": "New about", "email": "faris@example.test",
        })
        self.assertEqual(response.status_code, 302)
        self.assertContains(self.client.get("/"), "My next chapter")
        self.assertEqual(self.client.post(reverse("owner_admin:portfolio_profile_delete", args=[1]), {"post": "yes"}).status_code, 403)
        self.assertEqual(self.client.get(reverse("owner_admin:portfolio_profile_add")).status_code, 403)

    def test_publish_actions(self):
        self.client.force_login(self.owner)
        url = reverse("owner_admin:portfolio_project_changelist")
        for action, expected in [("publish_selected", True), ("hide_selected", False)]:
            self.client.post(url, {"action": action, "_selected_action": self.draft_project.pk})
            self.draft_project.refresh_from_db()
            self.assertEqual(self.draft_project.published, expected)

    def test_csrf_protects_owner_writes(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.owner)
        response = client.post(reverse("owner_admin:portfolio_project_add"), {"title": "Blocked"})
        self.assertEqual(response.status_code, 403)

    def test_public_routes_reject_writes_and_no_signup_exists(self):
        self.assertEqual(self.client.post("/").status_code, 405)
        self.assertEqual(self.client.post(self.public_project.get_absolute_url()).status_code, 405)
        self.assertEqual(self.client.get("/signup/").status_code, 404)
        self.client.force_login(self.owner)
        self.assertEqual(self.client.get("/admin/auth/user/").status_code, 404)

    def test_user_content_is_html_escaped(self):
        self.public_project.title = '<script>alert("test")</script>'
        self.public_project.description = '<img src=x onerror=alert("test")>'
        self.public_project.save()
        response = self.client.get(self.public_project.get_absolute_url())
        self.assertNotContains(response, '<script>alert(')
        self.assertNotContains(response, '<img src=x')
        self.assertContains(response, '&lt;script&gt;')

    def test_ordering_and_featured_projects(self):
        Project.objects.create(title="Featured first", slug="featured", summary="Featured", featured=True, published=True, position=99)
        response = self.client.get("/")
        items = list(response.context["projects"])
        self.assertEqual(items[0].title, "Featured first")

    def test_valid_image_upload_and_rejection_of_svg(self):
        self.client.force_login(self.owner)
        url = reverse("owner_admin:portfolio_project_add")
        base = {"title": "Image project", "slug": "image-project", "summary": "Image test", "category": "web", "position": 0}
        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            buffer = BytesIO()
            Image.new("RGB", (20, 20), "purple").save(buffer, "PNG")
            response = self.client.post(url, {**base, "image": SimpleUploadedFile("image.png", buffer.getvalue(), "image/png")})
            self.assertEqual(response.status_code, 302)
            self.assertTrue(Project.objects.get(slug="image-project").image.name.endswith(".png"))
            response = self.client.post(url, {**base, "slug": "bad-image", "image": SimpleUploadedFile("image.svg", b"<svg></svg>", "image/svg+xml")})
            self.assertEqual(response.status_code, 200)
            self.assertFalse(Project.objects.filter(slug="bad-image").exists())

    def test_single_owner_constraint_and_no_second_claim(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Owner.objects.create(pk=2, user=self.other_superuser)
        with self.assertRaises(CommandError):
            call_command("create_owner", username="another", stdout=StringIO())


class SetupTests(TestCase):
    def test_seed_is_idempotent_and_does_not_invent_credentials(self):
        call_command("seed_portfolio", stdout=StringIO())
        profile = Profile.objects.get(pk=1)
        profile.name = "My edited name"
        profile.save()
        call_command("seed_portfolio", stdout=StringIO())
        profile.refresh_from_db()
        self.assertEqual(profile.name, "My edited name")
        self.assertEqual(Skill.objects.count(), 3)
        self.assertEqual(Passion.objects.count(), 3)
        self.assertEqual(Project.objects.count(), 0)
        self.assertEqual(Certification.objects.count(), 0)
        self.assertEqual(Qualification.objects.count(), 0)

    @patch("portfolio.management.commands.create_owner.getpass", return_value="A-new-local-owner-password-78!")
    def test_create_owner_binds_exactly_one_account(self, _getpass):
        call_command("create_owner", username="faris", email="faris@example.test", stdout=StringIO())
        owner = Owner.objects.get(pk=1)
        self.assertEqual(owner.user.username, "faris")
        self.assertTrue(owner.user.is_superuser)
        self.assertTrue(owner.user.check_password("A-new-local-owner-password-78!"))
        with self.assertRaises(CommandError):
            call_command("create_owner", username="someone-else", stdout=StringIO())
