from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Associacio, Noticia, Comentari, Activitat
from .forms import AssociacioForm, ActivitatForm
import json

def index(request):
    return render(request, 'inici.html')

def custom_logout(request):
    logout(request)
    return redirect('index')

def entitats_list(request):
    entitats = Associacio.objects.all()
    # Puc afegir les ultimes noticies de cadascuna
    return render(request, 'entitats.html', {'entitats': entitats})

def entitat_activitats(request, pk):
    entitat = get_object_or_404(Associacio, pk=pk)
    activitats = entitat.activitats.all()
    events = []
    for a in activitats:
        events.append({
            'title': a.titol,
            'start': a.data.strftime('%Y-%m-%d') + 'T' + a.hora.strftime('%H:%M:%S'),
            'description': a.descripcio,
            'adreça': a.adreça,
            'data': a.data.strftime('%d/%m/%Y'),
            'hora': a.hora.strftime('%H:%M'),
        })
    return render(request, 'entitat_activitats.html', {'entitat': entitat, 'events_json': events})

def activitats_calendar(request):
    entitats = Associacio.objects.all()
    activitats = Activitat.objects.all()
    events = []
    for a in activitats:
        events.append({
            'title': f"[{a.associacio.nom}] {a.titol}",
            'start': a.data.strftime('%Y-%m-%d') + 'T' + a.hora.strftime('%H:%M:%S'),
            'description': a.descripcio,
            'entity_id': a.associacio.id,
            'adreça': a.adreça,
            'data': a.data.strftime('%d/%m/%Y'),
            'hora': a.hora.strftime('%H:%M'),
        })
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

def contacte(request):
    # En el futur podria gestionar un formulari aquí
    return render(request, 'contacte.html')

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
        form = ActivitatForm(request.POST)
        if form.is_valid():
            activitat = form.save(commit=False)
            activitat.associacio = entitat
            activitat.usuari = request.user
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
        form = ActivitatForm(request.POST, instance=activitat)
        if form.is_valid():
            form.save()
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
