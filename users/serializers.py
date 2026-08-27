from rest_framework import serializers
from .models import User
from organisation.models import Membership
from bibliotheque.models import Bibliotheque
from organisation.models import Organisation
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.text import slugify

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    organisation_id = serializers.SerializerMethodField()
    bibliotheque_id = serializers.SerializerMethodField()
    bibliotheque_nom = serializers.SerializerMethodField()
    platform_admin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'organisation_id', 'bibliotheque_id', 'bibliotheque_nom', 'platform_admin']

    def get_role(self, obj):
        membership = Membership.objects.filter(user=obj).first()
        return membership.role if membership else None

    def get_organisation_id(self, obj):
        membership = Membership.objects.filter(user=obj).first()
        return str(membership.organisation_id) if membership else None

    def get_bibliotheque_id(self, obj):
        membership = Membership.objects.filter(user=obj).first()
        return str(membership.bibliotheque_id) if membership and membership.bibliotheque_id else None

    def get_bibliotheque_nom(self, obj):
        membership = Membership.objects.filter(user=obj).select_related("bibliotheque").first()
        return membership.bibliotheque.nom if membership and membership.bibliotheque else None

    def get_platform_admin(self, obj):
        has_client_space = Membership.objects.filter(user=obj, role="owner").exists()
        return bool((obj.is_superuser or obj.is_staff) and not has_client_space)

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        read_only_fields = ['id']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

#création d'un User + Organisation + Bibliothèque + membership
class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)

    organisation_nom = serializers.CharField(max_length=100)
    organisation_email = serializers.EmailField()
    organisation_telephone = serializers.CharField(max_length=100)

    bibliotheque_nom = serializers.CharField(max_length=255)
    bibliotheque_adresse = serializers.CharField(required=False, allow_blank=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Cet identifiant est déjà utilisé.")
        return value

    def validate(self, attrs):
        organisation_slug = slugify(attrs["organisation_nom"])
        bibliotheque_slug = slugify(attrs["bibliotheque_nom"])

        errors = {}
        if not organisation_slug:
            errors["organisation_nom"] = "Le nom de l'organisation doit contenir des caractères valides."
        elif Organisation.objects.filter(slug=organisation_slug).exists():
            errors["organisation_nom"] = "Cette organisation existe déjà."

        if not bibliotheque_slug:
            errors["bibliotheque_nom"] = "Le nom de la bibliothèque doit contenir des caractères valides."
        elif Bibliotheque.objects.filter(slug=bibliotheque_slug).exists():
            errors["bibliotheque_nom"] = "Cette bibliothèque existe déjà."

        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def to_representation(self, instance):
        return {
            "id": str(instance.id),
            "username": instance.username,
            "email": instance.email,
        }

    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )

        organisation = Organisation.objects.create(
            nom=validated_data["organisation_nom"],
            slug=slugify(validated_data["organisation_nom"]),
            email=validated_data["organisation_email"],
            telephone=validated_data["organisation_telephone"],
        )

        Membership.objects.create(
            user=user,
            organisation=organisation,
            role="owner",
        )

        Bibliotheque.objects.create(
            nom=validated_data["bibliotheque_nom"],
            organisation=organisation,
            adresse=validated_data.get("bibliotheque_adresse", ""),
            telephone=validated_data["organisation_telephone"],
            email=validated_data["organisation_email"],
            slug=slugify(validated_data["bibliotheque_nom"]),
        )

        return user