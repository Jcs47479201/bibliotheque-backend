from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from organisation.models import Membership
from .models import *
from .serializers import *
from users.permissions import IsClientMember





##################################
#           Gestion des Wiews    #
#         Affichage des views    #
##################################

class MyCategoriesView(APIView):
    permission_classes = [IsClientMember]

    def get(self, request):
        membership = Membership.objects.filter(user=request.user).first()
        if not membership:
            return Response(
                {"detail": "Aucune organisation associée à cet utilisateur."},
                status=404
            )

        categories = Categorie.objects.filter(
            bibliotheque__organisation=membership.organisation
        )
        serializer = CategorieSerializer(categories, many=True)

        return Response(serializer.data)


class CategorieCreateView(APIView):
    permission_classes = [IsClientMember]

    def post(self, request):
        membership = Membership.objects.filter(user=request.user).first()
        if not membership:
            return Response({"detail": "Aucune organisation associée à cet utilisateur."}, status=404)

        serializer = CategorieSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        bibliotheque = serializer.validated_data["bibliotheque"]
        if bibliotheque.organisation != membership.organisation:
            return Response({"detail": "Cette bibliothèque n'appartient pas à votre organisation."}, status=403)

        #Vérifier si une catégorie existe déjà
        if Categorie.objects.filter(bibliotheque__organisation=membership.organisation).filter(nom=serializer.validated_data["nom"]).exists():
            return Response(
                {"detail": "Une catégorie avec ce nom existe déjà."},
                status=400
            )

        categorie = serializer.save()
        return Response(CategorieSerializer(categorie).data, status=201)

class CategorieDetailView(APIView):
    permission_classes = [IsClientMember]

    def get_object(self, categorie_id, organisation):
        try:
            return Categorie.objects.get(
                id=categorie_id,
                bibliotheque__organisation=organisation,
            )
        except Categorie.DoesNotExist:
            return None

    def patch(self, request, categorie_id):
        membership = Membership.objects.filter(user=request.user).first()
        if not membership:
            return Response({"detail": "Aucune organisation associée à cet utilisateur."}, status=404)

        categorie = self.get_object(categorie_id, membership.organisation)
        if not categorie:
            return Response({"detail": "Catégorie non trouvée."}, status=404)

        serializer = CategorieSerializer(categorie, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        bibliotheque = serializer.validated_data.get("bibliotheque", categorie.bibliotheque)
        if bibliotheque.organisation != membership.organisation:
            return Response({"detail": "Cette bibliothèque n'appartient pas à votre organisation."}, status=403)

        return Response(CategorieSerializer(serializer.save()).data)

    def delete(self, request, categorie_id):
        membership = Membership.objects.filter(user=request.user).first()
        if not membership:
            return Response({"detail": "Aucune organisation associée à cet utilisateur."}, status=404)

        categorie = self.get_object(categorie_id, membership.organisation)
        if not categorie:
            return Response({"detail": "Catégorie non trouvée."}, status=404)

        categorie.delete()
        return Response(status=204)

#La gestion des auteurs.next
class MyAuteursView(APIView):
    permission_classes = [IsClientMember]

    def get(self, request):
        membership = Membership.objects.filter(user=request.user).first()

        if not membership:
            return Response(
                {"detail": "Aucune organisation associée à cet utilisateur."},
                status=404
            )

        auteurs = Auteur.objects.filter(bibliotheque__organisation=membership.organisation)
        serializer = AuteurSerializer(auteurs,many=True)

        return Response(serializer.data)

#La gestion des livres.next
class MyLivresView(APIView):
    permission_classes = [IsClientMember]

    def get(self, request):
        membership = Membership.objects.filter(user=request.user).first()
        if not membership:
            return Response(
                {"detail": "Aucune organisation associée à cet utilisateur."}, status=404
            )
        livres = Livre.objects.filter(bibliotheque__organisation=membership.organisation)
        serializer = LivreSerializer(livres,many=True)
        return Response(serializer.data)


##################################
#           Gestion des Posts    #
#         Création  des views    #
##################################

#Création des livres avec des auteurs existants
class LivreCreateView(APIView):
    permission_classes = [IsClientMember]

    def post(self, request):

        membership = Membership.objects.filter(
            user=request.user
        ).first()

        if not membership:
            return Response(
                {"detail": "Aucune organisation associée à cet utilisateur."},
                status=403
            )

        organisation = membership.organisation

        serializer = LivreCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=400
            )

        bibliotheque = serializer.validated_data["bibliotheque"]
        categorie = serializer.validated_data["categorie"]
        auteurs = serializer.validated_data["auteurs"]

        # Vérifier la bibliothèque
        if bibliotheque.organisation != organisation:
            return Response(
                {"detail": "Cette bibliothèque n'appartient pas à votre organisation."},
                status=403
            )

        # Vérifier la catégorie
        if categorie.bibliotheque != bibliotheque:
            return Response(
                {"detail": "Cette catégorie n'appartient pas à cette bibliothèque."},
                status=403
            )

        # Vérifier l'auteur
        if any(auteur.bibliotheque.organisation != organisation for auteur in auteurs):
            return Response(
                {"detail": "Un auteur n'appartient pas à votre organisation."},
                status=403
            )

        #Vérifier si un livre avec ce titre existe déjà
        if Livre.objects.filter(bibliotheque__organisation=membership.organisation).filter(titre=serializer.validated_data["titre"]).exists():
            return Response(
                {"detail": "Un livre avec ce titre existe déjà."},
                status=400
            )
        livre = serializer.save()
        return Response(LivreSerializer(livre).data,status=201)


##########################Création des auteurs ################################
class AuteurCreateView(APIView):
    permission_classes = [IsClientMember]

    def post(self, request):
        membership = Membership.objects.filter(user=request.user).first()

        if not membership:
            return Response(
                {"detail": "Aucune organisation associée à cet utilisateur."},
                status=404
            )

        serializer = AuteurCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        bibliotheque = serializer.validated_data.get("bibliotheque")
        if bibliotheque:
            if bibliotheque.organisation != membership.organisation:
                return Response(
                    {"detail": "Cette bibliothèque n'appartient pas à votre organisation."},
                    status=403
                )
        else:
            bibliotheque = membership.bibliotheque or Bibliotheque.objects.filter(organisation=membership.organisation).first()

        if not bibliotheque:
            return Response(
                {"detail": "Aucune bibliothèque trouvée dans cette organisation. Veuillez d'abord en créer une."},
                status=400
            )

        # Vérifier si un auteur existe déjà dans cette organisation
        if Auteur.objects.filter(bibliotheque__organisation=membership.organisation, nom=serializer.validated_data["nom"]).exists():
            return Response(
                {"detail": "Un auteur avec ce nom existe déjà dans votre organisation."},
                status=400
            )

        auteur = serializer.save(bibliotheque=bibliotheque)
        return Response(AuteurSerializer(auteur).data, status=201)

### Update & Delete d'un auteur
class AuteurDetailView(APIView):
    permission_classes = [IsClientMember]

    def get_object(self, auteur_id, organisation):
        try:
            return Auteur.objects.get(
                id=auteur_id,
                bibliotheque__organisation=organisation
            )
        except (Auteur.DoesNotExist, ValueError):
            return None

    def patch(self, request, auteur_id):
        membership = Membership.objects.filter(user=request.user).first()

        if not membership:
            return Response({"detail": "Aucune organisation associée à cet auteur."},
                status=404
            )

        auteur = self.get_object(auteur_id, membership.organisation)
        if not auteur:
            return Response(
                {"detail": "Auteur non trouvé."},
                status=404
            )

        serializer = AuteurSerializer(auteur, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        bibliotheque = serializer.validated_data.get("bibliotheque")
        if bibliotheque and bibliotheque.organisation != membership.organisation:
            return Response({"detail": "Cette bibliothèque n'appartient pas à votre organisation."}, status=403)

        serializer.save()
        return Response(serializer.data)

    def delete(self, request, auteur_id):
        membership = Membership.objects.filter(user=request.user).first()

        if not membership:
            return Response(
                {"detail": "Aucune organisation associée à cet utilisateur."},
                status=404
            )

        auteur = self.get_object(auteur_id, membership.organisation)
        if not auteur:
            return Response(
                {"detail": "Auteur non trouvé."},
                status=404
            )

        auteur.delete()
        return Response(status=204)