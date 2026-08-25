from django.urls import path
from .views import MeView, OrganisationUserDetailView, OrganisationUsersView, RegisterView




urlpatterns = [
    path("me/", MeView.as_view(), name="me"),
    path("organisation/", OrganisationUsersView.as_view(), name="organisation-users"),
    path("organisation/<int:user_id>/", OrganisationUserDetailView.as_view(), name="organisation-user-detail"),
    path("register/", RegisterView.as_view(), name="register"),
]