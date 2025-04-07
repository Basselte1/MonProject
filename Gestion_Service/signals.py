from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
import logging
from .models import DemandeService

#__name__ :filtrer les logs (ex. : n'afficher que les erreurs venant de ce module "app.signals").

logger = logging.getLogger(__name__) # crée un logger avec le nom du module.

@receiver(post_save, sender=DemandeService)
def notifier_admin_nouvelle_demande(sender, instance, created, **kwargs):
    if created:
        # voir si la fonction est bien exécutée.
        print("🚀 Signal post_save activé !")  # Test pour voir si le signal s'exécute
        logger.info("🚀 Signal post_save activé !")  # Ajout d'un log

        admin_email = "edjabeadam1@gmail.com"
        sujet = f"Nouveau devis demandé par {instance.client.username}"
        message = f"Un nouveau devis a été soumis pour le service : {instance.service.nom}."

        # Envoyer un e-mail
        try:
            send_mail(sujet, message, "noreply@tonsite.com", [admin_email])
        except Exception as e:
            logger.error(f"Erreur d'envoi de l'email : {e}")

     # enregistrement de la notification dans le modèle LogEntry
        if instance.client.is_staff:
            LogEntry.objects.log_action(
                user_id=instance.client.id,  # ID de l'admin qui fait l'action
                content_type_id=ContentType.objects.get_for_model(DemandeService).id,
                object_id=instance.id,
                object_repr=f"DemandeService {instance.id}",
                action_flag=ADDITION,
                change_message=f"Un nouveau devis a été soumis pour le service : {instance.service.nom}."
            )
        # ✅ L’admin verra la notification dans Django Admin sous "Historique des actions"
        # ⚠️ Suppression de messages.info(request, ...) car pas de request dans un signal
