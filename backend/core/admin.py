from django.contrib import admin
from .models import Associacio, Activitat, Noticia, Comentari

class BaseEntityAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(associacio__gerent=request.user)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser and db_field.name == "associacio":
            kwargs["queryset"] = Associacio.objects.filter(gerent=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Associacio)
class AssociacioAdmin(admin.ModelAdmin):
    list_display = ('nom', 'any_fundacio', 'zona_geografica', 'gerent')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(gerent=request.user)

@admin.register(Activitat)
class ActivitatAdmin(BaseEntityAdmin):
    list_display = ('titol', 'data', 'associacio')

@admin.register(Noticia)
class NoticiaAdmin(BaseEntityAdmin):
    list_display = ('titol', 'data_publicacio', 'associacio')

@admin.register(Comentari)
class ComentariAdmin(admin.ModelAdmin):
    list_display = ('usuari', 'noticia', 'data')
