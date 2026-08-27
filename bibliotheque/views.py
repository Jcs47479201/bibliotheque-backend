from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from .models import Bibliotheque, Adherent
from organisation.models import Membership
from .serializers import BibliothequeSerializer, AdherentSerializer, AdherentCreateSerializer
from users.permissions import IsClientMember, IsPlatformOwner, current_membership, has_library_access


class MyBibliothequesView(APIView):
    permission_classes = [IsClientMember]

    def get(self, request):
        membership = current_membership(request.user)

        if not membership:
            return Response(
                {"detail": "Aucune organisation associée à cet utilisateur."},
                status=404
            )

        if membership.bibliotheque:
            bibliotheques = Bibliotheque.objects.filter(id=membership.bibliotheque.id)
        else:
            bibliotheques = Bibliotheque.objects.filter(organisation=membership.organisation)

        serializer = BibliothequeSerializer(
            bibliotheques,
            many=True
        )

        return Response(serializer.data)


class PlatformBibliothequesView(APIView):
    permission_classes = [IsPlatformOwner]

    def get(self, request):
        libraries = Bibliotheque.objects.select_related("organisation").order_by("nom")
        return Response(BibliothequeSerializer(libraries, many=True).data)

    @transaction.atomic
    def post(self, request):
        serializer = BibliothequeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        library = serializer.validated_data["organisation"]
        if not library.active:
            return Response({"detail": "Cette organisation est inactive."}, status=400)
        library = serializer.save()
        return Response(BibliothequeSerializer(library).data, status=201)

#Affichage des adhérents d'une bibliothèque
class MyAdherentsView(APIView):
    permission_classes = [IsClientMember]

    def get(self, request, bibliotheque_id):
        membership = current_membership(request.user)

        if not membership:
            return Response(
                {"detail": "Aucune organisation associée à cet utilisateur."},
                status=404
            )

        if membership.bibliotheque and str(bibliotheque_id) != str(membership.bibliotheque.id):
            return Response(
                {"detail": "Vous n'avez pas l'autorisation d'accéder aux adhérents de cette bibliothèque."},
                status=403
            )

        try:
            bibliotheque = Bibliotheque.objects.get(
                id=bibliotheque_id,
                organisation=membership.organisation
            )
        except (Bibliotheque.DoesNotExist, ValueError):
            return Response(
                {"detail": "Bibliothèque non trouvée."},
                status=404
            )

        adherents = bibliotheque.adherent_set.all()
        serializer = AdherentSerializer(adherents, many=True)

        return Response(serializer.data)
    
################################################
# Création d'un adhérent pour une bibliothèque #
################################################
class AdherentCreateView(APIView):
    permission_classes = [IsClientMember]

    @transaction.atomic
    def post(self, request):
        membership = current_membership(request.user)

        if not membership:
            return Response(
                {"detail": "Aucune organisation associée à cet utilisateur."},
                status=404
            )

        serializer = AdherentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        bibliotheque = serializer.validated_data.get("bibliotheque")
        if membership.bibliotheque:
            if bibliotheque and str(bibliotheque.id) != str(membership.bibliotheque.id):
                return Response(
                    {"detail": "Vous n'avez pas l'autorisation de créer un adhérent dans une autre bibliothèque."},
                    status=403
                )
            bibliotheque = membership.bibliotheque
        else:
            if bibliotheque:
                if bibliotheque.organisation != membership.organisation:
                    return Response(
                        {"detail": "Cette bibliothèque n'appartient pas à votre organisation."},
                        status=403
                    )
            else:
                bibliotheque = Bibliotheque.objects.filter(organisation=membership.organisation).first()

        if not bibliotheque:
            return Response(
                {"detail": "Aucune bibliothèque trouvée dans cette organisation. Veuillez d'abord en créer une."},
                status=400
            )

        # Vérifier si un adhérent existe déjà dans cette bibliothèque
        if Adherent.objects.filter(bibliotheque=bibliotheque).filter(
            nom=serializer.validated_data["nom"], 
            prenom=serializer.validated_data["prenom"],
            email=serializer.validated_data["email"],
            contact=serializer.validated_data["contact"]
        ).exists():
            return Response(
                {"detail": "Un adhérent avec ces coordonnées existe déjà dans cette bibliothèque."},
                status=400
            )

        adherent = serializer.save(bibliotheque=bibliotheque)
        return Response(AdherentSerializer(adherent).data, status=201)

#######################################################################################################
# UPDATE & DELETE: Gestion de la mise à jour et de la suppression d'un adhérent pour une bibliothèque #
#######################################################################################################
class AdherentDetailView(APIView):
    permission_classes = [IsClientMember]

    def get_object(self, adherent_id, membership):
        try:
            if membership.bibliotheque:
                return Adherent.objects.get(
                    id=adherent_id,
                    bibliotheque=membership.bibliotheque
                )
            return Adherent.objects.get(
                id=adherent_id,
                bibliotheque__organisation=membership.organisation
            )
        except (Adherent.DoesNotExist, ValueError):
            return None

    def patch(self, request, adherent_id):
        membership = current_membership(request.user)

        if not membership:
            return Response({"detail": "Aucune organisation associée à cet utilisateur."},
                status=404
            )

        adherent = self.get_object(adherent_id, membership)
        if not adherent:
            return Response(
                {"detail": "Adhérent non trouvé ou accès non autorisé."},
                status=404
            )

        serializer = AdherentSerializer(adherent, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        bibliotheque = serializer.validated_data.get("bibliotheque")
        if bibliotheque and not has_library_access(membership, bibliotheque):
            return Response({"detail": "Vous n'avez pas l'autorisation d'agir sur cette bibliothèque."}, status=403)

        serializer.save()
        return Response(serializer.data)

    def delete(self, request, adherent_id):
        membership = current_membership(request.user)

        if not membership:
            return Response(
                {"detail": "Aucune organisation associée à cet utilisateur."},
                status=404
            )

        adherent = self.get_object(adherent_id, membership)
        if not adherent:
            return Response(
                {"detail": "Adhérent non trouvé ou accès non autorisé."},
                status=404
            )

        adherent.delete()
        return Response(status=204)