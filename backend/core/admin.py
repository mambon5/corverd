from django.contrib import admin
from .models import Associacio, Activitat, Noticia, Comentari

class BaseEntityAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Canviat associacio__gerent per associacio__gerents
        return qs.filter(associacio__gerents=request.user).distinct()
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser and db_field.name == "associacio":
            # Canviat gerent per gerents
            kwargs["queryset"] = Associacio.objects.filter(gerents=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Associacio)
class AssociacioAdmin(admin.ModelAdmin):
    # Substituïm 'gerent' per la funció custom 'mostrar_gerents'
    list_display = ('nom', 'any_fundacio', 'zona_geografica', 'mostrar_gerents')
    
    # Interfície molt més còmoda a l'admin per seleccionar usuaris gerents
    filter_horizontal = ('gerents',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Canviat gerent per gerents
        return qs.filter(gerents=request.user).distinct()

    @admin.display(description='Gerents')
    def mostrar_gerents(self, obj):
        # Retorna els noms d'usuari dels gerents separats per comes
        return ", ".join([g.username for g in obj.gerents.all()]) or "Sense gerents"

@admin.register(Activitat)
class ActivitatAdmin(BaseEntityAdmin):
    list_display = ('titol', 'data', 'associacio')

@admin.register(Noticia)
class NoticiaAdmin(BaseEntityAdmin):
    list_display = ('titol', 'data_publicacio', 'associacio')

@admin.register(Comentari)
class ComentariAdmin(admin.ModelAdmin):
    list_display = ('usuari', 'noticia', 'data')