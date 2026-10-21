from core.models import Associacio
from django.db.models import Count

# 1. Agrupem per nom per identificar quins noms tenen duplicats
noms_duplicats = (
    Associacio.objects.values('nom')
    .annotate(total=Count('id'))
    .filter(total__gt=1)
    .values_list('nom', flat=True)
)

for nom in noms_duplicats:
    # Obtenim totes les associacions amb aquest nom, ordenades per ID (o data)
    associacions = Associacio.objects.filter(nom=nom).order_by('id')
    
    # Suposem que volem conservar la primera (la més antiga) i avaluar la resta
    original = associacions.first()
    duplicades = associacions.exclude(id=original.id)
    
    for dup in duplicades:
        # Comprovem si té gerents assignats (la relació ManyToMany 'gerents')
         te_gerents = dup.gerents.exists()
         
         # Opcionalment, pots comprovar també si té activitats, adhesions, etc., si ho creus necessari.
         
         if not te_gerents:
             print(f"Esborrant associació duplicada sense gerents: {dup.nom} (ID: {dup.id})")
             dup.delete()
         else:
             print(f"S'omet {dup.nom} (ID: {dup.id}) perquè té gerents assignats.")

exit()