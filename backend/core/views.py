from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Associacio, Noticia, Comentari, Activitat, AdhesioEntitat, AdhesioPersona
from .forms import AssociacioForm, ActivitatForm, GestorUserForm, GestorAssociacioForm
from django.contrib.auth.models import User
import json
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages


def index(request):
    return render(request, 'inici.html')

def custom_logout(request):
    logout(request)
    return redirect('index')

def entitats_list(request):
    entitats = Associacio.objects.all().order_by('nom')
    return render(request, 'entitats.html', {'entitats': entitats})

def entitats_adherides_view(request):
    entitats = AdhesioEntitat.objects.all().order_by('nom')
    persones = AdhesioPersona.objects.all().order_by('nom')
    return render(request, 'entitats_adherides.html', {
        'entitats': entitats,
        'persones': persones,
        'titol_pagina': 'Adhesions al manifest'
    })

def adhesio_manifest_view(request):
    if request.method == 'POST':
        tipus = request.POST.get('tipus_adhesio')
        if tipus == 'entitat':
            AdhesioEntitat.objects.create(
                nom=request.POST.get('nom'),
                lluita_o_objectiu=request.POST.get('lluita_o_objectiu'),
                contacte=request.POST.get('contacte'),
                web=request.POST.get('web')
            )
        elif tipus == 'persona':
            AdhesioPersona.objects.create(
                nom=request.POST.get('nom'),
                cognoms=request.POST.get('cognoms'),
                any_naixement=request.POST.get('any_naixement'),
                codi_postal=request.POST.get('codi_postal'),
                email=request.POST.get('email'),
                professio=request.POST.get('professio'),
                comentari=request.POST.get('comentari')
            )
        return render(request, 'adhesio.html', {'success': True})
    
    # Range of years from 1890 to current year
    years_range = range(2026, 1889, -1)
    return render(request, 'adhesio.html', {'years_range': years_range})

def entitat_activitats(request, pk):
    entitat = get_object_or_404(Associacio, pk=pk)
    activitats = Activitat.objects.filter(associacio=entitat)
    events = []
    for act in activitats:
        event = {
            'title': act.titol,
            'start': act.data.isoformat() + ('T' + act.hora.strftime('%H:%M:%S') if act.hora else ''),
            'entity_id': act.associacio_id,
            'description': act.descripcio,
            'data': act.data.strftime('%d/%m/%Y'),
            'hora': act.hora.strftime('%H:%M') if act.hora else '',
            'adreça': act.adreça or '',
            'latitud': act.latitud,
            'longitud': act.longitud,
            'pdf_activitat': act.pdf_activitat.url if act.pdf_activitat else None,
        }
        events.append(event)
    return render(request, 'entitat_activitats.html', {'entitat': entitat, 'events_json': events})

def activitats_calendar(request):
    entitats = Associacio.objects.all()
    activitats = Activitat.objects.select_related('associacio').all()
    events = []
    for act in activitats:
        event = {
            'title': act.titol,
            'start': act.data.isoformat() + ('T' + act.hora.strftime('%H:%M:%S') if act.hora else ''),
            'entity_id': act.associacio_id,
            'description': act.descripcio,
            'data': act.data.strftime('%d/%m/%Y'),
            'hora': act.hora.strftime('%H:%M') if act.hora else '',
            'adreça': act.adreça or '',
            'latitud': act.latitud,
            'longitud': act.longitud,
            'pdf_activitat': act.pdf_activitat.url if act.pdf_activitat else None,
        }
        events.append(event)
    return render(request, 'activitats_calendar.html', {'entitats': entitats, 'events_json': events})

def noticia_detail(request, pk):
    noticia = get_object_or_404(Noticia, pk=pk)
    comentaris = noticia.comentaris.all().order_by('-data')
    if request.method == 'POST' and request.user.is_authenticated:
        text = request.POST.get('text', '').strip()
        if text:
            Comentari.objects.create(noticia=noticia, usuari=request.user, text=text)
            return redirect('noticia_detail', pk=pk)
    
    return render(request, 'noticia_detail.html', {
        'noticia': noticia, 
        'comentaris': comentaris
    })

def manifest(request):
    return render(request, 'manifest.html')

def sobre(request):
    return render(request, 'sobre.html')

def testimonis(request):
    return render(request, 'testimonis.html')

def faq(request):
    return render(request, 'faq.html')

def recursos(request):
    return render(request, 'recursos.html')

def serveis(request):
    return render(request, 'serveis.html')

def blog(request):
    return render(request, 'blog.html')

def proteccio_dades(request):
    return render(request, 'proteccio_dades.html')

@login_required
def intranet_dashboard(request):
    associacions = Associacio.objects.filter(gerent=request.user)
    entitat = associacions.first() if associacions.exists() else None
    activitats = entitat.activitats.all().order_by('-data', '-hora') if entitat else []
    
    return render(request, 'intranet/dashboard.html', {
        'entitat': entitat,
        'activitats': activitats,
    })

@login_required
def editar_entitat(request, pk):
    entitat = get_object_or_404(Associacio, pk=pk, gerent=request.user)
    if request.method == 'POST':
        form = AssociacioForm(request.POST, instance=entitat)
        if form.is_valid():
            form.save()
            return redirect('intranet_dashboard')
    else:
        form = AssociacioForm(instance=entitat)
    return render(request, 'intranet/formulari.html', {'form': form, 'titol': 'Editar Entitat'})

@login_required
def crear_activitat(request):
    entitat = Associacio.objects.filter(gerent=request.user).first()
    if not entitat:
        return redirect('intranet_dashboard')
        
    if request.method == 'POST':
        form = ActivitatForm(request.POST, request.FILES)
        if form.is_valid():
            activitat = form.save(commit=False)
            activitat.associacio = entitat
            activitat.usuari = request.user
            activitat.save()
            if form.cleaned_data.get('pdf_activitat'):
                activitat.pdf_activitat = form.cleaned_data['pdf_activitat']
                activitat.save()
            return redirect('intranet_dashboard')
    else:
        form = ActivitatForm()
    return render(request, 'intranet/formulari.html', {'form': form, 'titol': 'Nova Activitat'})

@login_required
def editar_activitat(request, pk):
    entitat = Associacio.objects.filter(gerent=request.user).first()
    activitat = get_object_or_404(Activitat, pk=pk, associacio=entitat)
    if request.method == 'POST':
        form = ActivitatForm(request.POST, request.FILES, instance=activitat)
        if form.is_valid():
            activitat = form.save(commit=False)
            if form.cleaned_data.get('pdf_activitat'):
                activitat.pdf_activitat = form.cleaned_data['pdf_activitat']
            activitat.save()
            return redirect('intranet_dashboard')
    else:
        form = ActivitatForm(instance=activitat)
    return render(request, 'intranet/formulari.html', {'form': form, 'titol': 'Editar Activitat'})

@login_required
def esborrar_activitat(request, pk):
    entitat = Associacio.objects.filter(gerent=request.user).first()
    activitat = get_object_or_404(Activitat, pk=pk, associacio=entitat)
    activitat.delete()
    return redirect('intranet_dashboard')

def mapa_entitats_view(request):
    entitats = Associacio.objects.all().order_by('nom')
    entitats_json = []
    for e in entitats:
        entitats_json.append({
            'id': e.id,
            'nom': e.nom,
            'descripcio': e.descripcio,
            'latitud': float(e.latitud) if e.latitud else None,
            'longitud': float(e.longitud) if e.longitud else None,
            'web': e.web,
        })
    return render(request, 'mapa_entitats.html', {
        'entitats': entitats,
        'entitats_json': json.dumps(entitats_json)
    })

def historia_view(request):
    return render(request, 'historia.html')

def presentacio_view(request):
    return render(request, 'presentacio.html')

def organitzacio_view(request):
    return render(request, 'organitzacio.html')

def contacte(request):
    if request.method == 'POST':
        nom_representant = request.POST.get('nom_representant')
        nom_entitat = request.POST.get('nom_entitat')
        email = request.POST.get('email')
        descripcio = request.POST.get('descripcio')

        subject_admin = f"Nou contacte de {nom_representant} ({nom_entitat})"
        message_admin = f"Nom representant: {nom_representant}\nNom entitat: {nom_entitat}\nCorreu: {email}\n\nDescripció:\n{descripcio}"
        
        subject_user = "Confirmació de recepció - Coordinadora Verda"
        message_user = f"Hola {nom_representant},\n\nHem rebut correctament el teu missatge a la Coordinadora en Defensa del Patrimoni Verd. Ens posarem en contacte amb tu al més aviat possible.\n\nDetalls del missatge enviat:\nEntitat: {nom_entitat}\nMissatge:\n{descripcio}\n\nAtentament,\nCoordinadora en Defensa del Patrimoni Verd"

        # Envia correu a la coordinadora
        try:
            send_mail(
                subject_admin,
                message_admin,
                settings.DEFAULT_FROM_EMAIL,
                ['contacte@coordinadoraverda.cat'],
                fail_silently=True,
            )
        except Exception:
            pass

        # Envia correu de confirmació al remitent
        try:
            send_mail(
                subject_user,
                message_user,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            messages.success(request, "El missatge s'ha enviat correctament.")
        except Exception as e:
            messages.error(request, f"Error en enviar el correu de confirmació al remitent: {str(e)}")
            
        return render(request, 'contacte.html', {'success': True})
        
    return render(request, 'contacte.html')


import os

def control_dashboard(request):
    # Check if the user is logged in as the special gestor
    is_gestor = request.session.get('is_gestor', False)
    
    # Handle Login attempt
    if request.method == 'POST' and request.POST.get('action') == 'login':
        user_env = os.getenv('gestor_web')
        pass_env = os.getenv('gestor_contrasenya')
        
        user_input = request.POST.get('username')
        pass_input = request.POST.get('password')
        
        if user_input == user_env and pass_input == pass_env:
            request.session['is_gestor'] = True
            return redirect('control_dashboard')
        else:
            messages.error(request, "Credencials incorrectes.")
    
    # Handle Logout
    if request.GET.get('logout') == 'true':
        request.session['is_gestor'] = False
        return redirect('control_dashboard')

    if not is_gestor:
        return render(request, 'control_dashboard.html', {'is_gestor': False})
        
    # If logged in as gestor
    form_user = GestorUserForm()
    form_assoc = GestorAssociacioForm()
    
    admins_exist = User.objects.filter(is_staff=True).exists()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'crear_usuari':
            form_user = GestorUserForm(request.POST)
            if form_user.is_valid():
                username = form_user.cleaned_data['username']
                password = form_user.cleaned_data['password']
                email = form_user.cleaned_data['email']
                first_name = form_user.cleaned_data['first_name']
                last_name = form_user.cleaned_data['last_name']
                is_admin = form_user.cleaned_data['is_admin']
                
                if User.objects.filter(username=username).exists():
                    messages.error(request, f"L'usuari '{username}' ja existeix.")
                else:
                    new_user = User.objects.create_user(
                        username=username,
                        password=password,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                    )
                    if is_admin:
                        new_user.is_staff = True
                        new_user.save()
                    messages.success(request, f"Usuari '{username}' creat correctament.")
                    return redirect('control_dashboard')
                    
        elif action == 'crear_associacio':
            form_assoc = GestorAssociacioForm(request.POST, request.FILES)
            if form_assoc.is_valid():
                form_assoc.save()
                messages.success(request, "Associació creada correctament.")
                return redirect('control_dashboard')
            else:
                messages.error(request, "Error al crear l'associació.")

    return render(request, 'control_dashboard.html', {
        'is_gestor': True,
        'form_user': form_user,
        'form_assoc': form_assoc,
        'admins_exist': admins_exist
    })
