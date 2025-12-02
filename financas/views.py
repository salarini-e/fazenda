from django.shortcuts import render
from .models import Servico
# Create your views here.


def index(request):
  
    context = { 
        'titulo': 'ops',
        'servicos': Servico.objects.filter(ativo=True),                  
    }

    return render(request, 'financas/index.html', context)

def nfse(request):
    context = {

    }
    return render(request, 'financas/nfse.html', context)