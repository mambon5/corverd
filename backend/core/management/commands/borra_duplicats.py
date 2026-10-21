import difflib
from django.core.management.base import BaseCommand
from core.models import Associacio

class Command(BaseCommand):
    help = "Esborra associacions duplicades similars que no tenen gerents assignats"

    def similarity(self, a, b):
        """Retorna un valor entre 0 i 1 de semblança entre dues cadenes de text."""
        return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def handle(self, *args, **options):
        self.stdout.write("Buscant associacions amb noms similars o duplicats...")
        
        associacions = list(Associacio.objects.all().order_by('id'))
        eliminats_count = 0
        esborrats_ids = set()

        for i in range(len(associacions)):
            a1 = associacions[i]
            if a1.id in esborrats_ids:
                continue

            for j in range(i + 1, len(associacions)):
                a2 = associacions[j]
                if a2.id in esborrats_ids:
                    continue

                # Càlcul de similitud
                score = self.similarity(a1.nom, a2.nom)
                
                # També comprovem si un nom conté l'altre (ex: "Satalia..." i "La Satalia...")
                nom1_clean = a1.nom.lower().replace("la ", "").replace("l'", "").replace("associació ", "").replace("assiciació ", "")
                nom2_clean = a2.nom.lower().replace("la ", "").replace("l'", "").replace("associació ", "").replace("assiciació ", "")
                
                són_similars = score > 0.80 or (len(nom1_clean) > 5 and nom1_clean in nom2_clean) or (len(nom2_clean) > 5 and nom2_clean in nom1_clean)

                if són_similars:
                    self.stdout.write(f"\n[DETECTAT DUPLICAT] ({score*100:.0f}% semblança):")
                    self.stdout.write(f"  - ID {a1.id}: '{a1.nom}' (Gerents: {a1.gerents.count()})")
                    self.stdout.write(f"  - ID {a2.id}: '{a2.nom}' (Gerents: {a2.gerents.count()})")

                    # Decidim quin esborrar:
                    # Preferim mantenir el que TÉ gerents. Si cap dels dos en té, mantenim el primer (ID menor).
                    g1 = a1.gerents.exists()
                    g2 = a2.gerents.exists()

                    target_to_delete = None

                    if g1 and not g2:
                        target_to_delete = a2
                    elif g2 and not g1:
                        target_to_delete = a1
                    elif not g1 and not g2:
                        target_to_delete = a2  # Esborrem el segon (ID més alt)
                    else:
                        self.stdout.write(self.style.WARNING("  -> Tots dos tenen gerents assignats! No s'esborra cap per seguretat."))
                        continue

                    self.stdout.write(self.style.SUCCESS(f"  -> Esborrant ID {target_to_delete.id}: '{target_to_delete.nom}'"))
                    esborrats_ids.add(target_to_delete.id)
                    target_to_delete.delete()
                    eliminats_count += 1

        self.stdout.write(self.style.SUCCESS(f"\nProcés finalitzat. S'han eliminat {eliminats_count} registres duplicats/erronis."))