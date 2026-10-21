from django.core.management.base import BaseCommand
from core.models import Associacio

class Command(BaseCommand):
    help = "Llista totes les associacions per detectar duplicats"

    def handle(self, *args, **options):
        self.stdout.write("--- LLISTAT DE TOTES LES ASSOCIACIONS A LA BD ---")
        
        associacions = Associacio.objects.all().order_by('id')
        
        if not associacions.exists():
            self.stdout.write("La taula core_associacio està totalment buida.")
            return

        for ass in associacions:
            num_gerents = ass.gerents.count()
            self.stdout.write(f"ID: {ass.id} | Nom: '{ass.nom}' | Gerents: {num_gerents}")

        self.stdout.write(f"\nTotal d'associacions trobades: {associacions.count()}")