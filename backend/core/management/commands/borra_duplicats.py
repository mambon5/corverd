from django.core.management.base import BaseCommand
from core.models import Associacio
from django.db.models import Count

class Command(BaseCommand):
    help = "Esborra associacions duplicades que no tenen gerents assignats"

    def handle(self, *args, **options):
        self.stdout.write("Buscant associacions duplicades...")
        
        noms_duplicats = (
            Associacio.objects.values('nom')
            .annotate(total=Count('id'))
            .filter(total__gt=1)
            .values_list('nom', flat=True)
        )

        if not noms_duplicats:
            self.stdout.write(self.style.SUCCESS("No s'ha trobat cap nom duplicat a la base de dades."))
            return

        eliminats_count = 0

        for nom in noms_duplicats:
            associacions = Associacio.objects.filter(nom=nom).order_by('id')
            original = associacions.first()
            duplicades = associacions.exclude(id=original.id)
            
            for dup in duplicades:
                te_gerents = dup.gerents.exists()
                
                if not te_gerents:
                    self.stdout.write(f"-> Esborrant duplicat sense gerents: '{dup.nom}' (ID: {dup.id})")
                    dup.delete()
                    eliminats_count += 1
                else:
                    self.stdout.write(f"-> Ometent '{dup.nom}' (ID: {dup.id}) perquè té gerents assignats.")

        self.stdout.write(self.style.SUCCESS(f"\nProcés finalitzat. S'han eliminat {eliminats_count} registres duplicats."))