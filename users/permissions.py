from rest_framework.permissions import BasePermission
from organisation.models import Membership


def current_membership(user):
    return Membership.objects.filter(user=user).select_related("organisation", "bibliotheque").first()


def has_library_access(membership, bibliotheque):
    if not membership or not bibliotheque:
        return False
    if membership.bibliotheque_id:
        return str(bibliotheque.id) == str(membership.bibliotheque_id)
    return str(bibliotheque.organisation_id) == str(membership.organisation_id)


def is_platform_owner(user):
    has_client_space = Membership.objects.filter(user=user, role="owner").exists()
    return bool((user.is_superuser or user.is_staff) and not has_client_space)


def can_manage_organisation_users(user):
    membership = current_membership(user)
    return bool(is_platform_owner(user) or membership and membership.role in {"owner", "admin"})


def is_client_member(user):
    membership = current_membership(user)
    return bool(membership and membership.role in {"owner", "admin", "bibliothecaire"})


class IsPlatformOwner(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and is_platform_owner(request.user))


class CanManageOrganisationUsers(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and can_manage_organisation_users(request.user))


class IsClientMember(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and is_client_member(request.user))
