from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from organisation.models import Membership
from .models import *
from .serializers import *
from users.permissions import IsClientMember, current_membership, has_library_access


# Create your views here.
#Get des emprunts
class EmpruntView(APIView):
    permission_classes = [IsClientMember]

    def get(self, request):
        membership = current_membership(request.user)

        if not membership:
            return Response({"detail": "Aucune organisation associée à cet emprunt."}, status=404)
    
        if membership.bibliotheque:
            emprunts = Emprunt.objects.filter(bibliotheque=membership.bibliotheque)
        else:
            emprunts = Emprunt.objects.filter(bibliotheque__organisation=membership.organisation)
        serializer = EmpruntSerializer(emprunts, many=True)
        return Response(serializer.data)

#création des emprunts
class EmpruntCreateAPI(APIView):
    permission_classes = [IsClientMember]

    def post(self, request):
        membership = current_membership(request.user)

        if not membership:
            return Response(
                {"detail": "Aucune organisation associée à cet utilisateur."},
                status=404
            )

        data = request.data.copy() if hasattr(request.data, "copy") else dict(request.data)
        if not data.get("date_limite"):
            from django.utils import timezone
            from datetime import timedelta
            data["date_limite"] = (timezone.now() + timedelta(days=14)).isoformat()

        serializer = EmpruntCreateSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        livre = serializer.validated_data["livre"]
        adherent = serializer.validated_data["adherent"]

        # Vérification des autorisations sur la bibliothèque
        if not has_library_access(membership, livre.bibliotheque):
            return Response(
                {"detail": "Vous n'avez pas l'autorisation de prêter un livre de cette bibliothèque."},
                status=403
            )

        if not has_library_access(membership, adherent.bibliotheque):
            return Response(
                {"detail": "Vous n'avez pas l'autorisation d'enregistrer un prêt pour un adhérent d'une autre bibliothèque."},
                status=403
            )

        emprunt = serializer.save(bibliotheque=livre.bibliotheque)
        return Response(EmpruntSerializer(emprunt).data, status=201)

#Update & Delete des emprunts
class EmpruntDetailView(APIView):
    permission_classes = [IsClientMember]

    def get_object(self, emprunt_id, membership):
        try:
            if membership.bibliotheque:
                return Emprunt.objects.get(
                    id=emprunt_id,
                    bibliotheque=membership.bibliotheque
                )
            return Emprunt.objects.get(
                id=emprunt_id,
                bibliotheque__organisation=membership.organisation
            )
        except (Emprunt.DoesNotExist, ValueError):
            return None


    #Update des emprunts
    def patch(self, request, emprunt_id):
        membership = current_membership(request.user)

        if not membership:
            return Response({"detail": "Aucune organisation associée à cet emprunt."}, status=404)
    
        emprunt = self.get_object(emprunt_id, membership)
        if not emprunt:
            return Response(
                {"detail": "Emprunt non trouvé ou accès non autorisé."},
                status=404
            )

        serializer = EmpruntSerializer(emprunt, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, emprunt_id):
        membership = current_membership(request.user)

        if not membership:
            return Response({"detail": "Aucune organisation associée à cet emprunt."}, status=404)
    
        emprunt = self.get_object(emprunt_id, membership)
        if not emprunt:
            return Response(
                {"detail": "Emprunt non trouvé ou accès non autorisé."},
                status=404
            )

        emprunt.delete()
        return Response({"detail": "Emprunt supprimé avec succès."})