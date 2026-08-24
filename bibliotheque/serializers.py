from rest_framework import serializers
from .models import Bibliotheque, Adherent


class BibliothequeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bibliotheque
        fields = ["id", "nom", "slug", "adresse", "telephone", "email", "statut", "organisation"]
        read_only_fields = ["id"]


class AdherentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adherent
        fields = ["id", "nom", "prenom", "email", "bibliotheque", "contact", "date_creation", "date_modification"]
        read_only_fields = ["id", "date_creation", "date_modification"]

#Création d'un sérialiseur pour la création d'un adhérent
class AdherentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adherent
        fields = ["id", "nom", "prenom", "email", "bibliotheque", "contact", "date_creation", "date_modification"]
        read_only_fields = ["id", "bibliotheque", "date_creation", "date_modification"]