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

class AdherentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adherent
        fields = ["id", "nom", "prenom", "email", "bibliotheque", "contact", "date_creation", "date_modification"]
        read_only_fields = ["id", "date_creation", "date_modification"]
        extra_kwargs = {
            "bibliotheque": {"required": False}
        }