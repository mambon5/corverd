from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('entitats/', views.entitats_list, name='entitats_list'),
    path('entitat/<int:pk>/activitats/', views.entitat_activitats, name='entitat_activitats'),
    path('activitats/', views.activitats_calendar, name='activitats_calendar'),
    path('noticia/<int:pk>/', views.noticia_detail, name='noticia_detail'),
    path('manifest/', views.manifest, name='manifest'),
    path('sobre/', views.sobre, name='sobre'),
    path('testimonis/', views.testimonis, name='testimonis'),
    path('faq/', views.faq, name='faq'),
    path('recursos/', views.recursos, name='recursos'),
    path('serveis/', views.serveis, name='serveis'),
    path('blog/', views.blog, name='blog'),
    path('contacte/', views.contacte, name='contacte'),
]
