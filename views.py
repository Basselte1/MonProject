import os

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail, EmailMessage
from django.shortcuts import redirect, get_object_or_404

from Gestion_Service.models import Service
from django.contrib.auth.decorators import login_required


# Create your views here.


def service_comptabilite(request):
    # Ici, tu peux récupérer les informations spécifiques du client (comme entreprise).

    return render(request, 'services/service_comptabilite.html')

def service_gl(request):

    services = Service.objects.all()

    return render(request, 'services/service_gl.html',{'services':services})

###############################################################################################################

def devis_form(request):
    # Récupérer tous les services disponibles pour le formulaire
    services = Service.objects.all()
   # show_modal = False  # Par défaut, ne pas afficher la modale

    # Si la méthode HTTP est POST, cela signifie que le formulaire a été soumis
    if request.method == "POST":
        # Récupérer les données soumises par l'utilisateur
        description = request.POST.get("details")
        service_id = request.POST.get("service")
        fichier = request.FILES.get("fichier")
        nom=request.POST.get("username")
        email=request.POST.get("email")
        adresse=request.POST.get("adresse")


        # Construction du message pour l'email
        message_admin = f"""
               📌 Nouvelle demande de devis :

               Client : {nom}
               Email : {email}
               Service demandé : {service_id}
               adresse: {adresse}  
               Description : {description}
               Fichier joint : {fichier.name if fichier else 'Aucun fichier'}"""

        try:
            send_mail(
                subject="🛠 Nouvelle demande ",
                message=message_admin,
                from_email=email,
                recipient_list=[settings.ADMIN_EMAIL],  # Remplace par l'email de l'admin
                fail_silently=False,
            )
            #messages.success(request, "Votre demande a bien été envoyée ! L'administrateur va vous contacter.")
        except Exception as e:
            messages.error(request, f"Erreur lors de l'envoi de l'email : {e}")

            ##############################################################################
        # Vérification de la validité du service
        try:
            service = Service.objects.get(id=int(service_id))
        except (ValueError, Service.DoesNotExist):
            messages.error(request, "Service invalide.")
            return render(request, "devis.html", {"services": services})


        # Si l'utilisateur n'est pas connecté, stocker la demande en session (request. session).
        if not request.user.is_authenticated:
            request.session['demandeservice_temp'] = {
                'description': description,
                'service_id': service_id,
                'fichier': fichier.name if fichier else None  # Stocke seulement le nom du fichier
            }

            show_modal = True  # Activer la fenêtre modale
            # Afficher un message et rediriger l'utilisateur pour qu'il se connecte ou s'inscrive
            messages.info(request, "Votre demande est en cour de traitement .")


            return render(request, "devis.html", {"show_modal": show_modal, "services": services})  # Afficher une fenêtre modale

        # Si l'utilisateur est connecté, traiter normalement la demande
        else:
            # Récupérer les données soumises par l'utilisateur depuis le formulaire
            description = request.POST.get("details")
            service_id = request.POST.get("service")
            fichier= request.FILES.get("fichier")

            print("Service ID reçu :", service_id)  # Débogage : afficher l'ID du service
            print("fichier envoyer:",fichier)

            # Vérification que l'ID du service est valide
            try:
                service = Service.objects.get(id=int(service_id))  # Récupérer l'objet Service correspondant à l'ID
            except (ValueError, Service.DoesNotExist):  # Si l'ID n'est pas valide ou si le service n'existe pas
                messages.error(request, "Service invalide.")
                return render(request, "devis.html", {"services": services})  # Réafficher le formulaire

            # Créer la demande de service (DemandeService) dans la base de données
            demandeservice_temp = DemandeService.objects.create(
                description=description,
                service=service,
                fichier=fichier,  # stockage du fichier
                client=request.user,  # Associe la demande à l'utilisateur (client) qui l'a soumise
                statut='EN_ATTENTE'  # La demande est initialement en attente
            )

            # Vérifier si l'utilisateur est un administrateur ou un client
            if request.user.is_staff:  # Si l'utilisateur est un administrateur
                messages.info(request, "Une nouvelle demande a été soumise par un client.")
                return redirect('/admin/Gestion_Service/demandeservice/')

            # Rediriger l'admin vers son espace d'administration

            else:  # Si l'utilisateur est un client

                messages.success(request, "Votre demande de service a été envoyée avec succès !nous vous contacterons dans des brefs delais")
                return redirect("client_dashbord")

                # Si la méthode HTTP n'est pas POST (c'est-à-dire que la page est juste visitée ou que le formulaire a échoué).
    return render(request, "devis.html", {"services": services})

####################################################################################3
# suivre en temps les services demandees
#  fonction pour recuperer les informations du client connecte

from django.shortcuts import render
from .models import Facture, Devis, DemandeService
from datetime import datetime

@login_required
def dashboard(request):
    user = request.user
# Comptabilise les demandes de service selon leur statut (EN_ATTENTE, VALIDEE, REFUSEE).

    # Récupérer les demandes de l'utilisateur
    demandes_attente = DemandeService.objects.filter(client=user, statut='EN_ATTENTE').count()
    demandes_validees = DemandeService.objects.filter(client=user, statut='VALIDÉE').count()
    demandes_refusees = DemandeService.objects.filter(client=user, statut='REFUSÉE').count()


    #On récupère les Devis en filtrant via demande__client=user.
    devis_attente = Devis.objects.filter(demande__client=user, statut='EN_ATTENTE').count()
    devis_valides = Devis.objects.filter(demande__client=user, statut='VALIDÉ').count()
    devis_refuses = Devis.objects.filter(demande__client=user, statut='REFUSÉ').count()


    # Récupérer les factures de l'utilisateur
    factures_attente = Facture.objects.filter(devis__demande__client=user, statut='EN_ATTENTE').count()
    factures_impayees = Facture.objects.filter(devis__demande__client=user, statut='IMPAYEE').count()
    factures_payees = Facture.objects.filter(devis__demande__client=user, statut='PAYEE').count()


    context = {
        'demandes_attente': demandes_attente,
        'demandes_validees': demandes_validees,
        'demandes_refusees': demandes_refusees,

        'devis_attente': devis_attente,
        'devis_valides': devis_valides,
        'devis_refuses': devis_refuses,

        'factures_attente': factures_attente,
        'factures_impayees': factures_impayees,
        'factures_payees': factures_payees,

    }


    return render(request, 'users/clients.html', context)

####################################################################################
# vue Django pour fournir des statistiques sur les demandes de service et les factures de l'utilisateur connecté.

from django.http import JsonResponse, FileResponse  # classe permet de renvoyer une réponse HTTP au format JSON

#JSON (JavaScript Object Notation) est un format de données
# qui permet d'échanger des informations entre une application et un serveur.


@login_required
def refresh_dashboard(request):
    #récupèration de l'utilisateur actuellement connecté à partir de l'objet request
    user = request.user

#dictionnaire Python qui contient différentes statistiques basées sur les demandes de service et les factures de l'utilisateur connecté.
    data = {
        "demandes_en_attente": DemandeService.objects.filter(client=user, statut='EN_ATTENTE').count(),
        "demandes_validees" : DemandeService.objects.filter(client=user, statut='VALIDÉE').count(),
        "demandes_refusees": DemandeService.objects.filter(client=user, statut='REFUSÉE').count(),

        "devis_attente": Devis.objects.filter(demande__client=user, statut='EN_ATTENTE').count(),
        "devis_valides": Devis.objects.filter(demande__client=user, statut='VALIDÉ').count(),
        "devis_refuses": Devis.objects.filter(demande__client=user, statut='REFUSÉ').count(),

        "factures_attente": Facture.objects.filter(devis__demande__client=user, statut='EN_ATTENTE').count(),
        "factures_impayees": Facture.objects.filter(devis__demande__client=user, statut='IMPAYEE').count(),
        "factures_payees": Facture.objects.filter(devis__demande__client=user, statut='PAYEE').count(),

    }
#renvoie le dictionnaire data au format JSON
    return JsonResponse(data) # JsonResponse(), fonction Django qui permet d'envoyer une réponse JSON à une requête.

###############################################################
#vues pour les demandes
from django.core.files.storage import default_storage

@login_required
def voir_demandes_par_statut(request, statut):
    """Affiche la liste des demandes du client selon leur statut"""
    # Vérification du mapping des statuts

    demandes = DemandeService.objects.filter(client=request.user, statut=statut)

    print(f"Demandes avec statut {statut} :", list(demandes))

    return render(request, 'demandes/liste_demandes.html', {'demandes': demandes, 'statut': statut})

@login_required
def modifier_demande(request, demande_id):

    """Permet au client de modifier sa demande et de la remettre en attente"""
    demande = get_object_or_404(DemandeService, id=demande_id, client=request.user)

    if request.method == "POST":
        description = request.POST.get("details")
        service_id = request.POST.get("service")
        fichier = request.FILES.get("fichier")

        # Vérifier si le service existe
        try:
            service = Service.objects.get(id=int(service_id))
        except (ValueError, Service.DoesNotExist):
            messages.error(request, "Service invalide.")
            return redirect('modifier_demande', demande_id=demande.id)

        # Mise à jour des données
        demande.description = description
        demande.service = service
        demande.statut = "EN_ATTENTE"  # Revenir en attente après modification

        if fichier:
            if demande.fichier:
                default_storage.delete(demande.fichier.path)  # Supprime l'ancien fichier
            demande.fichier = fichier  # Ajoute le nouveau fichier

        demande.save()

        messages.success(request, "Votre demande a été modifiée et renvoyée avec succès.")
        return redirect('voir_demandes_par_statut', statut="EN_ATTENTE")

    services = Service.objects.all()
    return render(request, 'demandes/modifier_demande.html', {'demande': demande, 'services': services})

@login_required
def supprimer_demande(request, demande_id):

    """Supprime une demande validée ou refusée"""
    demande = get_object_or_404(DemandeService, id=demande_id, client=request.user)

    if demande.statut in ["VALIDÉE", "REFUSÉE"]:
        if demande.fichier:
            default_storage.delete(demande.fichier.path)  # Supprime le fichier associé
        demande.delete()
        messages.success(request, "Votre demande a été supprimée.")
    else:
        messages.error(request, "Vous ne pouvez pas supprimer une demande en attente.")

    return redirect('voir_demandes_par_statut', statut=demande.statut)

#######################################################################
#vue Django qui génère un devis en PDF pour une demande de service spécifique, 
# le stocke dans la base de données, et renvoie un lien pour le télécharger.

from django.http import HttpResponse
from django.core.files.base import ContentFile
from weasyprint import HTML
from django.conf import settings


@login_required
def generate_devis_pdf(request, demande_id):  #http://127.0.0.1:8000/devis/generer/20/ id du devis dans la BD/
    """
    Génère un devis en PDF, le stocke dans la base de données et retourne un lien de téléchargement.
    """

    # 🔹 1. Vérifier si un devis existe déjà pour cette demande et récupérer la demande de service correspondant à l'ID (demande_id).
    try:
        # Récupérer la demande
        demande = get_object_or_404(DemandeService, id=demande_id)
    except DemandeService.DoesNotExist:
        return HttpResponse("Demande de service non trouvée", status=404)

    # Vérifier si la demande est liée à un utilisateur (client)
    if not demande.client:
        return HttpResponse("Erreur : cette demande n'a pas de client associé.", status=404)


    # Affichage des informations de la demande et de l'utilisateur pour déboguer
    print(demande.client)
    print("Demande Service ID:", demande.id)
    print("Client associé : ", demande.client.username)


    # Vérifie si un devis existe déjà
    devis = Devis.objects.filter(demande=demande).first()

    # Si un devis existe déjà et qu'il a déjà un fichier PDF associé, on renvoie un lien pour télécharger ce fichier.
    if not devis and devis.fichier:
        return HttpResponse(f"Devis déjà existant ! <a href='{devis.fichier.url}' target='_blank'>Télécharger</a>")

    # récupérer un devis existant pour cette demande. S'il n'existe pas, on en crée un nouveau.
    # "created" = booléen qui indique si le devis a été créé (True) ou s'il existait déjà (False).
    if not devis:
        devis = Devis.objects.get_or_create(demande=demande)

    #2.dictionnaire context qui contient toutes les informations nécessaires pour générer le devis (nom du client, email, entreprise, etc.).

    # 🔹 3. Préparer les données du contexte
    client = demande.client

    context = {
        # Informations du client
        "client_nom": client.username,
        "client_email": client.email,
        "client_entreprise": client.first_name,  # Si c'est le nom de l'entreprise

        # Informations du devis
        "devis": devis,
        "validite": devis.validite,
        "description": devis.description,
        "duree": devis.duree,

        # Coûts détaillés
        "cout_backend": devis.cout_backend,
        "cout_frontend": devis.cout_frontend,
        "cout_test": devis.cout_test,
        "cout_maintenance": devis.cout_maintenance,
        "cout_hebergement": devis.cout_hebergement if devis.cout_hebergement else 0,
        "cout_nom_de_domaine": devis.cout_nom_de_domaine if devis.cout_nom_de_domaine else 0,

        # Totaux
        "total_ht": devis.calcul_total_ht,
        "tva": devis.calcul_tva,
        "total_ttc": devis.calcul_total_ttc,
    }

    # 🔹 3. générer le contenu HTML du devis en utilisant le contexte défini précédemment.

    html_content = render(request, 'devis/devis_template.html', context).content.decode()

    # 🔹 4. convertit le contenu HTML en fichier PDF en utilisant une bibliothèque comme WeasyPrint
    pdf_file = HTML(string=html_content).write_pdf()

#################### Enregistrement du fichier PDF

    # 🔹 5. Définir le chemin et enregistrer le fichier
    devis_filename = f"devis_{demande.id}.pdf"

    # Si un fichier PDF existait déjà pour ce devis, on le supprime avant d'enregistrer le nouveau.
    if devis.fichier:
        devis.fichier.delete(save=False)

    # Cela supprime le fichier précédent, et enregistrer la modification dans la base de données

    # 🔹 6. On enregistre le fichier PDF dans le champ fichier du modèle Devis.
    devis.fichier.save(devis_filename, ContentFile(pdf_file), save=True)

    # 🔹 7. renvoie une réponse HTTP avec un lien pour télécharger le fichier PDF.
    pdf_url = devis.fichier.url  # Django construit automatiquement le bon chemin

    print("Fichier enregistré:", devis.fichier.path)  # Chemin sur le disque
    print("URL du fichier:", devis.fichier.url)  # URL publique

    # envoyer email à l'utilisateur correspondant

    if devis.demande:
        service_nom = devis.demande.service.nom
    else:
        service_nom = "service inconnu"
    try:
        send_mail(
            subject='devis envoye',
            message=f"""Votre devis pour un {service_nom} a ete envoyer.
            Vous pouvez le telechage en cliquant sur ce lien :  {request.build_absolute_uri(devis.fichier.url)}
            ou Veuillez vous connectez pour le voir.
                    Merci de votre confiance ! """,
            from_email=settings.ADMIN_EMAIL,
            recipient_list=[demande.client.email],
            fail_silently=False,
        )

        print(f"Email envoyé à {demande.client.email}")
        print(f"Email envoyé à {demande.client.email}")

    except Exception as e:
        print("Erreur lors de l'envoi d'email :", e)

    return HttpResponse(f"Devis généré avec succès ! <a href='{pdf_url}' target='_blank'>Télécharger le PDF</a>")


######################################################
# methode pour supprimer l'ancien fichier lorsqu'un devis est supprime.

def delete(self, *args, **kwargs):
    if self.fichier and os.path.exists(self.fichier.path):
        os.remove(self.fichier.path)
    super().delete(*args, **kwargs)

###################################################3
# vue Django qui permet à un utilisateur connecté de voir la liste des devis associés à son compte,
#  en fonction d'un statut spécifique (par exemple, "EN_ATTENTE", "VALIDÉ", ou "REFUSÉ").

@login_required
def voir_devis(request, statut):  
    """
    Affiche les devis de l'utilisateur en fonction de leur statut (EN_ATTENTE, VALIDÉ, REFUSÉ)
    """
    user = request.user
    
    #Filtrage des devis par utilisateur et statut
    #On utilise le modèle Devis pour récupérer tous les devis qui correspondent à deux critères (le client associe a la demande et le statut)
    devis_list = Devis.objects.filter(demande__client=user, statut=statut,)

    #fonction "render" pour afficher un template HTML (devis/voir_devis.html) en lui passant un contexte (un dictionnaire de données).

    return render(request, 'devis/voir_devis.html', {'devis_list': devis_list, 'statut': statut,
                                                     'message': "Aucun devis trouvé avec ce statut." if not devis_list else "",})


#############################################################
#valider le devis

@login_required
def valider_devis(request, devis_id):
    """
    Permet au client de valider son devis
    """
    devis = get_object_or_404(Devis, id=devis_id)

    # Vérifier que le devis appartient à l'utilisateur connecté (le client)
    if devis.demande.client != request.user:
        messages.success(request, "Votre demande a echouée !")
        return redirect('client_dashbord')  # Rediriger si ce n'est pas le bon client

    # Mettre à jour le statut du devis à "validé"
    devis.statut = 'VALIDÉ'  # Assurer que le statut 'VALIDÉ' existe dans ton modèle
    devis.save()

    # Envoyer un email à l'administrateur pour l'informer que le devis a été validé
    subject = "Un devis a été validé"
    message = f"""
        Bonjour Admin,

        Le client {devis.demande.client.username} a validé un devis.

        Détails du devis :
        - ID : {devis.id}
        - Service : {devis.demande.service.nom}
        - Montant : {devis.calcul_total_ttc()} €
        Veuillez consulter le tableau de bord pour plus d'informations.
        """
    send_mail(subject, message, {devis.demande.client.email}, [settings.ADMIN_EMAIL])

    messages.success(request,'votre devis a ete valide avec success. ')
    return redirect('client_dashbord')  # Rediriger après validation


###############################3###########################
#GENERER LA FACTURE
@login_required
def facture_pdf_view(request, facture_id):
    """Affiche une facture existante et envoie un email si elle est validée."""
    try:
        # Récupérer la facture
        facture = get_object_or_404(Facture, pk=facture_id)

        # Générer le PDF si nécessaire
        if not facture.fichier_pdf or not os.path.exists(facture.fichier_pdf.path):
            if not facture.generate_pdf():
                return HttpResponse("Erreur lors de la génération du PDF.", status=500)

        # Ouvrir le fichier PDF
        with open(facture.fichier_pdf.path, 'rb') as pdf_file:
            pdf_content = pdf_file.read()

        # Vérifier si la facture est validée et envoyer un email
        if facture.devis and facture.devis.statut == 'VALIDÉ':
            client = facture.get_client()
            service = facture.get_service()

            client_email = client.email if client else None
            service_nom = service.nom if service else "Service inconnu"

            if client_email:  # Vérification si l'email existe
                try:
                    email = EmailMessage(
                        subject="Votre facture est disponible",
                        body=f"Bonjour {client.username},\n\n"
                             f"Votre devis pour le service '{service_nom}' a été validé.\n"
                             f"Votre facture est maintenant disponible dans votre espace client.\n\n"
                             f"Cordialement,\nL'équipe de gestion.",
                        from_email=settings.ADMIN_EMAIL,
                        to=[client_email],
                    )
                    email.attach(
                        filename=f"{facture.numero_facture or facture.pk}.pdf",
                        content=pdf_content,
                        mimetype="application/pdf"
                    )
                    email.send(fail_silently=False)
                    print(f"✅ Email avec facture envoyé à {client_email}")
                except Exception as e:
                    print(f"❌ Erreur lors de l'envoi de l'email : {e}")

        # Retourner le PDF
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{facture.numero_facture or facture.pk}.pdf"'
        return response

    except ObjectDoesNotExist:
        return HttpResponse("Facture introuvable.", status=404)

    except Exception as e:
        print(f"❌ Erreur générale : {e}")
        return HttpResponse("Erreur interne du serveur.", status=500)

#############################################################
# telechargement  de la facture

@login_required
def telecharger_facture(request, facture_id):
    """Permet au client de télécharger une facture en PDF."""
    facture = get_object_or_404(Facture, pk=facture_id)

    # Vérifier si la facture appartient bien au client connecté
    if facture.devis and facture.devis.demande.client != request.user:
        return HttpResponse("Accès refusé : cette facture ne vous appartient pas.", status=403)

    # Vérifier si le fichier PDF existe
    if not facture.fichier_pdf or not os.path.exists(facture.fichier_pdf.path):
        return HttpResponse("Facture non disponible", status=404)

    # Ouvrir et retourner le fichier PDF en téléchargement
    try:
        response = FileResponse(facture.fichier_pdf.open('rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{facture.numero_facture or facture.pk}.pdf"'
        return response
    except Exception as e:
        print(f"❌ Erreur lors de l'ouverture du fichier PDF : {e}")
        return HttpResponse("Erreur lors du téléchargement de la facture.", status=500)

################################################################################################3
# permettre a l'utilisateur de voir la facture

@login_required
def voir_facture(request, statut):
    """
    Affiche les devis de l'utilisateur en fonction de leur statut (EN_ATTENTE, VALIDÉ, REFUSÉ)
    """
    user = request.user

    # Filtrage des devis par utilisateur et statut
    # On utilise le modèle Devis pour récupérer tous les devis qui correspondent à deux critères (le client associe a la demande et le statut)
    facture_list = Facture.objects.filter(devis__demande__client=user, statut=statut )

    for facture in facture_list:
        print(f"🔍 Facture {facture.numero_facture} - Fichier PDF : {facture.fichier_pdf}")  # Debug

    # fonction "render" pour afficher un template HTML (devis/voir_devis.html) en lui passant un contexte (un dictionnaire de données).

    return render(request, 'factures/liste_facture.html', {'facture_list': facture_list, 'statut': statut})

