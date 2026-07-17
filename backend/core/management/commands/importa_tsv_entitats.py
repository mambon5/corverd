# backend/core/management/commands/import_tsv_entities.py
import csv
import os
from django.core.management.base import BaseCommand
from core.models import Associacio

class Command(BaseCommand):
    help = "Importa entitats des d'un fitxer TSV (delimitat per tabuladors)"

    def add_arguments(self, parser):
        parser.add_argument('tsv_file', type=str, help='Ruta del fitxer .tsv descarregat')

    def handle(self, *args, **options):
        tsv_path = options['tsv_file']

        if not os.path.exists(tsv_path):
            self.stderr.write(self.style.ERROR(f"El fitxer {tsv_path} no existeix."))
            return

        self.stdout.write(f"Processant el fitxer TSV: {tsv_path}...")

        with open(tsv_path, mode='r', encoding='utf-8') as file:
            # Forcem el delimitador per tabulador (\t) propi del TSV
            reader = csv.reader(file, delimiter='\t')
            
            # Saltem la capçalera
            try:
                headers = next(reader)
            except StopIteration:
                self.stderr.write("El fitxer està buit.")
                return

            created_count = 0
            updated_count = 0

            for i, row in enumerate(reader, start=2):
                # Si la línia està buida, la saltem
                if not row or len(row) < 15:
                    continue

                # Mapatge directe i neteja d'espais per índex segons la teva estructura:
                nom_entitat = row[1].strip()      # Columna 1
                nom_popular = row[2].strip()      # Nom popular de la vostra entitat/col·lectiu
                zona_geo = row[5].strip()         # Àmbit geogràfic d'actuació
                email = row[6].strip()            # Correu electrònic
                url_web = row[7].strip()          # Adreça web
                adreça_postal = row[11].strip()   # Adreça postal
                any_fund = row[24].strip()        # Columna 24 (Any de fundació flexible)

                # Saltem capçaleres accidentals o files sense nom d'entitat
                if not nom_entitat or nom_entitat == "Columna 1":
                    continue

                # Normalització ràpida de la web (Evitem els links de Drive si s'han equivocat de columna)
                if "drive.google.com" in url_web:
                    url_web = ""
                elif url_web and url_web.startswith("www."):
                    url_web = f"https://{url_web}"

                # Generem una descripció dinàmica combinant dades si no tenim un camp de descripció llarga
                desc_text = f"Entitat adherida a la Coordinadora Verda."
                if zona_geo:
                    desc_text += f" El seu àmbit d'actuació principal es troba a: {zona_geo}."

                # Inserció o actualització automàtica
                associacio, created = Associacio.objects.update_or_create(
                    nom=nom_entitat,
                    defaults={
                        'descripcio_curta': nom_popular[:150],
                        'descripcio': desc_text,
                        'zona_geografica': zona_geo if zona_geo else "Catalunya",
                        'correu': email if email else None,
                        'web': url_web if url_web else None,
                        'adreça': adreça_postal if adreça_postal else None,
                        'any_fundacio': any_fund if any_fund else None,
                    }
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            self.stdout.write(self.style.SUCCESS(
                f"Sincronització TSV completada -> Creades: {created_count} | Actualitzades: {updated_count}"
            ))