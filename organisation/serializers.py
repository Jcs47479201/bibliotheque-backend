from rest_framework import serializers
from .models import Organisation


class OrganisationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ["id", "nom", "slug", "adresse", "telephone", "email", "active", "date_creation", "abonnement_plan", "abonnement_statut", "abonnement_debut", "abonnement_fin"]
        read_only_fields = ["id"]
        