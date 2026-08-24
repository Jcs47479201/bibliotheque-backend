from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from organisation.models import Membership
from .models import *
from .serializers import *
from users.permissions import IsClientMember


# Create your views here.
#Get des emprunts
class EmpruntView(APIView):
    permission_classes = [IsClientMember]

    def get(self, request):
        membership = Membership.objects.filter(user=request.user).first()

        if not membership:
            return Response({"detail": "Aucune organisation associée à cet emprunt."})
    
        emprunts = Emprunt.objects.filter(bibliotheque__organisation=membership.organisation)
        serializer = EmpruntSerializer(emprunts, many=True)
        return Response(serializer.data)

#création des emprunts
class EmpruntCreateAPI(APIView):
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

            #vérification de livres
            if livre.organisation != organisation:
                return Response(
                    {"detail": "Ce livre n'appartient pas à votre organisation."},
                    status=404
                )
            
            #vérification de l'Adhérents
            if adherent.bibliotheque.organisation != organisation:
                return Response(
                    {"detail": "Cet adhérent n'appartient pas à votre organisation."},
                    status=404
                )
        serializer = EmpruntCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(bibliotheque=bibliotheque)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

#Update & Delete des emprunts
class EmpruntDetailView(APIView):
    permission_classes = [IsClientMember]

    def get_object(self, emprunt_id, organisation):
        try:
            return Emprunt.objects.get(
                id=emprunt_id,
                bibliotheque__organisation=organisation
            )
        except Emprunt.DoesNotExist:
            return None


    #Update des emprunts
    def patch(self, request, emprunt_id):
        membership = Membership.objects.filter(user=request.user).first()

        if not membership:
            return Response({"detail": "Aucune organisation associée à cet emprunt."})
    
        emprunt = self.get_object(emprunt_id, membership.organisation)
        if not emprunt:
            return Response(
                {"detail": "Emprunt non trouvé."},
                status=404
            )

        serializer = EmpruntSerializer(emprunt, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, emprunt_id):
        membership = Membership.objects.filter(user=request.user).first()

        if not membership:
            return Response({"detail": "Aucune organisation associée à cet emprunt."})
    
        emprunt = self.get_object(emprunt_id, membership.organisation)
        if not emprunt:
            return Response(
                {"detail": "Emprunt non trouvé."},
                status=404
            )

        emprunt.delete()
        return Response({"detail": "Emprunt supprimé avec succès."})