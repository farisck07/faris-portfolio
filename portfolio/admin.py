from django import forms
from django.contrib import admin
from django.contrib.admin.forms import AdminAuthenticationForm

from .models import Owner, Profile, Project, Passion, Skill, Certification, Qualification


def is_portfolio_owner(user):
    return bool(user.is_authenticated and user.is_active and user.is_staff and user.is_superuser
                and Owner.objects.filter(pk=1, user_id=user.pk).exists())


class OwnerLoginForm(AdminAuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not is_portfolio_owner(user):
            raise forms.ValidationError("Please enter the correct owner credentials.", code="invalid_login")


class OwnerAdminSite(admin.AdminSite):
    site_header = "Faris / Studio"
    site_title = "Portfolio studio"
    index_title = "Your content, your way."
    login_form = OwnerLoginForm
    index_template = "admin/portfolio_index.html"

    def has_permission(self, request):
        return is_portfolio_owner(request.user)


owner_admin = OwnerAdminSite(name="owner_admin")


@admin.register(Profile, site=owner_admin)
class ProfileAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Identity", {"fields": ("name", "role", "headline", "intro", "about")}),
        ("Contact & availability", {"fields": ("email", "location", "availability")}),
        ("Your links", {"fields": ("github_url", "linkedin_url", "resume_url")}),
    ]

    def has_add_permission(self, request):
        return super().has_add_permission(request) and not Profile.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


class ContentAdmin(admin.ModelAdmin):
    list_display = ("title", "published", "position")
    list_editable = ("published", "position")
    list_filter = ("published",)
    search_fields = ("title", "description")
    save_on_top = True
    actions = ("publish_selected", "hide_selected")

    @admin.action(description="Publish selected items")
    def publish_selected(self, request, queryset):
        count = queryset.update(published=True)
        self.message_user(request, f"Published {count} item(s).")

    @admin.action(description="Move selected items to draft")
    def hide_selected(self, request, queryset):
        count = queryset.update(published=False)
        self.message_user(request, f"Moved {count} item(s) to draft.")


@admin.register(Project, site=owner_admin)
class ProjectAdmin(ContentAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ("published", "category", "featured")
    fieldsets = [
        ("Project", {"fields": ("title", "slug", "summary", "description")}),
        ("Presentation", {"fields": ("category", "technologies", "image", "image_alt", "featured")}),
        ("Links", {"fields": ("live_url", "source_url")}),
        ("Visibility", {"fields": ("published", "position")}),
    ]


@admin.register(Skill, site=owner_admin)
class SkillAdmin(ContentAdmin):
    list_filter = ("published", "category")


owner_admin.register(Passion, ContentAdmin)
owner_admin.register(Certification, ContentAdmin)
owner_admin.register(Qualification, ContentAdmin)
# Owner and authentication models are intentionally not registered here.
# Binding the single owner requires server-side access to create_owner.
