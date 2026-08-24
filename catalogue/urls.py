from django.urls import path
from .views import *



urlpatterns = [
    path("categories/", MyCategoriesView.as_view(), name="my-categories"),
    path("categories/create/", CategorieCreateView.as_view(), name="categorie-create"),
    path("categories/<uuid:categorie_id>/", CategorieDetailView.as_view(), name="categorie-detail"),

    #Url des auteurs
    path("auteurs/", MyAuteursView.as_view(), name="my-auteurs"),
    path("auteurs/create/", AuteurCreateView.as_view(), name="auteur-create"),
    path('auteurs/<uuid:auteur_id>/', AuteurDetailView.as_view(), name="auteur-details"),

    #url des livres
    path("livres/", MyLivresView.as_view(),name="my-livres"),
    path("livres/create/", LivreCreateView.as_view(), name="livre-create"),
    path("livres/<uuid:livre_id>/", LivreCreateView.as_view(), name="livre-detail"),

]