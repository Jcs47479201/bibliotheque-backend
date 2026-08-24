from django.contrib import admin
from .models import Categorie, Auteur, Livre


# Register your models here.
admin.site.register(Categorie)
admin.site.register(Auteur)
admin.site.register(Livre)