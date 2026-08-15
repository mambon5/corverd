from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from core.models import Activitat
import os

class Command(BaseCommand):
    help = 'Elimina els PDFs d\'activitats que han passat fa més de 3 dies'

    def handle(self, *args, **kwargs):
        three_days_ago = timezone.now().date() - timedelta(days=3)
        activitats = Activitat.objects.filter(data__lt=three_days_ago).exclude(pdf_activitat__exact='')

        count = 0
        for activitat in activitats:
            if activitat.pdf_activitat:
                try:
                    if os.path.isfile(activitat.pdf_activitat.path):
                        os.remove(activitat.pdf_activitat.path)
                    activitat.pdf_activitat = None
                    activitat.save()
                    count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'No s\'ha pogut eliminar el PDF de l\'activitat ID {activitat.id}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'S\'han eliminat {count} PDFs antics.'))
