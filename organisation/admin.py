from django.contrib import admin
from django import forms
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils.text import slugify
from .models import Organisation, Membership
from bibliotheque.models import Bibliotheque

User = get_user_model()


class OrganisationSpaceForm(forms.ModelForm):
	responsable_username = forms.CharField(label="Identifiant du responsable", max_length=150)
	responsable_email = forms.EmailField(label="Email du responsable")
	responsable_password = forms.CharField(label="Mot de passe du responsable", min_length=8, widget=forms.PasswordInput)
	bibliotheque_nom = forms.CharField(label="Nom de la bibliothèque", max_length=255)
	bibliotheque_adresse = forms.CharField(label="Adresse de la bibliothèque", required=False, widget=forms.Textarea)

	class Meta:
		model = Organisation
		fields = ("nom", "email", "telephone", "adresse", "abonnement_plan", "abonnement_statut")

	def clean_responsable_username(self):
		username = self.cleaned_data["responsable_username"]
		if User.objects.filter(username=username).exists():
			raise forms.ValidationError("Cet identifiant est déjà utilisé.")
		return username

	def clean_nom(self):
		nom = self.cleaned_data["nom"]
		if Organisation.objects.filter(slug=slugify(nom)).exists():
			raise forms.ValidationError("Cette organisation existe déjà.")
		return nom

	def clean_bibliotheque_nom(self):
		nom = self.cleaned_data["bibliotheque_nom"]
		if Bibliotheque.objects.filter(slug=slugify(nom)).exists():
			raise forms.ValidationError("Cette bibliothèque existe déjà.")
		return nom


@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
	form = OrganisationSpaceForm
	list_display = ("nom", "email", "abonnement_statut", "active")
	search_fields = ("nom", "email", "slug")

	def has_add_permission(self, request):
		return request.user.is_superuser

	def has_change_permission(self, request, obj=None):
		return False

	def has_delete_permission(self, request, obj=None):
		return request.user.is_superuser

	@transaction.atomic
	def save_model(self, request, obj, form, change):
		super().save_model(request, obj, form, change)
		user = User.objects.create_user(
			username=form.cleaned_data["responsable_username"],
			email=form.cleaned_data["responsable_email"],
			password=form.cleaned_data["responsable_password"],
		)
		Membership.objects.create(user=user, organisation=obj, role="owner")
		Bibliotheque.objects.create(
			nom=form.cleaned_data["bibliotheque_nom"],
			organisation=obj,
			adresse=form.cleaned_data["bibliotheque_adresse"],
			telephone=obj.telephone,
			email=obj.email,
			slug=slugify(form.cleaned_data["bibliotheque_nom"]),
		)



# Register your models here.
admin.site.register(Membership)