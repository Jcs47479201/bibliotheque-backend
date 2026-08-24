from django.db import models
from organisation.models import Organisation
import uuid

# Create your models here.
class Bibliotheque(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=255)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    adresse = models.TextField()
    telephone = models.CharField(max_length=255)
    email = models.EmailField()
    statut = models.CharField(max_length=255, default='actif')
    image = models.ImageField(null=True,blank=True,upload_to='media/bibliotheque')
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.nom

# Le models des adherent
class Adherent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bibliotheque = models.ForeignKey(Bibliotheque, on_delete=models.CASCADE)
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    email = models.EmailField()
    contact = models.CharField(max_length=255)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.prenom} -- {self.nom} -- {self.bibliotheque} -- {self.contact} -- {self.email}"