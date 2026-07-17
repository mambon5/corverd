from django.db import models
from django.contrib.auth.models import User

class Associacio(models.Model):
    nom = models.CharField(max_length=255)
    descripcio = models.TextField()
    any_fundacio = models.CharField(max_length=100, null=True, blank=True)
    zona_geografica = models.CharField(max_length=255, null=True, blank=True)
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)
    gerent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='associacions_administrades')
    adreça = models.CharField(max_length=255, null=True, blank=True)
    web = models.CharField(max_length=255, null=True, blank=True)
    correu = models.EmailField(max_length=255, null=True, blank=True)
    foto = models.ImageField(upload_to='fotos_associacions/', null=True, blank=True)
    descripcio_curta = models.CharField(max_length=150, null=True, blank=True, help_text="Breu descripció (màyim 10 paraules)")
    
    def __str__(self):
        return self.nom

class Activitat(models.Model):
    titol = models.CharField(max_length=255)
    descripcio = models.TextField()
    data = models.DateField()
    hora = models.TimeField()
    adreça = models.CharField(max_length=255, null=True, blank=True)
    latitud = models.FloatField(null=True, blank=True)
    longitud = models.FloatField(null=True, blank=True)
    associacio = models.ForeignKey(Associacio, on_delete=models.CASCADE, related_name='activitats')
    usuari = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='activitats_organitzades')
    pdf_activitat = models.FileField(upload_to='pdfs_activitats/', null=True, blank=True, max_length=255, help_text="PDF explicatiu de l'activitat (màx 2MB)")

    def __str__(self):
        return self.titol

class Noticia(models.Model):
    titol = models.CharField(max_length=255)
    contingut = models.TextField()
    data_publicacio = models.DateTimeField(auto_now_add=True)
    associacio = models.ForeignKey(Associacio, on_delete=models.CASCADE, related_name='noticies')
    usuari = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='noticies_publicades')

    def __str__(self):
        return self.titol

class Comentari(models.Model):
    text = models.TextField()
    data = models.DateTimeField(auto_now_add=True)
    usuari = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comentaris')
    noticia = models.ForeignKey(Noticia, on_delete=models.CASCADE, related_name='comentaris')

    def __str__(self):
        return f"Comentari de {self.usuari.username} a {self.noticia.titol}"

class AdhesioEntitat(models.Model):
    nom = models.CharField(max_length=255)
    lluita_o_objectiu = models.CharField(max_length=255)
    contacte = models.EmailField(max_length=255)
    web = models.URLField(max_length=255, null=True, blank=True)
    data_adhesio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

class AdhesioPersona(models.Model):
    nom = models.CharField(max_length=100)
    cognoms = models.CharField(max_length=150)
    any_naixement = models.IntegerField()
    codi_postal = models.CharField(max_length=10)
    email = models.EmailField(max_length=255)
    professio = models.CharField(max_length=150, null=True, blank=True)
    comentari = models.TextField(null=True, blank=True)
    data_adhesio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} {self.cognoms}"
