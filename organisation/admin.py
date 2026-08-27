from django.contrib import admin
from .models import Organisation, Membership


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
	list_display = ("nom", "slug", "email", "telephone", "abonnement_plan", "abonnement_statut", "active", "date_creation")
	search_fields = ("nom", "email", "slug")
	list_filter = ("abonnement_statut", "abonnement_plan", "active")
	prepopulated_fields = {"slug": ("nom",)}


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
	list_display = ("user", "organisation", "role", "bibliotheque", "date_creation")
	search_fields = ("user__username", "user__email", "organisation__nom")
	list_filter = ("role", "organisation", "bibliotheque")