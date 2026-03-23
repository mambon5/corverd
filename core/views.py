from django.shortcuts import render, get_object_or_404, redirect
from .models import Associacio, Noticia, Comentari, Activitat
import json

def index(request):
    return render(request, 'inici.html')

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
