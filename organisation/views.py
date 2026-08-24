from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Membership, Organisation
from .serializers import OrganisationSerializer
from users.permissions import IsPlatformOwner


class MyOrganisationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        membership = Membership.objects.filter(user=request.user).first()
        if not membership:
            return Response(
                {"detail": "Aucune organisation associée à cet utilisateur."},
                status=404
            )
        serializer = OrganisationSerializer(membership.organisation)

        return Response(serializer.data)

#Création d'une organisation
class OrganisationCreateView(APIView):
    permission_classes = [IsPlatformOwner]

    def post(self, request):
        serializer = OrganisationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        organisation = serializer.save()
        Membership.objects.get_or_create(user=request.user, organisation=organisation, defaults={"role": "owner"})
        return Response(OrganisationSerializer(organisation).data, status=201)


class PlatformOrganisationsView(APIView):
    permission_classes = [IsPlatformOwner]

    def get(self, request):
        return Response(OrganisationSerializer(Organisation.objects.all().order_by("nom"), many=True).data)

    def post(self, request):
        return OrganisationCreateView().post(request)


class PlatformOrganisationDetailView(APIView):
    permission_classes = [IsPlatformOwner]

    def patch(self, request, organisation_id):
        try:
            organisation = Organisation.objects.get(id=organisation_id)
        except Organisation.DoesNotExist:
            return Response({"detail": "Organisation non trouvée."}, status=404)
        serializer = OrganisationSerializer(organisation, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        return Response(OrganisationSerializer(serializer.save()).data)