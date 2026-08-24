from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Bibliotheque, Adherent
from organisation.models import Membership
from .serializers import BibliothequeSerializer, AdherentSerializer, AdherentCreateSerializer
from users.permissions import IsClientMember, IsPlatformOwner


class MyBibliothequesView(APIView):
    permission_classes = [IsClientMember]

    def get(self, request):
        membership = Membership.objects.filter( user=request.user).first()

        if not membership:
            return Response(
                {"detail": "Aucune organisation associée à cet utilisateur."},
                status=404
            )

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
        membership = Membership.objects.filter(user=request.user).first()

        if not membership:
            return Response(
                {"detail": "Aucune organisation associée à cet utilisateur."},
                status=404
            )

        try:
            bibliotheque = Bibliotheque.objects.get(
                id=bibliotheque_id,
                organisation=membership.organisation
            )
        except Bibliotheque.DoesNotExist:
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

    def post(self, request):
        membership = Membership.objects.filter(user=request.user).first()

        if not membership:
            return Response(
                {"detail": "Aucune organisation associée à cet utilisateur."},
                status=404
            )

        try:
            bibliotheque = Bibliotheque.objects.get(
                organisation=membership.organisation
            )
        except Bibliotheque.DoesNotExist:
            return Response(
                {"detail": "Bibliothèque non trouvée."},
                status=404
            )

        serializer = AdherentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        # Vérifier si un adhérent existe déjà
        if Adherent.objects.filter(bibliotheque__organisation=membership.organisation).filter(
            nom=serializer.validated_data["nom"], 
            prenom=serializer.validated_data["prenom"],
            email=serializer.validated_data["email"],
            contact=serializer.validated_data["contact"]
        ).exists():
            return Response(
                {"detail": "Un adhérent avec ce mail existe déjà."},
                status=400
            )

        serializer.save(bibliotheque=bibliotheque)
        return Response(serializer.data, status=201)

#######################################################################################################
# UPDATE & DELETE: Gestion de la mise à jour et de la suppression d'un adhérent pour une bibliothèque #
#######################################################################################################
class AdherentDetailView(APIView):
    permission_classes = [IsClientMember]

    def get_object(self, adherent_id, organisation):
        try:
            return Adherent.objects.get(
                id=adherent_id,
                bibliotheque__organisation=organisation
            )
        except Adherent.DoesNotExist:
            return None

    def patch(self, request, adherent_id):
        membership = Membership.objects.filter(user=request.user).first()

        if not membership:
            return Response({"detail": "Aucune organisation associée à cet utilisateur."},
                status=404
            )

        adherent = self.get_object(adherent_id, membership.organisation)
        if not adherent:
            return Response(
                {"detail": "Adhérent non trouvé."},
                status=404
            )

        serializer = AdherentSerializer(adherent, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, adherent_id):
        membership = Membership.objects.filter(user=request.user).first()

        if not membership:
            return Response(
                {"detail": "Aucune organisation associée à cet utilisateur."},
                status=404
            )

        adherent = self.get_object(adherent_id, membership.organisation)
        if not adherent:
            return Response(
                {"detail": "Adhérent non trouvé."},
                status=404
            )

        adherent.delete()
        return Response(status=204)