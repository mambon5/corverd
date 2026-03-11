from django.db import models
from django.contrib.auth.models import User

class Associacio(models.Model):
    nom = models.CharField(max_length=255)
    descripcio = models.TextField()
    any_fundacio = models.IntegerField(null=True, blank=True)
    zona_geografica = models.CharField(max_length=255, null=True, blank=True)
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='associacions_administrades')

    def __str__(self):
        return self.nom

class Activitat(models.Model):
    titol = models.CharField(max_length=255)
    descripcio = models.TextField()
    data = models.DateTimeField()
    associacio = models.ForeignKey(Associacio, on_delete=models.CASCADE, related_name='activitats')

    def __str__(self):
        return self.titol

class Noticia(models.Model):
    titol = models.CharField(max_length=255)
    contingut = models.TextField()
    data_publicacio = models.DateTimeField(auto_now_add=True)
    associacio = models.ForeignKey(Associacio, on_delete=models.CASCADE, related_name='noticies')

    def __str__(self):
        return self.titol

class Comentari(models.Model):
    text = models.TextField()
    data = models.DateTimeField(auto_now_add=True)
    usuari = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comentaris')
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE, related_name='comentaris')

    def __str__(self):
        return f"Comentari de {self.usuari.username} a {self.noticia.titol}"
