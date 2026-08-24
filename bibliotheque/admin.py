from django.contrib import admin
from .models import Bibliotheque, Adherent

# Register your models here.

class BibliothequeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'adresse', 'telephone', 'email', 'statut')
    list_filter = ('statut',)
    search_fields = ('nom', 'adresse', 'telephone', 'email', 'statut')
    ordering = ('nom',)

admin.site.register(Bibliotheque, BibliothequeAdmin)
admin.site.register(Adherent)
