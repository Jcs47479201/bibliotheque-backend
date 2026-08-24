from rest_framework import serializers
from .models import Emprunt


class EmpruntSerializer(serializers.ModelSerializer):
    livre_titre = serializers.CharField(source="livre.titre", read_only=True)
    adherent_nom = serializers.SerializerMethodField()

    class Meta:
        model = Emprunt
        fields = ["id", "livre", "livre_titre", "adherent", "adherent_nom", "date_emprunt", "date_retour", "bibliotheque", "date_limite"]
        read_only_fields = ["id", "date_emprunt"]

    def get_adherent_nom(self, obj):
        return f"{obj.adherent.prenom} {obj.adherent.nom}"
    

class EmpruntCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emprunt
        fields = ["id", "livre", "adherent", "date_emprunt", "date_retour", "bibliotheque", "date_limite"]
        read_only_fields = ["id", "date_emprunt", "bibliotheque"]