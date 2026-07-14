from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('entitats/', views.entitats_list, name='entitats_list'),
    path('entitats/adherides/', views.entitats_adherides_view, name='entitats_adherides'),
    path('entitat/<int:pk>/activitats/', views.entitat_activitats, name='entitat_activitats'),
    path('activitats/', views.activitats_calendar, name='activitats_calendar'),
    path('mapa-entitats/', views.mapa_entitats_view, name='mapa_entitats'),
    path('noticia/<int:pk>/', views.noticia_detail, name='noticia_detail'),
    path('manifest/', views.manifest, name='manifest'),
    path('adhesio/', views.adhesio_manifest_view, name='adhesio'),
    path('sobre/', views.sobre, name='sobre'),
    path('sobre/historia/', views.historia_view, name='historia'),
    path('sobre/presentacio/', views.presentacio_view, name='presentacio'),
    path('sobre/organitzacio/', views.organitzacio_view, name='organitzacio'),
    path('testimonis/', views.testimonis, name='testimonis'),
    path('faq/', views.faq, name='faq'),
    path('recursos/', views.recursos, name='recursos'),
    path('serveis/', views.serveis, name='serveis'),
    path('blog/', views.blog, name='blog'),
    path('contacte/', views.contacte, name='contacte'),
    path('proteccio-dades/', views.proteccio_dades, name='proteccio_dades'),
    path('intranet/', views.intranet_dashboard, name='intranet_dashboard'),
    path('intranet/entitat/<int:pk>/editar/', views.editar_entitat, name='editar_entitat'),
    path('intranet/activitat/nova/', views.crear_activitat, name='crear_activitat'),
    path('intranet/activitat/<int:pk>/editar/', views.editar_activitat, name='editar_activitat'),
    path('intranet/activitat/<int:pk>/esborrar/', views.esborrar_activitat, name='esborrar_activitat'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('control/', views.control_dashboard, name='control_dashboard'),
]
