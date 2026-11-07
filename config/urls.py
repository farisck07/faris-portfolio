from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from portfolio.admin import owner_admin
from portfolio import views

urlpatterns = [
    path("", views.home, name="home"),
    path("projects/<slug:slug>/", views.project_detail, name="project_detail"),
    path("admin/", owner_admin.urls),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
