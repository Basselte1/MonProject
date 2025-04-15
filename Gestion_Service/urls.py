
from django.urls import path


from Gestion_Service.views import service_comptabilite, service_gl, devis_form, dashboard, refresh_dashboard, \
    generate_devis_pdf, voir_devis, telecharger_facture, facture_pdf_view, voir_demandes_par_statut, modifier_demande, \
    supprimer_demande, voir_facture, valider_devis

urlpatterns = [

    path('service_comptabilite/', service_comptabilite, name='service_comptabilite'),
    path('service_gl/', service_gl, name='service_gl'),

    path('devis_form/', devis_form, name='devis_form'),

    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/refresh/', refresh_dashboard, name='refresh_dashboard'),

    path('demandes/<str:statut>/', voir_demandes_par_statut, name='voir_demandes_par_statut'),
    path('demandes/modifier/<int:demande_id>/', modifier_demande, name='modifier_demande'),
    path('demandes/supprimer/<int:demande_id>/', supprimer_demande, name='supprimer_demande'),

    path('devis/generer/<int:demande_id>/', generate_devis_pdf, name='generate_devis_pdf'),

    path('devis/<str:statut>/', voir_devis, name='voir_devis'),
    path('valider-devis/<int:devis_id>/', valider_devis, name='valider_devis'),

    path('facture/pdf/<int:facture_id>/', facture_pdf_view, name='facture_pdf'),
    path('facture/<str:statut>/', voir_facture, name='voir_facture'),
    path('facture/<int:facture_id>/download/', telecharger_facture, name='telecharger_facture'),

    #path('map/', carte_vue, name='map'),


]
