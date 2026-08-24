from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # Authentification JWT
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # API
    path("api/organisation/", include("organisation.urls")),
    path("api/bibliotheque/", include("bibliotheque.urls")),
    path("api/catalogue/", include("catalogue.urls")),
    path("api/circulation/", include("circulation.urls")),
    path("api/users/", include("users.urls")),
]