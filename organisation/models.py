from django.db import models
import uuid
from django.conf import settings

# Create your models here.
class Organisation(models.Model):
    """ represente une bibliotheque"""
    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom=models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    email=models.EmailField(max_length=100)
    telephone=models.CharField(max_length=100)
    adresse=models.TextField(null=True,blank=True)
    logo = models.ImageField(upload_to='organisations/logos/', null=True, blank=True)
    date_creation=models.DateField(auto_now_add=True)
    active=models.BooleanField(default=True)
    
    SUBSCRIPTION_STATUS = [("active", "Active"), ("trial", "Essai"), ("suspended", "Suspendue"), ("expired", "Expirée")]
    abonnement_plan = models.CharField(max_length=50, default="standard")
    abonnement_statut = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS, default="trial")
    abonnement_debut = models.DateField(null=True, blank=True)
    abonnement_fin = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Organisation"
        verbose_name_plural = "Organisations"
    
    def __str__(self):
        return self.nom
    

class Membership(models.Model):
    ROLE_CHOICES = [("owner", "Propriétaire"),("admin", "Administrateur"),("bibliothecaire", "Bibliothécaire"),]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="memberships")
    organisation = models.ForeignKey(Organisation,on_delete=models.CASCADE,related_name="organisations")
    role = models.CharField(max_length=30,choices=ROLE_CHOICES)  
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "organisation"],
                name="unique_user_organisation"
            )
        ]

    def __str__(self):
        return f"{self.user} - {self.organisation} - {self.role}"