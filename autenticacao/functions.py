from django.forms import ValidationError
from functools import wraps
from django.conf import settings
from django.shortcuts import redirect

from autenticacao.models import Pessoa
# from cursos.models import Aluno


def validate_cpf(cpf):
    """
    Function that validates a CPF.
    """
    cpf = cpf.replace('.', '')
    cpf = cpf.replace('-', '')
    if len(cpf) != 11:
        raise ValidationError(('O CPF deve conter 11 dígitos'), code='invalid1')
    if cpf in ["00000000000", "11111111111", "22222222222", "33333333333", "44444444444", "55555555555", "66666666666", "77777777777", "88888888888", "99999999999"]:
        raise ValidationError(('CPF inválido'), code='invalid2')

    sum = 0
    weight = 10
    for i in range(9):
        sum += int(cpf[i]) * weight
        weight -= 1
    check_digit = 11 - (sum % 11)
    if check_digit > 9:
        check_digit = 0
    if check_digit != int(cpf[9]):
        raise ValidationError(('CPF inválido'), code='invalid2')
    sum = 0
    weight = 11
    for i in range(10):
        sum += int(cpf[i]) * weight
        weight -= 1
    check_digit = 11 - (sum % 11)
    if check_digit > 9:
        check_digit = 0
    if check_digit != int(cpf[10]):
        raise ValidationError(('CPF inválido'), code='invalid2')
    return cpf

def aluno_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_superuser:
            # try:
            #     pessoa = Pessoa.objects.get(user=request.user)                
            # except Exception as e:
            #     #redireciona para cadastrar Pessoa
            #     return redirect("autenticacao:cadastrar_usuario")

            # try:
            #     aluno = Aluno.objects.get(pessoa=pessoa)                                
            # except Aluno.DoesNotExist:
            #     #redireciona para cadastrar Aluno
            #     return redirect("autenticacao:cadastrar_aluno")
            
            return view_func(request, *args, **kwargs)   
        elif request.user.is_superuser:
            return view_func(request, *args, **kwargs)   
        else:
            return redirect(settings.LOGIN_URL)                
    return wrapper