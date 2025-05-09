
import logging
import os

from django.core.files.base import ContentFile
from django.db import models
from django.template.loader import render_to_string


from django.utils.timezone import now
from weasyprint import HTML, CSS

from AppGestionService import settings

logger = logging.getLogger(__name__)


# mes class => tables de ma BD
################################################## #####################################

# ✅ Modèle Catégorie
class Categorie(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField(default= "")
    date_creation =models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-date_creation'] #LIFVIEW

    def __str__(self):
        return self.nom


###########################################################################

from django.urls import reverse

# ✅ Modèle Services
class Service(models.Model):
    nom = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to= 'images', blank=True, null=True)
    date_creation = models.DateField(auto_now=True)
    # une categorie contient plusieurs services.
    categorie = models.ForeignKey(Categorie, related_name = 'services',on_delete= models.CASCADE)

    class Meta:
        ordering = ['-date_creation'] #LIFview
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse('home')
    
###############################################################################################################

from utilisateurs.models import User

# ✅ Modèle Demande
class DemandeService(models.Model):

    description = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True) # mise à jour a chaque modification

    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="demandes") # est demandé N fois
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name="demandes") # demande N fois
    
    fichier = models.FileField(upload_to='demandes/', blank=True, null=True)  # Permetre de stocke un fichier dans la demande lors de l'envois.

    #sattut de la demande
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('VALIDÉE', 'Validée'),
        ('REFUSÉE', 'Refusée'),
    ]
    statut = models.CharField(max_length=12, choices=STATUT_CHOICES, default='EN_ATTENTE')

    class Meta:
        ordering = ['-date_creation']  #LIFview
        verbose_name = "DemandeService"
        verbose_name_plural = "DemandeServices"


    def __str__(self):
        return f"Demande {self.pk} - {self.statut}"
    
###########################################################################################################################
# model devis
from django.core.files.storage import FileSystemStorage
from decimal import Decimal
from django.core.validators import MinValueValidator

fs = FileSystemStorage(location='media/')

class Devis(models.Model):

    # empêche plusieurs devis pour une meme demande
    demande = models.OneToOneField(DemandeService, on_delete=models.CASCADE, related_name='devis',unique=True)
    fichier = models.FileField(upload_to='devis/', storage=fs,null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    duree = models.IntegerField(default=10,help_text="en jours")

    # Champs pour les détails de la prestation
    description = models.TextField(default="")  # Ex: "Développement d'application web avec Django et React"

    validite = models.IntegerField(default=10,help_text="en jours") #


    cout_backend = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    cout_frontend = models.DecimalField(max_digits=15, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    cout_test = models.DecimalField(max_digits=15, decimal_places=2, default=0,help_text="Coût_test") # cout pour les tests
    cout_maintenance = models.DecimalField(max_digits=15, decimal_places=2, default=0,help_text="Coût_maintenance")

    cout_hebergement = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text=" Coût_l'hébergement")
    cout_nom_de_domaine = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text="Coût_nom de domaine")

    # Statut du devis
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('VALIDÉ', 'Validé'),
        ('REFUSÉ', 'Refusé'),
    ]
    statut = models.CharField(max_length=12, choices=STATUT_CHOICES, default='EN_ATTENTE')

    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Devis"
        verbose_name_plural = "Devis"

    def __str__(self):
        return f"Devis {self.pk} - {self.demande.client.username}"

    # Fonctions pour calculer les montants

    def calcul_total_ht(self):
        """ Calcule le total hors taxes (HT). """
        return sum(filter(None, [ # filter(None) pour ignorer les valeurs null
            self.cout_backend,
            self.cout_frontend,
            self.cout_test,
            self.cout_maintenance,
            self.cout_hebergement,
            self.cout_nom_de_domaine

        ]))

    def calcul_tva(self):

        """ Calcule la TVA sur le total HT. Par défaut, TVA à 20%. """
        taux_tva= Decimal("0.20")
        return self.calcul_total_ht() * taux_tva

    def calcul_total_ttc(self):
        """ Calcule le total TTC (HT + TVA). """
        return self.calcul_total_ht() + self.calcul_tva()

###############################################################

from django.db import models
from django.utils.timezone import now
from decimal import Decimal
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from django.core.files.base import ContentFile
from django.conf import settings
import os
import traceback

class Facture(models.Model):
    description = models.TextField(null=True, max_length=1000, blank=True)
    date_creation = models.DateField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True, null=True, blank=True)
    validite = models.IntegerField(default=10,help_text="en jours")
    devis = models.OneToOneField("Devis", on_delete=models.CASCADE, related_name="facture", null=True, blank=True)

    STATUT_CHOICES = [('PAYEE', 'Payée'), ('IMPAYEE', 'Impayée'), ('EN_ATTENTE', 'En attente')]
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='EN_ATTENTE')

    quantite = models.IntegerField(default=10, help_text="en jours")
    fichier_pdf = models.FileField(upload_to='factures/', blank=True, null=True)
    numero_facture = models.CharField(max_length=20, unique=True, blank=True, null=True)

    class Meta:
        ordering = ['-date_creation']
        verbose_name = "Facture"
        verbose_name_plural = "Factures"

    def save(self, *args, **kwargs):
        try:
            # 1. Sauvegarde initiale si pk n'existe pas
            if not self.pk:
                super().save(*args, **kwargs)

            # 2. Génération du numéro de facture
            if not self.numero_facture:
                date_part = now().strftime("%Y%m%d")
                self.numero_facture = f"FAC-{date_part}-{str(self.pk).zfill(6)}"

            # 3. Sauvegarde finale avec numéro
            super().save(*args, **kwargs)

        except Exception as e:
            print("Erreur lors de l'enregistrement de la facture:", e)
            print(traceback.format_exc())

    def __str__(self):
        try:
            return f"{self.numero_facture or self.pk} - {self.montant_ttc} FCFA"
        except:
            return str(self.pk)

    @property
    def montant_ht(self):
        return self.devis.calcul_total_ht() if self.devis else Decimal("0.00")

    @property
    def montant_tva(self):
        return self.devis.calcul_tva() if self.devis else Decimal("0.00")

    @property
    def montant_ttc(self):
        return self.devis.calcul_total_ttc() if self.devis else Decimal("0.00")

    def get_client(self):
        if self.devis and self.devis.demande:
            return self.devis.demande.client
        return None

    def get_service(self):
        if self.devis and self.devis.demande:
            return self.devis.demande.service
        return None

    def generate_pdf(self):
        try:
            client = self.get_client()

            context = {
                "client_nom": getattr(client, "username", "Inconnu"),
                "client_email": getattr(client, "email", "inconnu@example.com"),
                "client_entreprise": getattr(client, "entreprise", "Nom entreprise non défini"),
                "client_adresse": getattr(client, "adresse", "Pas d'adresse mentionnée"),
                "validite": self.validite,
                "description": self.description,
                "duree": self.quantite,
                "date_creation": self.date_creation,
                "total_ht": self.montant_ht,
                "tva": self.montant_tva,
                "total_ttc": self.montant_ttc,
                "facture": self.numero_facture
            }

            html_string = render_to_string('facture_template.html', context)
            css_path = os.path.join(settings.BASE_DIR, 'static/css/facture.css')

            if not os.path.exists(css_path):
                print("⚠️ Le fichier CSS est introuvable")
                return False

            pdf_file = HTML(string=html_string).write_pdf(stylesheets=[CSS(css_path)])
            filename = f"facture_{self.pk}.pdf"

            if self.fichier_pdf:
                self.fichier_pdf.close()
                self.fichier_pdf.delete(save=True)

            self.fichier_pdf.save(filename, ContentFile(pdf_file), save=False)
            self.save()
            return True

        except Exception as e:
            print("❌ Erreur lors de la génération du PDF :", str(e))
            print(traceback.format_exc())
            return False  # L'application continue à fonctionner sans planter


####################################################################################

