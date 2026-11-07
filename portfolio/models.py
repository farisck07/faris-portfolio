from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.urls import reverse


def validate_image_size(value):
    if value.size > 5 * 1024 * 1024:
        raise ValidationError("Choose an image smaller than 5 MB.")


def image_path(instance, filename):
    return f"portfolio/{uuid4().hex}{Path(filename).suffix.lower()}"


class Owner(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Meta:
        constraints = [models.CheckConstraint(condition=models.Q(id=1), name="single_portfolio_owner")]

    def __str__(self):
        return str(self.user)


class Profile(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    name = models.CharField(max_length=120, default="Muhammed Faris C K")
    role = models.CharField(max_length=160, default="Django & Python Full-Stack Developer")
    headline = models.CharField(max_length=160, default="Thoughtful code. Meaningful experiences.")
    intro = models.CharField(max_length=320, default="I turn ideas into purposeful web experiences, from the first interface to the Python that powers it.")
    about = models.TextField(default="I'm Muhammed Faris C K, a Django and Python full-stack developer. I enjoy connecting clear interfaces with reliable backends and turning everyday ideas into useful web applications.")
    email = models.EmailField(blank=True)
    location = models.CharField(max_length=120, blank=True)
    availability = models.CharField(max_length=100, blank=True, help_text="For example: Open to freelance projects. Leave blank to hide.")
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    resume_url = models.URLField(blank=True, help_text="A public link to your CV PDF.")

    class Meta:
        verbose_name = "profile & contact details"
        verbose_name_plural = "profile & contact details"
        constraints = [models.CheckConstraint(condition=models.Q(id=1), name="single_portfolio_profile")]

    def __str__(self):
        return self.name


class PublishedContent(models.Model):
    title = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    published = models.BooleanField(default=False, help_text="Only published items appear on your public portfolio.")
    position = models.PositiveIntegerField(default=0, help_text="Smaller numbers appear first.")

    class Meta:
        abstract = True
        ordering = ["position", "pk"]

    def __str__(self):
        return self.title


class Project(PublishedContent):
    CATEGORY_CHOICES = [("web", "Full stack"), ("api", "Backend & API"), ("frontend", "Frontend")]
    slug = models.SlugField(max_length=160, unique=True)
    summary = models.CharField(max_length=240)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="web")
    technologies = models.CharField(max_length=240, blank=True, help_text="Comma-separated: Django, Python, PostgreSQL")
    image = models.ImageField(upload_to=image_path, blank=True, validators=[
        FileExtensionValidator(["jpg", "jpeg", "png", "webp"]), validate_image_size,
    ], help_text="JPG, PNG or WebP, up to 5 MB. Landscape works best.")
    image_alt = models.CharField(max_length=200, blank=True)
    live_url = models.URLField(blank=True)
    source_url = models.URLField(blank=True)
    featured = models.BooleanField(default=False)

    @property
    def tags(self):
        return [tag.strip() for tag in self.technologies.split(",") if tag.strip()]

    def get_absolute_url(self):
        return reverse("project_detail", kwargs={"slug": self.slug})


class Passion(PublishedContent):
    symbol = models.CharField(max_length=12, default="</>", help_text="A short symbol or emoji.")


class Skill(PublishedContent):
    category = models.CharField(max_length=20, choices=[
        ("backend", "Backend"), ("frontend", "Frontend"), ("database", "Databases"), ("tools", "Tools"),
    ], default="backend")
    level = models.CharField(max_length=80, blank=True, help_text="Optional, e.g. Working knowledge or Currently learning.")


class Certification(PublishedContent):
    issuer = models.CharField(max_length=140)
    issued_on = models.DateField(blank=True, null=True)
    credential_url = models.URLField(blank=True)
    credential_id = models.CharField(max_length=160, blank=True)


class Qualification(PublishedContent):
    institution = models.CharField(max_length=160)
    period = models.CharField(max_length=100, help_text="For example: 2024 – Present")
