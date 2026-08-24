from django.urls import path
from .views import  *

urlpatterns = [
    path("me/", MyBibliothequesView.as_view(), name="my-bibliotheque"),
    path("admin/", PlatformBibliothequesView.as_view(), name="platform-bibliotheques"),
    path("me/<uuid:bibliotheque_id>/adherents/", MyAdherentsView.as_view(), name="my-adherents"),
    path("me/adherents/create/", AdherentCreateView.as_view(), name="adherent-create"),
    path('adherent/<uuid:adherent_id>/', AdherentDetailView.as_view(), name="adherent-details")
]