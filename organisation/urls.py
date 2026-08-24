from django.urls import path
from .views import MyOrganisationView, PlatformOrganisationDetailView, PlatformOrganisationsView, OrganisationCreateView


urlpatterns = [
    path("me/", MyOrganisationView.as_view(), name="my-organisation"),
    path("admin/", PlatformOrganisationsView.as_view(), name="platform-organisations"),
    path("admin/create/", OrganisationCreateView.as_view(), name="platform-organisation-create"),
    path("admin/<uuid:organisation_id>/", PlatformOrganisationDetailView.as_view(), name="platform-organisation-detail"),
]