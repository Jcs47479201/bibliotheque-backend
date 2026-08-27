from rest_framework import serializers
from .models import Categorie,Auteur, Livre


class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ["id", "nom", "bibliotheque"]
        read_only_fields = ["id"]

class AuteurSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auteur
        fields = ["id", "nom", "bibliotheque", "date_creation", "date_modification"]
        read_only_fields = ["id", "date_creation", "date_modification"]

class LivreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livre
        fields = ["id", "titre", "auteurs", "categorie", "bibliotheque", "isbn", "pages", "image", "statut", "date_creation", "langue"]
        read_only_fields = ["id", "date_creation"]

#Sérialiseur pour la création d'un livre avec des auteurs existants
class LivreCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Livre
        fields = ["id", "titre", "auteurs", "categorie", "bibliotheque", "isbn", "pages", "image", "statut", "date_creation", "langue"]
        read_only_fields = ["id", "date_creation"]

## Sérialiseur pour la création des auteurs #####
class AuteurCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Auteur
        fields = ["id", "nom", "bibliotheque", "date_creation", "date_modification"]
        read_only_fields = ["id", "date_creation", "date_modification"]
        extra_kwargs = {
            "bibliotheque": {"required": False}
        }