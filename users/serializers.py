from rest_framework import serializers
from .models import User
from organisation.models import Membership


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    organisation_id = serializers.SerializerMethodField()
    platform_admin = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'organisation_id', 'platform_admin']

    def get_role(self, obj):
        membership = Membership.objects.filter(user=obj).first()
        return membership.role if membership else None

    def get_organisation_id(self, obj):
        membership = Membership.objects.filter(user=obj).first()
        return str(membership.organisation_id) if membership else None

    def get_platform_admin(self, obj):
        membership = Membership.objects.filter(user=obj).first()
        return bool(obj.is_superuser or obj.is_staff or membership and membership.role == "owner")

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
