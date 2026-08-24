from django.urls import path
from .views import EmpruntView,EmpruntCreateAPI,EmpruntDetailView

urlpatterns = [
    path('emprunt/', EmpruntView.as_view(), name='emprunt'),
    path('emprunt/create/', EmpruntCreateAPI.as_view(), name='emprunt'),
    path('emprunt/<uuid:emprunt_id>/',EmpruntDetailView.as_view(),name="emprunt-detail")]