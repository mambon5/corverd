import difflib
from django.core.management.base import BaseCommand
from core.models import Associacio

class Command(BaseCommand):
    help = "Esborra associacions duplicades similars que no tenen gerents assignats"

    def similarity(self, a, b):
        return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def handle(self, *args, **options):
        self.stdout.write("Buscant associacions amb noms similars o duplicats...")

        # Afegim un conjunt per portar el registre dels IDs que ja hem esborrat
        esborrats_ids = set()

        # Obtenim els IDs en un ordre establert
        associacio_ids = list(Associacio.objects.values_list('id', flat=True).order_by('id'))
        eliminats_count = 0

        for i in range(len(associacio_ids)):
            id1 = associacio_ids[i]
            if id1 in esborrats_ids:
                continue

            # Carreguem l'objecte actual directament de la BD
            try:
                a1 = Associacio.objects.get(pk=id1)
            except Associacio.DoesNotExist:
                continue

            for j in range(i + 1, len(associacio_ids)):
                id2 = associacio_ids[j]
                if id2 in esborrats_ids:
                    continue

                try:
                    a2 = Associacio.objects.get(pk=id2)
                except Associacio.DoesNotExist:
                    continue

                # Càlcul de similitud
                score = self.similarity(a1.nom, a2.nom)
                
                # Normalitzem els noms treient caràcters habituals per fer una comparació neta
                clean_prefixes = ["la ", "l'", "associació ", "assiciació ", "avv de la ", "avv "]
                nom1_clean = a1.nom.lower()
                nom2_clean = a2.nom.lower()
                
                for prefix in clean_prefixes:
                    nom1_clean = nom1_clean.replace(prefix, "")
                    nom2_clean = nom2_clean.replace(prefix, "")

                # Considerem que són duplicats si superen el 82% de semblança O si la versió neta és exactament la mateixa
                són_duplicats = (score >= 0.82) or (nom1_clean.strip() == nom2_clean.strip())

                if són_duplicats:
                    self.stdout.write(f"\n[DETECTAT DUPLICAT] ({score*100:.0f}% semblança):")
                    self.stdout.write(f"  - ID {a1.id}: '{a1.nom}' (Gerents: {a1.gerents.count()})")
                    self.stdout.write(f"  - ID {a2.id}: '{a2.nom}' (Gerents: {a2.gerents.count()})")

                    # Decidim quin esborrar (mantenim el que TÉ gerents)
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

        self.stdout.write(self.style.SUCCESS(f"\nProcés finalitzat. S'han eliminat {eliminats_count} registres duplicats."))