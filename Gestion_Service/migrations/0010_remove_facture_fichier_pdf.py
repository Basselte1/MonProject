# Generated by Django 5.1.4 on 2025-04-10 22:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Gestion_Service', '0009_alter_devis_validite'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='facture',
            name='fichier_pdf',
        ),
    ]
