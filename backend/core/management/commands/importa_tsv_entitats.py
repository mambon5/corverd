# backend/core/management/commands/import_tsv_entities.py
import csv
import os
import re
from django.core.management.base import BaseCommand
from core.models import Associacio

class Command(BaseCommand):
    help = "Importa entitats des d'un fitxer TSV (delimitat per tabuladors)"

    def add_arguments(self, parser):
        parser.add_argument('tsv_file', type=str, help='Ruta del fitxer .tsv descarregat')

    def clean_drive_url(self, url):
        """
        Transforma un enllaç de compartir de Google Drive en un enllaç directe
        apte per a ser renderitzat en una etiqueta <img> d'HTML.
        """
        if not url or "drive.google.com" not in url:
            return url if url else None
        
        video_id = None
        # Cas 1: open?id=ID_DE_LA_FOTO
        if "id=" in url:
            match = re.search(r'id=([^&]+)', url)
            if match:
                video_id = match.group(1)
        # Cas 2: /file/d/ID_DE_LA_FOTO/view
        elif "/file/d/" in url:
            match = re.search(r'/file/d/([^/]+)', url)
            if match:
                video_id = match.group(1)
                
        if video_id:
            return f"https://drive.google.com/uc?export=view&id={video_id}"
        
        return url

    def handle(self, *args, **options):
        tsv_path = options['tsv_file']

        if not os.path.exists(tsv_path):
            self.stderr.write(self.style.ERROR(f"El fitxer {tsv_path} no existeix."))
            return

        self.stdout.write(f"Processant el fitxer TSV: {tsv_path}...")

        with open(tsv_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='\t')
            
            try:
                headers = next(reader)
            except StopIteration:
                self.stderr.write("El fitxer està buit.")
                return

            created_count = 0
            updated_count = 0

            for i, row in enumerate(reader, start=2):
                if not row or len(row) < 15:
                    continue

                nom_entitat = row[1].strip()      # Columna 1
                nom_popular = row[2].strip()      # Nom popular
                drive_logo = row[3].strip()       # NOU: Inserteu el logo de la vostra entitat (Columna 3)
                drive_foto = row[4].strip()     # <--- AFEGEIX AIXÒ (Columna 4: Imatge de la lluita)
                zona_geo = row[5].strip()         # Àmbit geogràfic
                email = row[6].strip()            # Correu electrònic
                url_web = row[7].strip()          # Adreça web
                adreça_postal = row[11].strip()   # Adreça postal
                any_fund = row[24].strip()        # Columna 24

                if not nom_entitat or nom_entitat == "Columna 1":
                    continue

                # Processem i netegem l'enllaç del logo de Drive
                logo_net = self.clean_drive_url(drive_logo)
                foto_neta = self.clean_drive_url(drive_foto)

                # Netegem la web normal de l'entitat (si és de Drive la buidem, ja tenim el logo per separat)
                if "drive.google.com" in url_web and url_web == drive_logo:
                    url_web = ""
                elif url_web and url_web.startswith("www."):
                    url_web = f"https://{url_web}"

                desc_text = f"Entitat adherida a la Coordinadora Verda."
                if zona_geo:
                    desc_text += f" El seu àmbit d'actuació principal es troba a: {zona_geo}."

                # Inserció o actualització automàtica incloent el nou camp foto_url
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
                        'logo_url': logo_net,
                        'foto_url': foto_neta,
                    }
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            self.stdout.write(self.style.SUCCESS(
                f"Sincronització TSV completada -> Creades: {created_count} | Actualitzades: {updated_count}"
            ))