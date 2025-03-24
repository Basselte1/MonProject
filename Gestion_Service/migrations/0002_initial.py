# Generated by Django 5.1.4 on 2025-03-21 13:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Gestion_Service', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='demandeservice',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='demandes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='devis',
            name='demande',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='devis', to='Gestion_Service.demandeservice'),
        ),
        migrations.AddField(
            model_name='facture',
            name='devis',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='facture', to='Gestion_Service.devis'),
        ),
        migrations.AddField(
            model_name='service',
            name='categorie',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='Gestion_Service.categorie'),
        ),
        migrations.AddField(
            model_name='demandeservice',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='demandes', to='Gestion_Service.service'),
        ),
    ]
