from django.db import models
from bibliotheque.models import Bibliotheque
import uuid

# Create your models here.
class Categorie(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=255)
    bibliotheque = models.ForeignKey(Bibliotheque, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return self.nom

class Auteur(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=255)
    bibliotheque = models.ForeignKey(Bibliotheque, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nom

class Livre(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titre = models.CharField(max_length=255)
    bibliotheque = models.ForeignKey(Bibliotheque, on_delete=models.CASCADE)
    auteurs = models.ManyToManyField(Auteur, related_name="livres")
    categorie = models.ForeignKey(Categorie, on_delete=models.PROTECT,related_name="livres")
    isbn=models.CharField(max_length=255)
    langue=models.CharField(max_length=255)
    pages=models.IntegerField()
    statut = models.CharField(max_length=20,choices=[("disponible", "Disponible"), ("emprunte", "Emprunté"), ("endommage", "Endommagé"), ("non_disponible", "Non disponible")],default="disponible")
    image = models.ImageField(null=True,blank=True,upload_to='media/livres')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.titre} -- {self.auteurs.all()} -- {self.langue}"