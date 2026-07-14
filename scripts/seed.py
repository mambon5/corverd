import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'corverd_project.settings')
django.setup()

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import Associacio, Activitat, Noticia, Comentari
from django.utils import timezone
from datetime import timedelta, time
import random
import os

def seed():
    # Esborrem dades anteriors per no tenir duplicats o problemes
    print("Netejant la base de dades existent...")
    Comentari.objects.all().delete()
    Noticia.objects.all().delete()
    Activitat.objects.all().delete()
    Associacio.objects.all().delete()
    User.objects.filter(username__startswith='representant_').delete()
    
    # Create the user group
    reps_group, _ = Group.objects.get_or_create(name="representants d'associacions")

    # Grant permissions to the group
    models_to_permit = [Associacio, Activitat, Noticia, Comentari]
    for model in models_to_permit:
        content_type = ContentType.objects.get_for_model(model)
        permissions = Permission.objects.filter(content_type=content_type)
        reps_group.permissions.add(*permissions)

    for i in range(1, 6):
        # 5 users
        username = f"representant_{i}"
        user, created = User.objects.get_or_create(username=username, defaults={'email': f"{username}@associacio{i}.cat"})
        user.set_password(os.getenv('SEED_USER_PASSWORD', 'password123'))
        user.is_staff = True
        user.save()
        user.groups.add(reps_group)

        # 5 Associacions
        assoc, _ = Associacio.objects.get_or_create(
            nom=f"Associació de Defensa {i}",
            defaults={
                'descripcio': f"Una associació increïble per a protegir la natura (Grup {i}).",
                'any_fundacio': 2010 + i,
                'zona_geografica': f"Comarca {i}",
                'latitud': 41.3851 + (i * 0.01),
                'longitud': 2.1734 + (i * 0.01),
                'gerent': user
            }
        )

        noticies_creades = []
        # 3 Noticies per associacio
        for j in range(1, 4):
            noticia, _ = Noticia.objects.get_or_create(
                titol=f"Notícia important #{j} de {assoc.nom}",
                associacio=assoc,
                defaults={
                    'contingut': f"El resum de la notícia número {j} que afecta a {assoc.nom}.",
                    'usuari': user
                }
            )
            noticies_creades.append(noticia)

        # 2 Activitats amb dates i hores diferents
        activitats_creades = []
        for j in range(1, 3):
            act_date = (timezone.now() + timedelta(days=i*2)).date()
            act_time = time(10 if j == 1 else 16, 0)
            
            act, _ = Activitat.objects.get_or_create(
                titol=f"Activitat {'Matinal' if j==1 else 'de Tarda'} de {assoc.nom}",
                associacio=assoc,
                defaults={
                    'descripcio': f"Ens trobarem a les {act_time.strftime('%H:%M')} per la nostra activitat {j}.",
                    'data': act_date,
                    'hora': act_time,
                    'adreça': f"Carrer de l'Activitat {j}, Ciutat {i}",
                    'latitud': 41.3851 - (i * 0.01) + (j * 0.005),
                    'longitud': 2.1734 + (i * 0.01) - (j * 0.005),
                    'usuari': user
                }
            )
            activitats_creades.append(act)

        # 1 comentari per a cada activitat
        # (El model té Comentari.noticia, de manera que associem el comentari a la Noticia, però sobre el tema de l'Activitat)
        for act in activitats_creades:
            comentari_random, _ = Comentari.objects.get_or_create(
                text=f"Molt bona iniciativa per la {act.titol} que es farà a {act.adreça}!",
                usuari=user,
                noticia=random.choice(noticies_creades)
            )

    print("S'ha inicialitzat la base de dades amb èxit!")

if __name__ == '__main__':
    seed()
