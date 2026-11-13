import csv
import os
import re
import requests
import difflib  # Per calcular la similitud entre noms
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from core.models import Associacio

class Command(BaseCommand):
    help = "Importa entitats des d'un fitxer TSV detectant canvis de nom per similitud"

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
        if "id=" in url:
            match = re.search(r'id=([^&]+)', url)
            if match:
                video_id = match.group(1)
        elif "/file/d/" in url:
            match = re.search(r'/file/d/([^/]+)', url)
            if match:
                video_id = match.group(1)
                
        if video_id:
            return f"https://drive.google.com/uc?export=view&id={video_id}"
        
        return url

    def download_image_from_drive(self, url, file_name):
        """Descarrega la imatge de Google Drive i retorna un ContentFile per a Django."""
        if not url or "drive.google.com" not in url:
            return None

        drive_id = None
        if "id=" in url:
            match = re.search(r'id=([^&]+)', url)
            if match:
                drive_id = match.group(1)
        elif "/file/d/" in url:
            match = re.search(r'/file/d/([^/]+)', url)
            if match:
                drive_id = match.group(1)

        if not drive_id:
            return None

        download_url = f"https://drive.google.com/thumbnail?id={drive_id}&sz=s1000"
        try:
            res = requests.get(download_url, timeout=15)
            if res.status_code == 200 and 'image' in res.headers.get('Content-Type', ''):
                return ContentFile(res.content, name=file_name)
        except Exception:
            pass
        return None

    def similarity(self, a, b):
        return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()

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

                nom_entitat = row[1].strip()      # Columna 1 (Nom)
                nom_popular = row[2].strip()      # Nom popular
                drive_logo = row[3].strip()       # Logo de l'entitat
                drive_foto = row[4].strip()       # Imatge de la lluita
                zona_geo = row[5].strip()         # Àmbit geogràfic
                email = row[6].strip()            # Correu electrònic
                url_web = row[7].strip()          # Adreça web
                adreça_postal = row[11].strip()   # Adreça postal
                any_fund = row[24].strip()        # Any fundació

                if not nom_entitat or nom_entitat == "Columna 1":
                    continue

                # 1. Busquem si l'entitat ja existeix exactament pel nom
                associacio = Associacio.objects.filter(nom=nom_entitat).first()

                # 2. Si no existeix exactament, busquem si hi ha alguna amb una similitud >= 82% (0.82)
                if not associacio:
                    totes = Associacio.objects.all()
                    millor_coincidencia = None
                    major_score = 0.0

                    clean_prefixes = ["la ", "l'", "associació ", "assiciació ", "avv de la ", "avv "]
                    
                    for ent in totes:
                        score = self.similarity(ent.nom, nom_entitat)
                        
                        # Comprovació neta treient prefixos comuns per afinar la cerca
                        n1 = ent.nom.lower()
                        n2 = nom_entitat.lower()
                        for p in clean_prefixes:
                            n1 = n1.replace(p, "")
                            n2 = n2.replace(p, "")
                        score_net = self.similarity(n1, n2)
                        
                        final_score = max(score, score_net)
                        if final_score > major_score:
                            major_score = final_score
                            millor_coincidencia = ent

                    # Si supera el 82%, considerem que és un canvi de nom de la mateixa entitat
                    if major_score >= 0.82 and millor_coincidencia:
                        self.stdout.write(self.style.WARNING(
                            f"-> Canvi de nom detectat ({int(major_score*100)}%): '{millor_coincidencia.nom}' -> '{nom_entitat}'"
                        ))
                        associacio = millor_coincidencia
                        associacio.nom = nom_entitat  # Actualitzem al nom nou

                # Processem i netegem els enllaços de Drive
                logo_net = self.clean_drive_url(drive_logo)
                foto_neta = self.clean_drive_url(drive_foto)

                if "drive.google.com" in url_web and url_web == drive_logo:
                    url_web = ""
                elif url_web and url_web.startswith("www."):
                    url_web = f"https://{url_web}"

                desc_text = f"Entitat adherida a la Coordinadora Verda."
                if zona_geo:
                    desc_text += f" El seu àmbit d'actuació principal es troba a: {zona_geo}."

                # 3. Creem o actualitzem l'associació mantenint l'ID existent si l'hem trobat per similitud
                if associacio:
                    associacio.nom = nom_entitat  # Assegurem que s'actualitza el nom nou
                    associacio.descripcio_curta = nom_popular[:150]
                    associacio.descripcio = desc_text
                    associacio.zona_geografica = zona_geo if zona_geo else "Catalunya"
                    associacio.correu = email if email else None
                    associacio.web = url_web if url_web else None
                    associacio.adreça = adreça_postal if adreça_postal else None
                    associacio.any_fundacio = any_fund if any_fund else None
                    associacio.logo_url = logo_net
                    associacio.foto_url = foto_neta
                    associacio.save()
                    updated_count += 1
                else:
                    associacio = Associacio.objects.create(
                        nom=nom_entitat,
                        descripcio_curta=nom_popular[:150],
                        descripcio=desc_text,
                        zona_geografica=zona_geo if zona_geo else "Catalunya",
                        correu=email if email else None,
                        web=url_web if url_web else None,
                        adreça=adreça_postal if adreça_postal else None,
                        any_fundacio=any_fund if any_fund else None,
                        logo_url=logo_net,
                        foto_url=foto_neta,
                    )
                    created_count += 1

                # --- Descarregar i sobreescriure la foto només si ha canviat ---
                if drive_foto:
                    filename = f"associacio_{associacio.id}.jpg"
                    
                    foto_ha_canviat = (associacio.foto_url != foto_neta)
                    fitxer_existeix = associacio.foto and os.path.exists(associacio.foto.path)

                    if foto_ha_canviat or not fitxer_existeix:
                        img_content = self.download_image_from_drive(drive_foto, filename)
                        
                        if img_content:
                            if associacio.foto:
                                associacio.foto.delete(save=False)
                            
                            associacio.foto.save(filename, img_content, save=True)
                            associacio.foto_url = foto_neta
                            associacio.save(update_fields=['foto_url'])

            self.stdout.write(self.style.SUCCESS(
                f"Sincronització TSV completada -> Creades: {created_count} | Actualitzades: {updated_count}"
            ))