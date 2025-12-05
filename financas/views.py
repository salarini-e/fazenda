from django.shortcuts import render
from .models import Servico, PaginasRelacionadas
# Create your views here.


def index(request):
  
    context = { 
        'titulo': 'Fazenda',
        'servicos': Servico.objects.filter(ativo=True),
        "paginas_relacionadas": PaginasRelacionadas.objects.all(),
    }

    return render(request, 'financas/index.html', context)

def nfse(request):
    context = {

    }
    return render(request, 'financas/nfse.html', context)
