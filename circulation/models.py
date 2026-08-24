import uuid
from django.db import models
from bibliotheque.models import Bibliotheque, Adherent
from catalogue.models import Livre

#Création du model Emprunt
class Emprunt(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    bibliotheque = models.ForeignKey(Bibliotheque,on_delete=models.CASCADE, related_name="emprunts")
    livre = models.ForeignKey(Livre,on_delete=models.PROTECT,related_name="emprunts")
    adherent = models.ForeignKey(Adherent,on_delete=models.PROTECT,related_name="emprunts")
    date_emprunt = models.DateTimeField(auto_now_add=True)
    date_limite = models.DateTimeField()
    date_retour = models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return f"{self.adherent} - {self.livre} -- {self.date_emprunt} -- {self.date_limite}"

