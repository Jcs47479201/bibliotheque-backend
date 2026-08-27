from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import UserSerializer, UserCreateSerializer, RegisterSerializer
from .models import User
from .permissions import CanManageOrganisationUsers, current_membership
from bibliotheque.models import Bibliotheque
from organisation.models import Membership
from rest_framework import generics

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

#La gestion du profil
class MyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request):
        request.user.delete()
        return Response(status=204)

#Création d'utilisateur
class UserCreateView(APIView):
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        if User.objects.filter(username=serializer.validated_data["username"]).exists():
            return Response({"detail": "Cet identifiant est déjà utilisé."}, status=400)
        serializer.save()
        return Response(serializer.data, status=201)


class OrganisationUsersView(APIView):
    permission_classes = [CanManageOrganisationUsers]

    def get(self, request):
        membership = current_membership(request.user)
        users = User.objects.filter(memberships__organisation=membership.organisation).distinct()
        return Response(UserSerializer(users, many=True).data)

    def post(self, request):
        membership = current_membership(request.user)
        serializer = UserCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        if User.objects.filter(username=serializer.validated_data["username"]).exists():
            return Response({"detail": "Cet identifiant est déjà utilisé."}, status=400)
        user = serializer.save()
        role = request.data.get("role", "bibliothecaire")
        allowed_roles = {"admin", "bibliothecaire"}
        if role not in allowed_roles:
            return Response({"detail": "Rôle utilisateur invalide."}, status=400)

        bibliotheque_id = request.data.get("bibliotheque") or request.data.get("bibliotheque_id")
        bibliotheque = None
        if bibliotheque_id:
            try:
                bibliotheque = Bibliotheque.objects.get(id=bibliotheque_id, organisation=membership.organisation)
            except (Bibliotheque.DoesNotExist, ValueError):
                return Response({"detail": "Cette bibliothèque n'appartient pas à votre organisation."}, status=400)

        Membership.objects.create(
            user=user,
            organisation=membership.organisation,
            role=role,
            bibliotheque=bibliotheque
        )
        return Response(UserSerializer(user).data, status=201)


class OrganisationUserDetailView(APIView):
    permission_classes = [CanManageOrganisationUsers]

    def get_membership(self, request, user_id):
        membership = current_membership(request.user)
        return Membership.objects.filter(
            user_id=user_id,
            organisation=membership.organisation,
        ).select_related("user").first()

    def patch(self, request, user_id):
        membership = current_membership(request.user)
        target = self.get_membership(request, user_id)
        if not target:
            return Response({"detail": "Utilisateur non trouvé."}, status=404)
        if target.user_id == request.user.id:
            return Response({"detail": "Vous ne pouvez pas modifier votre propre accès ici."}, status=400)

        update_fields = []
        if "role" in request.data:
            role = request.data.get("role")
            if role not in {"admin", "bibliothecaire"}:
                return Response({"detail": "Rôle utilisateur invalide."}, status=400)
            target.role = role
            update_fields.append("role")

        if "bibliotheque" in request.data or "bibliotheque_id" in request.data:
            bibliotheque_id = request.data.get("bibliotheque") or request.data.get("bibliotheque_id")
            if bibliotheque_id:
                try:
                    target.bibliotheque = Bibliotheque.objects.get(id=bibliotheque_id, organisation=membership.organisation)
                except (Bibliotheque.DoesNotExist, ValueError):
                    return Response({"detail": "Cette bibliothèque n'appartient pas à votre organisation."}, status=400)
            else:
                target.bibliotheque = None
            update_fields.append("bibliotheque")

        if update_fields:
            target.save(update_fields=update_fields)

        serializer = UserSerializer(target.user)
        return Response(serializer.data)

    def delete(self, request, user_id):
        target = self.get_membership(request, user_id)
        if not target:
            return Response({"detail": "Utilisateur non trouvé."}, status=404)
        if target.user_id == request.user.id or target.role == "owner":
            return Response({"detail": "Cet accès ne peut pas être supprimé."}, status=400)
        target.user.delete()
        return Response(status=204)

#Création d'un user lors de l'inscription
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [IsAdminUser]