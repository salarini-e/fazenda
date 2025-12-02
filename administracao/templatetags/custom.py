from django import template
from cursos.models import Alertar_Aluno_Sobre_Nova_Turma
from cursos.models import Matricula, Turma
register = template.Library()

@register.filter
def qntInteressados(id):
    return Alertar_Aluno_Sobre_Nova_Turma.objects.filter(curso=id, alertado=False).count()

@register.filter
def countCandidatos(id):
    turma = Turma.objects.get(id=id)
    matriculas = Matricula.objects.filter(turma=turma, status='c')
    return matriculas.count()

@register.filter
def mul(value, arg):
    """Multiply the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def div(value, arg):
    """Divide the value by the argument."""
    try:
        return float(value) / float(arg) if float(arg) != 0 else 0
    except (ValueError, TypeError):
        return 0