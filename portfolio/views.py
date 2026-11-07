from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_safe

from .admin import is_portfolio_owner
from .models import Profile, Project, Passion, Skill, Certification, Qualification


def shared_context(request):
    return {
        "profile": Profile.objects.first() or Profile(),
        "is_owner": is_portfolio_owner(request.user),
    }


@require_safe
def home(request):
    context = shared_context(request)
    context.update({
        "projects": Project.objects.filter(published=True).order_by("-featured", "position", "pk"),
        "passions": Passion.objects.filter(published=True),
        "skills": Skill.objects.filter(published=True),
        "certifications": Certification.objects.filter(published=True),
        "qualifications": Qualification.objects.filter(published=True),
        "project_categories": Project.CATEGORY_CHOICES,
    })
    return render(request, "portfolio/home.html", context)


@require_safe
def project_detail(request, slug):
    context = shared_context(request)
    context["project"] = get_object_or_404(Project, slug=slug, published=True)
    return render(request, "portfolio/project_detail.html", context)
