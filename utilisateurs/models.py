from django.contrib.auth.models import AbstractUser
from django.db import models

# ✅ Modèle Utilisateur
class User(AbstractUser):
    """
    Classe représentant un utilisateur personnalisé.
    Elle hérite du modèle AbstractUser de Django et ajoute des champs supplémentaires.
    """

    adresse = models.TextField(blank=True, null=True)  # Adresse du client (facultatif)
    entreprise = models.CharField(max_length=255, blank=True, null=True)  # Nom de l'entreprise du client (facultatif)

    # Vous n'avez pas besoin de redéfinir is_active ou is_staff car ces champs existent déjà dans AbstractUser

    class Meta:
        verbose_name = "Client/admin"  # Nom de l'utilisateur dans l'administration
        verbose_name_plural = "Clients/admin"  # Nom pluriel dans l'administration

    def __str__(self):
        """
        Cette méthode permet de représenter l'utilisateur sous forme de chaîne de caractères.
        Elle affiche le nom d'utilisateur et le nom de l'entreprise si disponible.
        """
        return f"{self.username} - {self.entreprise if self.entreprise else 'Particulier'}"
