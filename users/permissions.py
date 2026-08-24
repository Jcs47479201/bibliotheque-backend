from rest_framework.permissions import BasePermission
from organisation.models import Membership


def current_membership(user):
    return Membership.objects.filter(user=user).select_related("organisation").first()


def is_platform_owner(user):
    membership = current_membership(user)
    return bool(user.is_superuser or user.is_staff or membership and membership.role == "owner")


def can_manage_organisation_users(user):
    membership = current_membership(user)
    return bool(is_platform_owner(user) or membership and membership.role == "admin")


def is_client_member(user):
    membership = current_membership(user)
    return bool(membership and membership.role in {"admin", "bibliothecaire"})


class IsPlatformOwner(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and is_platform_owner(request.user))


class CanManageOrganisationUsers(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and can_manage_organisation_users(request.user))


class IsClientMember(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and is_client_member(request.user))
