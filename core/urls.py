from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('entitats/', views.entitats_list, name='entitats_list'),
    path('noticia/<int:pk>/', views.noticia_detail, name='noticia_detail'),
]
