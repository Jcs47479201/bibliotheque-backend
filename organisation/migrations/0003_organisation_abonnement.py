from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("organisation", "0002_membership")]

    operations = [
        migrations.AddField(
            model_name="organisation",
            name="abonnement_plan",
            field=models.CharField(default="standard", max_length=50),
        ),
        migrations.AddField(
            model_name="organisation",
            name="abonnement_statut",
            field=models.CharField(
                choices=[("active", "Active"), ("trial", "Essai"), ("suspended", "Suspendue"), ("expired", "Expirée")],
                default="trial",
                max_length=20,
            ),
        ),
        migrations.AddField(model_name="organisation", name="abonnement_debut", field=models.DateField(blank=True, null=True)),
        migrations.AddField(model_name="organisation", name="abonnement_fin", field=models.DateField(blank=True, null=True)),
    ]