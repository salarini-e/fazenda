
from .functions import generateToken
from django.db import IntegrityError
import unicodedata
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.db.models import Q, Count
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.utils import timezone
from cursos.models import *
from datetime import date
from django.template.loader import render_to_string
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator

from django.contrib.auth.decorators import user_passes_test
from autenticacao.functions import validate_cpf
from autenticacao.forms import Form_Pessoa, Form_Alterar_Pessoa
from django.contrib.auth.decorators import login_required

import csv
import re

from .models import *
from cursos.forms import *


from palestras.models import *
from palestras.forms import *


@staff_member_required
def enviar_email(aluno, turma):
    try:
        subject = f'Inscrição no curso {turma.curso.nome}'
        from_email = settings.EMAIL_HOST_USER
        to = [aluno.email]
        text_content = 'This is an important message.'
        html_content = render_to_string('email.html', {
            'turma': turma,
            'aluno': aluno
        }
        )
        msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except Exception as E:
        print(E)
    else:
        print('email enviado com sucesso!')


@staff_member_required
def adm_cursos_cadastrar(request):
    form = CadastroCursoForm()

    if request.method == 'POST':
        form = CadastroCursoForm(request.POST, request.FILES)
        if form.is_valid():
            curso = form.save(commit=False)
            curso.user_inclusao = request.user
            curso.user_ultima_alteracao = request.user
            curso.save()

            messages.success(request, 'Novo curso cadastrado!')
            return redirect('adm_cursos_listar')

    context = {
        'form': form,
        'CADASTRAR': 'NOVO'
    }
    return render(request, 'app_cursos/cursos/adm_cursos_cad_edit.html', context)

@staff_member_required
def adm_curso_visualizar(request, id):
    curso = get_object_or_404(Curso, pk=id)
    turmas = Turma.objects.filter(curso=curso)
    context = {
        'curso': curso,
        'turmas': turmas,
        'CADASTRAR': 'NOVO'
    }
    return render(request, 'app_cursos/cursos/adm_curso_visualizar.html', context)

@staff_member_required
def adm_curso_editar(request, id):
    curso = Curso.objects.get(id=id)
    form = CadastroCursoForm(instance=curso)

    if request.method == 'POST':
        form = CadastroCursoForm(request.POST, request.FILES, instance=curso)
        if form.is_valid():
            form.save()

    context = {
        'form': form,
        'CADASTRAR': 'EDITAR',
        'curso': curso
    }
    return render(request, 'app_cursos/cursos/adm_cursos_cad_edit.html', context)

@staff_member_required
def adm_curso_detalhes(request, id):
    curso = get_object_or_404(Curso, pk=id)
    interessados = Alertar_Aluno_Sobre_Nova_Turma.objects.filter(curso=curso, alertado=False).order_by('aluno__pessoa__dt_inclusao')
    matrizCur = Disciplinas.objects.filter(curso=curso)
    turmas = Turma.objects.filter(curso=curso).select_related('local').prefetch_related('instrutores', 'matricula_set')

    context = {
        'curso': curso,
        'interessados': interessados,
        'matrizesCur': matrizCur,
        'turmas': turmas
    }
    return render(request, 'app_cursos/cursos/adm_cursos_detalhes.html', context)


@staff_member_required
def adm_disciplina_adicionar(request, curso_id):
    curso = get_object_or_404(Curso, pk=curso_id)
    
    if request.method == 'POST':
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        carga_horaria = request.POST.get('carga_horaria')
        
        if nome and carga_horaria:
            Disciplinas.objects.create(
                nome=nome,
                descricao=descricao,
                carga_horaria=carga_horaria,
                curso=curso
            )
            messages.success(request, 'Disciplina adicionada com sucesso!')
            return redirect('adm_curso_detalhes', id=curso_id)
        else:
            messages.error(request, 'Nome e carga horária são obrigatórios!')
    
    context = {
        'curso': curso,
    }
    return render(request, 'app_cursos/disciplinas/adm_disciplina_adicionar.html', context)


@staff_member_required
def adm_disciplina_editar(request, disciplina_id):
    disciplina = get_object_or_404(Disciplinas, pk=disciplina_id)
    
    if request.method == 'POST':
        disciplina.nome = request.POST.get('nome')
        disciplina.descricao = request.POST.get('descricao')
        disciplina.carga_horaria = request.POST.get('carga_horaria')
        
        if disciplina.nome and disciplina.carga_horaria:
            disciplina.save()
            messages.success(request, 'Disciplina atualizada com sucesso!')
            return redirect('adm_curso_detalhes', id=disciplina.curso.id)
        else:
            messages.error(request, 'Nome e carga horária são obrigatórios!')
    
    context = {
        'disciplina': disciplina,
        'curso': disciplina.curso,
    }
    return render(request, 'app_cursos/disciplinas/adm_disciplina_editar.html', context)


@staff_member_required
def adm_curso_excluir(request, id):
    curso = get_object_or_404(Curso, pk=id)
    
    if request.method == 'POST':
        try:
            curso.delete()
            messages.success(request, f'Curso "{curso.nome}" excluído com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao excluir curso: {str(e)}')
        return redirect('adm_cursos_listar')
    
    context = {
        'curso': curso
    }
    return render(request, 'app_cursos/cursos/adm_curso_excluir.html', context)


# @staff_member_required
# def adm_cadastrar_


@staff_member_required
def cadastrar_categoria(request):

    form = CadastroCategoriaForm()
    if request.method == 'POST':
        form = CadastroCategoriaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Nova categoria cadastrada!')
            return redirect('adm_categorias_listar')
    context = {
        'form': form
    }
    return render(request, 'app_cursos/cursos/cadastrar_categoria.html', context)

@staff_member_required
def remover_interessado(request, id_curso, id):
    try:
        interessado = Alertar_Aluno_Sobre_Nova_Turma.objects.get(id=id)
        interessado.alertado = True
        interessado.save()
        return JsonResponse({'success': True})  # Retorno de sucesso como JSON
    except Alertar_Aluno_Sobre_Nova_Turma.DoesNotExist:
        return JsonResponse({'success': False})  # Retorno de falha como JSON

@staff_member_required
def cadastrar_local(request):
    form = CadastroLocalForm()

    if request.method == 'POST':
        form = CadastroLocalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Novo local cadastrado!')
            return redirect('adm_locais_listar')
    context = {
        'form': form
    }
    return render(request, 'app_cursos/cursos/cadastrar_local.html', context)


@staff_member_required
def administrativo(request):
    # Obter turmas ativas (em andamento e aguardando)
    turmas_ativas = Turma.objects.filter(
        status__in=['ati', 'acc', 'pre', 'agu']
    ).select_related('curso', 'local').prefetch_related('instrutores').order_by('data_inicio')[:6]
    
    # Obter estatísticas gerais
    total_cursos = Curso.objects.filter(ativo=True).count()
    total_alunos = Matricula.objects.filter(status='a').values('aluno').distinct().count()
    total_instrutores = Instrutor.objects.count()
    # total_eventos = Evento.objects.filter(app_name='cursos').count()  # Temporariamente comentado - modelo não existe
    total_eventos = 0  # Valor padrão até que o modelo seja criado
    
    # Contar turmas por status
    turmas_aguardando = Turma.objects.filter(status__in=['pre', 'agu']).count()
    turmas_em_andamento = Turma.objects.filter(status__in=['ati', 'acc']).count()
    
    context = {
        'turmas_ativas': turmas_ativas,
        'total_cursos': total_cursos,
        'total_alunos': total_alunos,
        'total_instrutores': total_instrutores,
        'total_eventos': total_eventos,
        'turmas_aguardando': turmas_aguardando,
        'turmas_em_andamento': turmas_em_andamento,
    }
    return render(request, 'administrativo.html', context)


@staff_member_required
def turmas(request):
    return render(request, 'app_cursos/turmas/adm_turmas.html')


@staff_member_required
def adm_turmas_cadastrar(request):
    form = CadastroTurmaForm()

    if request.method == 'POST':
        form = CadastroTurmaForm(request.POST)
        if form.is_valid():
            turma = form.save(commit=False)
            turma.user_inclusao = request.user
            turma.user_ultima_alteracao = request.user
            turma.save()
            messages.success(request, 'Nova turma cadastrada com sucesso!')
            return redirect('adm_turmas_listar')
    context = {
        'form': form
    }
    return render(request, 'app_cursos/turmas/adm_turmas_cadastrar.html', context)


@staff_member_required
def adm_turmas_listar(request):
    # Obter filtros dos parâmetros GET
    status_filter = request.GET.get('status', '')
    curso_filter = request.GET.get('curso', '')
    instrutor_filter = request.GET.get('instrutor', '')
    search_filter = request.GET.get('search', '')

    # Query base excluindo turmas encerradas (a menos que seja especificamente solicitado)
    if status_filter == 'concluida':
        turmas = Turma.objects.filter(status='enc')
    else:
        turmas = Turma.objects.exclude(status='enc')

    # Aplicar filtros adicionais
    if status_filter and status_filter != 'concluida':
        # Mapear os valores do frontend para os valores do modelo
        status_mapping = {
            'aguardando': ['pre', 'agu'],
            'em-andamento': ['ati', 'acc'],
            'cancelada': ['can']  # se existir
        }
        if status_filter in status_mapping:
            turmas = turmas.filter(status__in=status_mapping[status_filter])
    
    if curso_filter:
        turmas = turmas.filter(curso_id=curso_filter)
    
    if instrutor_filter:
        turmas = turmas.filter(instrutores__id=instrutor_filter)
    
    if search_filter:
        turmas = turmas.filter(
            Q(curso__nome__icontains=search_filter) |
            Q(local__nome__icontains=search_filter) |
            Q(instrutores__nome__icontains=search_filter)
        ).distinct()

    turmas = turmas.order_by('data_final')

    # Obter dados para os filtros
    cursos = Curso.objects.all().order_by('nome')
    professores = Instrutor.objects.all().order_by('nome')

    context = {
        'turmas': turmas,
        'cursos': cursos,
        'professores': professores,
        'current_status': status_filter,
        'current_curso': curso_filter,
        'current_instrutor': instrutor_filter,
        'current_search': search_filter,
    }
    return render(request, 'adm/adm_turmas_listar_admin.html', context)

@staff_member_required
def adm_turmas_listar_encerradas(request):
    turmas = Turma.objects.filter(status="enc").order_by('-data_final')

    context = {
        'turmas': turmas
    }
    return render(request, 'app_cursos/turmas/adm_turmas_listar_encerradas.html', context)


@staff_member_required
def adm_cursos_listar(request):
    cursos = Curso.objects.all()
    categorias = Categoria.objects.all()

    context = {
        'cursos': cursos,
        'categorias': categorias
    }
    return render(request, 'adm/adm_cursos_listar_admin.html', context)


@staff_member_required
def adm_locais(request):
    return render(request, 'app_cursos/locais/adm_locais.html')


@staff_member_required
def adm_locais_cadastrar(request):
    form = CadastroLocalForm()
    if request.method == 'POST':
        form = CadastroLocalForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Novo local cadastrado!')
            return redirect('adm_locais_listar')

    context = {
        'form': form,
        'CADASTRAR': 'NOVO'
    }
    return render(request, 'app_cursos/locais/adm_locais_cadastrar_admin.html', context)


@staff_member_required
def adm_locais_listar(request):
    locais = Local.objects.all().prefetch_related('instituicao_set')
    context = {
        'locais': locais
    }
    return render(request, 'app_cursos/locais/adm_locais_listar_admin.html', context)


@staff_member_required
def adm_locais_editar(request, id):
    local = Local.objects.get(id=id)
    form = CadastroLocalForm(instance=local)
    if request.method == 'POST':
        form = CadastroLocalForm(request.POST, instance=local)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Informações do local atualizada com sucesso')
            return redirect('adm_locais_listar')

    context = {
        'form': form,
        'local': local
    }
    return render(request, 'app_cursos/locais/adm_locais_editar_admin.html', context)


@staff_member_required
def adm_locais_excluir(request, id):
    local = Local.objects.get(id=id)
    
    if request.method == 'POST':
        # Aqui você pode adicionar verificações adicionais se necessário
        # Por exemplo, verificar se o local está sendo usado em cursos ativos
        local.delete()
        messages.success(request, f'Local "{local.nome}" foi excluído com sucesso!')
        return redirect('adm_locais_listar')
    
    context = {
        'local': local
    }
    return render(request, 'app_cursos/locais/adm_locais_excluir_admin.html', context)


@staff_member_required
def adm_local_visualizar(request, id):
    local = get_object_or_404(Local, pk=id)
    instituicoes = Instituicao.objects.filter(local=local).prefetch_related('curso_set')
    
    context = {
        'local': local,
        'instituicoes': instituicoes
    }
    return render(request, 'app_cursos/locais/adm_local_visualizar.html', context)


@staff_member_required
def adm_categorias(request):
    return render(request, 'app_cursos/categorias/adm_categorias.html')


@staff_member_required
def adm_categorias_cadastrar(request):
    form = CadastroCategoriaForm()
    if request.method == 'POST':
        form = CadastroCategoriaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Nova categoria cadastrada!')
            return redirect('adm_categorias_listar')

    context = {
        'form': form,
        'CADASTRAR': 'NOVO'
    }
    return render(request, 'app_cursos/categorias/adm_categorias_cadastrar.html', context)


@staff_member_required
def adm_categorias_listar(request):
    categorias = Categoria.objects.all().prefetch_related('curso_set')
    context = {
        'categorias': categorias
    }
    return render(request, 'adm/adm_categorias_listar_admin.html', context)


@staff_member_required
def adm_categorias_excluir(request, id):
    categoria = Categoria.objects.get(id=id)
    categoria.delete()
    return redirect('adm_categorias_listar')


@staff_member_required
def adm_categorias_editar(request, id):
    categoria = Categoria.objects.get(id=id)
    form = CadastroCategoriaForm(instance=categoria)
    if request.method == 'POST':
        form = CadastroCategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Informações da categoria atualizada!')
            return redirect('adm_categorias_listar')

    context = {
        'form': form,
        'categoria': categoria
    }
    return render(request, 'app_cursos/categorias/adm_categorias_editar.html', context)


@staff_member_required
def adm_categoria_visualizar(request, id):
    categoria = get_object_or_404(Categoria, pk=id)
    cursos = Curso.objects.filter(categoria=categoria).select_related('instituicao').prefetch_related('turma_set')
    
    # Estatísticas
    total_cursos = cursos.count()
    cursos_ativos = cursos.filter(ativo=True).count()
    total_turmas = sum(curso.turma_set.count() for curso in cursos)
    
    context = {
        'categoria': categoria,
        'cursos': cursos,
        'total_cursos': total_cursos,
        'cursos_ativos': cursos_ativos,
        'total_turmas': total_turmas
    }
    return render(request, 'app_cursos/categorias/adm_categoria_visualizar.html', context)


@staff_member_required
def adm_instituicoes_listar(request):
    instituicoes = Instituicao.objects.all().prefetch_related('curso_set').select_related('local')
    context = {
        'instituicoes': instituicoes
    }
    return render(request, 'adm/adm_instituicoes_listar_admin.html', context)


@staff_member_required
def adm_instituicao_cadastrar(request):
    form = Instituicao_form()
    if request.method == 'POST':
        form = Instituicao_form(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Nova instituição cadastrada!')
            return redirect('adm_instituicoes_listar')

    context = {
        'form': form,
        'CADASTRAR': 'NOVO'
    }
    return render(request, 'app_cursos/instituicoes/adm_instituicao_cadastrar.html', context)


@staff_member_required
def adm_instituicao_editar(request, id):
    instituicao = get_object_or_404(Instituicao, pk=id)
    form = Instituicao_form(instance=instituicao)
    
    if request.method == 'POST':
        form = Instituicao_form(request.POST, instance=instituicao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Instituição atualizada com sucesso!')
            return redirect('adm_instituicoes_listar')
    
    context = {
        'form': form,
        'instituicao': instituicao,
        'EDITAR': True
    }
    return render(request, 'app_cursos/instituicoes/adm_instituicao_editar.html', context)


@staff_member_required
def adm_instituicao_excluir(request, id):
    instituicao = get_object_or_404(Instituicao, pk=id)
    
    if request.method == 'POST':
        try:
            instituicao.delete()
            messages.success(request, f'Instituição "{instituicao.nome}" excluída com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao excluir instituição: {str(e)}')
        return redirect('adm_instituicoes_listar')
    
    context = {
        'instituicao': instituicao
    }
    return render(request, 'app_cursos/instituicoes/adm_instituicao_excluir.html', context)


@staff_member_required
def adm_instituicao_visualizar(request, id):
    instituicao = get_object_or_404(Instituicao, pk=id)
    cursos = Curso.objects.filter(instituicao=instituicao).select_related('categoria').prefetch_related('turma_set')
    
    # Estatísticas
    total_cursos = cursos.count()
    cursos_ativos = cursos.filter(ativo=True).count()
    total_turmas = sum(curso.turma_set.count() for curso in cursos)
    
    context = {
        'instituicao': instituicao,
        'cursos': cursos,
        'total_cursos': total_cursos,
        'cursos_ativos': cursos_ativos,
        'total_turmas': total_turmas
    }
    return render(request, 'app_cursos/instituicoes/adm_instituicao_visualizar.html', context)


@staff_member_required
def adm_turno_cadastrar(request, id):

    turma = get_object_or_404(Turma, pk=id)
    form = Turno_form()

    if request.method == 'POST':
        form = Turno_form(request.POST)
        if form.is_valid():
            turno = form.save()

            Turno_estabelecido.objects.create(turno=turno, turma=turma)

            messages.success(request, 'Novo turno cadastrado!')
            return redirect('adm_turma_visualizar', turma.id)

    context = {
        'form': form,
        'CADASTRAR': 'NOVO'
    }
    return render(request, 'app_cursos/turnos/adm_turno_cadastrar.html', context)


@staff_member_required
def adm_professores(request):
    context = {}
    return render(request, 'app_cursos/professores/adm_professores.html', context)


@staff_member_required
def adm_professores_cadastrar(request):
    form = CadastroProfessorForm()
    if request.method == 'POST':
        form = CadastroProfessorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Novo Instrutor cadastrada com sucesso!')
            return redirect('adm_professores_listar')

    context = {
        'form': form,
    }
    return render(request, 'app_cursos/professores/adm_professores_cadastrar.html', context)


@staff_member_required
def adm_professores_listar(request):
    instrutores = Instrutor.objects.all().prefetch_related('turma_set')
    context = {
        'instrutores': instrutores
    }
    return render(request, 'adm/adm_professores_listar_admin.html', context)


@staff_member_required
def adm_professores_editar(request, id):
    instrutor = Instrutor.objects.get(id=id)
    form = CadastroProfessorForm(instance=instrutor)
    if request.method == 'POST':
        form = CadastroProfessorForm(request.POST, instance=instrutor)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Informações do Instrutor atualizadas com sucesso!')
            return redirect('adm_professores_Listar')

    context = {
        'form': form,
        'instrutor': instrutor
    }
    return render(request, 'app_cursos/professores/adm_professores_editar.html', context)


@staff_member_required
def adm_professores_excluir(request, id):
    instrutor = Instrutor.objects.get(id=id)
    instrutor.delete()
    return redirect('adm_professores_listar')


@staff_member_required
def adm_instrutor_visualizar(request, id):
    instrutor = get_object_or_404(Instrutor, pk=id)
    turmas = Turma.objects.filter(instrutores=instrutor).select_related('curso', 'local').prefetch_related('matricula_set')
    
    # Estatísticas
    total_turmas = turmas.count()
    turmas_ativas = turmas.filter(status__in=['ati', 'acc']).count()
    turmas_aguardando = turmas.filter(status__in=['pre', 'agu']).count()
    total_alunos = sum(turma.matricula_set.filter(status='a').count() for turma in turmas)
    
    context = {
        'instrutor': instrutor,
        'turmas': turmas,
        'total_turmas': total_turmas,
        'turmas_ativas': turmas_ativas,
        'turmas_aguardando': turmas_aguardando,
        'total_alunos': total_alunos
    }
    return render(request, 'app_cursos/professores/adm_instrutor_visualizar.html', context)

@staff_member_required
def gerar_certificados(request, id):
    data_atual = datetime.date.today()
    turma = get_object_or_404(Turma, id=id)
    matriculas=Matricula.objects.filter(turma_id=id)
    matriculas_alunos = matriculas.filter(status='a').select_related('aluno')
    disciplinas = Disciplinas.objects.filter(curso_id=turma.curso.id)
    aux=[0,0]
    for d in disciplinas:
        aux[0]+=int(d.n_aulas)
        aux[1]+=int(d.carga_horaria)
    context={
        'turma': turma,
        'matriculas': matriculas_alunos,
        'data_atual': data_atual,
        'instrutor': turma.instrutores.all()[0],
        'disciplinas': disciplinas,
        'total_aulas': aux[0],
        'total_horas': aux[1]
    }
    return render(request, 'certificados.html', context)

@staff_member_required
def adm_turmas_visualizar(request, id):
    turma = Turma.objects.get(id=id)

    matriculas = Matricula.objects.filter(turma=turma)
    matriculas_alunos = matriculas.filter(status='a').select_related('aluno')
    total_aulas = Aula.objects.filter(
        associacao_turma_turno__turma=turma).count()

    matriculas_alunos_array = []
    for matricula in matriculas_alunos:
        presencas = Presenca.objects.filter(matricula=matricula.matricula).count()
        frequencia = "Nenhuma aula registrada"
        if total_aulas:
            frequencia = f"{presencas/total_aulas * 100}%"

        matriculas_alunos_array.append(
            {'aluno': matricula.aluno, 'matricula': matricula, 'frequencia': frequencia})

    matriculas_selecionados = matriculas.filter(
        status='s').select_related('aluno')

    matriculas_candidatos = matriculas.filter(
        status='c').select_related('aluno')

    if request.method == 'POST':
        for i in request.POST.getlist("candidatos_selecionados"):
            if i != 'csrfmiddlewaretoken':
                matricula_candidato = Matricula.objects.get(pk=i)
                matricula_candidato.status = 's'
                matricula_candidato.save()

    context = {
        'total_aulas': total_aulas,
        'turma': turma,
        'matriculas_alunos': matriculas_alunos_array,
        'matriculas_selecionados': matriculas_selecionados,
        'matriculas_candidatos': matriculas_candidatos,
        'qnt_alunos': matriculas_alunos.count(),
        'qnt_alunos_espera': matriculas_candidatos.count() + matriculas_selecionados.count(),
        'is_cheio': turma.quantidade_permitido <= matriculas_alunos.count(),
        'realocar': turma.status == 'pre' and len(Matricula.objects.filter(turma__curso=turma.curso, status='r')) > 0,

    }

    return render(request, 'adm/adm_turma_visualizar_admin.html', context)


@staff_member_required
def visualizar_turma_editar(request, id):
    
    turma = Turma.objects.get(id=id)
    form = CadastroTurmaForm(instance=turma)

    if request.method == 'POST':
        form = CadastroTurmaForm(request.POST, instance=turma)
        if form.is_valid():
            turma=form.save()
            if turma.status == 'ati':
                matriculas = Matricula.objects.filter(turma=turma)
                for matricula in matriculas:
                    if matricula.status == 's' or matricula.status == 'c':
                        matricula.status = 'r'
                        matricula.save()
            messages.success(request, 'Turma editada com sucesso!')
            return redirect('adm_turma_visualizar', id)
        
    context = {
        'turma': turma,
        'form': form
    }
    return render(request, 'adm/adm_turma_editar_admin.html', context)


@staff_member_required
def visualizar_turma_selecionado(request, matricula):
    matricula = Matricula.objects.get(pk=matricula)
    turma = Turma.objects.get(pk=matricula.turma_id)

    if turma.quantidade_permitido <= Matricula.objects.filter(turma=turma, status='a').count():
        messages.error(
            request, 'Turma cheia! Não é possível adicionar mais alunos.')
        return redirect('adm_turma_visualizar', matricula.turma.id)

    birthDate = matricula.aluno.pessoa.dt_nascimento
    today = date.today()
    age = 99
    
    if birthDate:
        age = today.year - birthDate.year - \
            ((today.month, today.day) < (birthDate.month, birthDate.day))

    form = CadastroAlunoForm(instance=matricula.aluno, prefix='aluno')
    form_responsavel = ''

    if age < 18:
        responsavel = Responsavel.objects.get(aluno=matricula.aluno)
        form_responsavel = CadastroResponsavelForm(
            instance=responsavel, prefix='responsavel')

    if request.method == 'POST':
        form_aluno = CadastroAlunoForm(
            request.POST, instance=matricula.aluno, prefix='aluno')

        if form_aluno.is_valid():

            if form_responsavel != '':
                form_responsavel = CadastroResponsavelForm(
                    instance=responsavel, prefix='responsavel')
                if form_responsavel.is_valid():
                    form_responsavel.save()
                else:
                    raise Exception('Erro no form do responsável')

            aluno = form_aluno.save()
            matricula.status = 'a'
            matricula.save()

            messages.success(request, "Candidato selecionado cadastrado como aluno!")
        return redirect('adm_turma_visualizar', matricula.turma.id)

    context = {
        'form': form,
        'form_responsavel': form_responsavel,
        'turma': turma,
        'selecionado': matricula.aluno,
        'matricula': matricula
    }
    return render(request, 'app_cursos/turmas/adm_turmas_editar_selecionado.html', context)


@staff_member_required
def excluir_turma(request, id):
    turma = Turma.objects.get(id=id)

    turma.delete()

    return redirect('adm_turmas_listar')

@staff_member_required
def matricular_aluno(request, id):
    if request.method == 'POST':
        form = MatriculaAlunoForm(request.POST)
        if form.is_valid():
            matricula = form.save(commit=False)
            matricula.dt_inclusao = datetime.datetime.now()
            matricula.dt_ultima_atualizacao = datetime.datetime.now()
            matricula.save()
            messages.success(request, 'Aluno matriculado com sucesso!')
            return redirect('adm_aluno_visualizar', matricula.aluno.id)
    context={
        'form': MatriculaAlunoForm(initial={'aluno': id}),
    }
    return render(request, 'app_cursos/alunos/adm_aluno_matricular.html', context)
@staff_member_required
def adm_realocar(request, id):
    turma = Turma.objects.get(id=id)
    if request.method == "POST":
        candidatos_selecionados = request.POST.getlist('candidatos_selecionados')
        for candidato in candidatos_selecionados:
            matricula_antiga = Matricula.objects.get(matricula=candidato)
            matricula_antiga.status = 'd'
            try:
                matricula_nova = Matricula.objects.create(aluno=matricula_antiga.aluno, turma=turma, status='c')
                matricula_nova.save()
                matricula_antiga.save()
                messages.success(request, f'Aluno(s) realocados para a turma {turma} com sucesso!')
            except IntegrityError as e:
                if str(e) == 'UNIQUE constraint failed: cursos_matricula.matricula':
                    messages.warning(request, f'Alguns alunos realocados <b>já estão matriculados</b> na turma {turma}!')
                    return redirect('adm_turma_visualizar', turma.id)
        return redirect('adm_turma_visualizar', turma.id)
    matriculas = Matricula.objects.filter(turma__curso=turma.curso, status='r').order_by('aluno__pessoa__nome')
            
    context={
        'turma': turma,
        'candidatos': matriculas
    }
    return render(request, 'app_cursos/turmas/adm_turma_realocar.html', context)
# @staff_member_required
# def adm_realocar(request, id):
#     turma = get_object_or_404(Turma, pk=id)

#     outras_turmas = Turma.objects.filter(curso=turma.curso).exclude(id=turma.id)

#     if outras_turmas.count() == 0:
#         messages.error(request, f"Antes de alocar os alunos é necessário criar uma turma do curso {turma.curso}")
#         return redirect('adm_turma_visualizar', turma.id)
    
#     if request.method == "POST":
#         turma_nova = get_object_or_404(Turma, pk=request.POST['turma'])
#         candidatos_selecionados = request.POST.getlist('candidatos_selecionados')
#         for candidato in candidatos_selecionados:
#             matricula_antiga = Matricula.objects.get(matricula=candidato)
#             matricula_antiga.status = 'r'
#             matricula_antiga.save()

#             matricula_nova = Matricula.objects.create(turma=turma_nova, aluno=matricula_antiga.aluno, status='c')

#         messages.success(request, f'Alunos realocados para a turma {turma_nova} com sucesso!')
#         return redirect('adm_turma_visualizar', turma_nova.id)

#     matriculas = Matricula.objects.filter(turma=turma)
#     candidatos = matriculas.filter(Q(status='s') | Q(status='c')).order_by('status')

#     context = {
#         'turma': turma,
#         'outras_turmas': outras_turmas,
#         'candidatos': candidatos
#     }

#     return render(request, 'app_cursos/turmas/adm_turma_realocar.html', context)
@staff_member_required
def adm_alunos_listar(request):
    if request.method == 'POST':                
        alunos = Aluno.objects.filter(pessoa__nome__icontains=request.POST['pesquisa'])
        if alunos.count() == 0:
            alunos = Aluno.objects.filter(pessoa__cpf__icontains=request.POST['pesquisa'])
            if alunos.count() == 0:
                messages.warning(request, 'Nenhum aluno encontrado')
    else:
        alunos = Aluno.objects.all()
    paginator = Paginator(alunos, 35)
    context = {
        'alunos': paginator.get_page(request.GET.get('page')),
        'total_alunos': alunos.count(),
    }
    return render(request, 'adm/adm_alunos_listar_admin.html', context)


@staff_member_required
def adm_aluno_visualizar(request, id):
    aluno = Aluno.objects.get(pk=id)
    responsavel = ''

    try:
        responsavel = Responsavel.objects.get(aluno=aluno)
    except:
        pass

    context = {
        'aluno': aluno,
        'matriculas': Matricula.objects.filter(aluno=aluno),
        'responsavel': responsavel,
    }

    return render(request, 'app_cursos/alunos/adm_aluno_visualizar.html', context)


@staff_member_required
def adm_aluno_editar(request, id):
    aluno = Aluno.objects.get(pk=id)

    form = CadastroAlunoForm(instance=aluno)
    if request.method == 'POST':
        form = CadastroAlunoForm(request.POST, instance=aluno)
        if form.is_valid():
            form.save()
            messages.success(request, 'Aluno(a) editado(a) com sucesso!')
            return redirect('adm_aluno_visualizar', id)

    context = {
        'aluno': aluno,
        'form': form
    }

    return render(request, 'app_cursos/alunos/adm_aluno_editar.html', context)


@staff_member_required
def adm_aluno_excluir(request, id):
    aluno = get_object_or_404(Aluno, pk=id)
    
    if request.method == 'POST':
        try:
            aluno.delete()
            messages.success(request, f'Aluno "{aluno.pessoa.nome}" excluído com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao excluir aluno: {str(e)}')
        return redirect('adm_alunos_listar')
    
    context = {
        'aluno': aluno
    }
    return render(request, 'app_cursos/alunos/adm_aluno_excluir.html', context)


@staff_member_required
def desmatricular_aluno(request, matricula):

    matricula_obj = Matricula.objects.get(matricula=matricula)
    matricula_obj.status = 'd'
    matricula_obj.save()
    messages.success(request, 'Aluno desmatriculado com sucesso')

    return redirect('adm_aluno_visualizar', matricula_obj.aluno.id)


def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


@staff_member_required
def adm_aula_cadastrar(request, turma_id):

    turma = get_object_or_404(Turma, pk=turma_id)
    turno_choices = [(turno.id, turno)
                     for turno in Turno_estabelecido.objects.filter(turma=turma)]
    form = Aula_form()
    form.fields['associacao_turma_turno'].choices = turno_choices

    if request.method == 'POST':
        form = Aula_form(data=request.POST)
        form.fields['associacao_turma_turno'].choices = turno_choices

        if form.is_valid():
            aula = form.save()
            messages.success(request, 'Aula registra!')
            return redirect('adm_aulas_listar', turma.id)

    context = {'form': form, 'CADASTRAR': 'NOVO'}
    return render(request, 'app_cursos/aulas/adm_aula_cadastrar.html', context)


@staff_member_required
def adm_aulas_listar(request, turma_id):
    from django.db.models import Count, Q

    turma = get_object_or_404(Turma, pk=turma_id)
    aulas = Aula.objects.filter(associacao_turma_turno__turma=turma).order_by('data')
    
    # Calcular estatísticas
    total_presencas = 0
    total_esperado = aulas.count() * turma.matricula_set.count()
    
    # Adicionar informações de presença para cada aula
    aulas_com_presenca = []
    for aula in aulas:
        presencas_aula = aula.presenca_set.filter(status='p').count()
        total_alunos = turma.matricula_set.count()
        percentual = (presencas_aula * 100 / total_alunos) if total_alunos > 0 else 0
        
        aula.presencas_count = presencas_aula
        aula.total_alunos = total_alunos
        aula.percentual_presenca = round(percentual, 1)
        
        total_presencas += presencas_aula
        aulas_com_presenca.append(aula)
    
    taxa_presenca = (total_presencas * 100 / total_esperado) if total_esperado > 0 else 0

    context = {
        'turma': turma,
        'aulas': aulas_com_presenca,
        'today': timezone.now().date(),
        'total_presencas': total_presencas,
        'taxa_presenca': round(taxa_presenca, 1)
    }

    return render(request, 'adm/adm_aulas_listar_admin.html', context)


@staff_member_required
def adm_aula_visualizar(request, turma_id, aula_id):

    if request.method == "POST":
        acao = request.POST.get('acao') or 'p'
        for matricula in request.POST.getlist('alunos_selecionados'):
            presenca = Presenca.objects.get_or_create(
                matricula=Matricula.objects.get(matricula=matricula), aula_id=aula_id)[0]
            presenca.status = acao
            presenca.save()

    turma = get_object_or_404(Turma, pk=turma_id)
    aula = get_object_or_404(Aula, pk=aula_id)
    matriculas = Matricula.objects.filter(turma=turma)

    matriculados = []
    for matricula in matriculas:
        try:
            presenca = Presenca.objects.get(aula=aula, matricula=matricula)
        except:
            presenca = ''

        matriculados.append({'matricula': matricula, 'presenca': presenca})

    context = {
        'turma': turma,
        'matriculados': matriculados,
        'aula': aula,
    }

    return render(request, 'app_cursos/aulas/adm_aula_visualizar.html', context)


@staff_member_required
def adm_justificativa_cadastrar(request, presenca_id):

    form = Justificativa_form()
    presenca = get_object_or_404(Presenca, pk=presenca_id)

    if request.method == "POST":
        form = Justificativa_form(request.POST)
        if form.is_valid():
            justificativa = form.save()
            presenca.justificativa = justificativa
            presenca.save()

            messages.error(request, 'Justificativa registrada!')
            return redirect('adm_aula_visualizar', presenca.aula.associacao_turma_turno.turma.id, presenca.aula.id)

    context = {
        'presenca': presenca,
        'form': form
    }

    return render(request, 'app_cursos/justificativas/adm_justificativa_cadastrar.html', context)


@staff_member_required
def adm_justificativa_visualizar(request, presenca_id):

    presenca = get_object_or_404(Presenca, pk=presenca_id)

    context = {
        'presenca': presenca,
        'aluno': presenca.matricula.aluno
    }

    return render(request, 'app_cursos/justificativas/adm_justificativa_visualizar.html', context)


# @staff_member_required
# def adm_eventos_listar(request):
#     # Temporariamente comentado - modelo Evento não existe
#     eventos = []  # Evento.objects.filter(app_name='cursos')
#     context = {
#         'eventos': eventos
#     }
#     return render(request, 'app_eventos/eventos/adm_eventos_listar.html', context)


# @staff_member_required
# def adm_evento_cadastrar(request):
#     # Temporariamente comentado - modelo Evento não existe
#     messages.error(request, 'Funcionalidade de eventos temporariamente indisponível')
#     return redirect('administrativo')


# @staff_member_required
# def adm_evento_editar(request, id):
#     # Temporariamente comentado - modelo Evento não existe
#     messages.error(request, 'Funcionalidade de eventos temporariamente indisponível')
#     return redirect('administrativo')


@staff_member_required
def import_users_from_csv(csv_file_path):
    csv_file_path = '/home/hugo/Downloads/Inscri├з├гo para o Curso Livre e Gratuito de Finan├зas Pessoais da Secretaria de Ci├кncia, Tecnologia, Inova├з├гo e Educa├з├гo Profissionalizante e Superior.vento.csv'
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        turma = Turma.objects.get(id=3)

        for row in reader:
            try:
                telefone = re.sub(r'[^\w\s]', '', row['Telefone de contato']).strip().replace(" ", "")
                password = telefone[-8:]
                print(password)
                username = f"{row['Nome'].lower().split(' ')[0]}{telefone[-3:]}"
                email = row['E-mail']
                
                user = User.objects.create_user(username, email, password)
                pessoa = Pessoa.objects.create(
                    user=user, nome=row['Nome'], email=email, endereco=row['Endereço'])
                aluno = Aluno.objects.create(pessoa=pessoa)
                matricula = Matricula.objects.create(
                    aluno=aluno, turma=turma, status='c')
                
            except Exception as e:
                print(e)
###
@staff_member_required
def administrativo_bemestaranimal(request):
    return render(request, 'adm/administracao.html')

@staff_member_required
def cadastrar_errante(request):
    errante_form = Form_Errante()
    especie_form = Form_Especie()

    context = {
        'errante_form': errante_form,
        'especie_form': especie_form
    }
    if request.method == "POST":
        errante_form = Form_Errante(request.POST, request.FILES)
        especie_form = Form_Especie(request.POST)
        if errante_form.is_valid():
            if especie_form.is_valid():
                errante = errante_form.save(commit=False)
                v_especie = especie_form.save(commit=False)
                especie, verify = Especie.objects.get_or_create(nome_especie=v_especie.nome_especie)
                errante.especie = especie
                errante.save()
                messages.success(request, 'Animal cadastrado com sucesso!')
                return redirect('cadastrar_errante')
    context = {
        'errante_form': errante_form,
        'especie_form': especie_form
    }
    return render(request, 'errante/animal-errante-cadastro.html', context)

@staff_member_required
def listar_errante(request):
    errantes = Errante.objects.all()
    context = {
        'errantes':errantes
    }
    return render(request, 'errante/animal_errante.html', context)

@staff_member_required
def listar_tutor(request):
    qntd = Tutor.objects.all().count()
    tutores = Tutor.objects.annotate(num=Count('animal'))
    context = {
        'tutores':tutores,
        'qntd':qntd,
    }
    return render(request, 'adm/listar-tutores.html', context)

@staff_member_required
def listar_animal_tutor(request, tutor_id):
    animais = Animal.objects.filter(tutor_id=tutor_id)
    tutor = Tutor.objects.get(pk=tutor_id).pessoa.nome
    context = {
        'animais':animais,
        'tutor':tutor
    }
    return render(request, 'adm/listar-animais-tutor.html', context)


@staff_member_required
def cad_infos_extras(request, tutor_id, animal_id):
    animal = Animal.objects.get(pk=animal_id)
    try:
        info = Informacoes_Extras.objects.get(animal=animal.id)
        if info:
            info_extras_form = Form_Info_Extras(instance=info)
    except:
        info_extras_form = Form_Info_Extras(initial={'animal':Animal.objects.get(pk=animal_id).id})
    context = {
        'info_extras_form':info_extras_form,
        'animal':animal
    }
    if request.method == "POST":
        if info:
            info_extras_form = Form_Info_Extras(request.POST, instance=info)
        else:
            info_extras_form = Form_Info_Extras(request.POST)
        if info_extras_form.is_valid():
            info_extras_form.save()
    return render(request, 'adm/info-extra-cadastrar.html', context)

@staff_member_required
def cad_catalogo_animal(request):
    animal_form = Form_Animal()
    especie_form = Form_Especie()
    animal_catalogo_form = Form_Catalogo()
    if request.method == "POST":
        especie_form = Form_Especie(request.POST)
        animal_form = Form_Animal(request.POST, request.FILES)
        animal_catalogo_form = Form_Catalogo(request.POST)
        if animal_form.is_valid() and especie_form.is_valid():
            animal = animal_form.save(commit=False)
            v_especie = especie_form.save(commit=False)
            especie, verify = Especie.objects.get_or_create(nome_especie=v_especie.nome_especie)
            animal.especie_id = especie.id
            animal.save()
            if animal_catalogo_form.is_valid():
                animal_adocao = animal_catalogo_form.save(commit=False)
                animal_adocao.animal=animal
                animal_adocao.save()
                messages.success(request, 'Animal cadastrado com sucesso!')
                animal_form = Form_Animal()
                especie_form = Form_Especie()
                animal_catalogo_form = Form_Catalogo()
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    context = {
        'animal_catalogo_form':animal_catalogo_form,
        'especie_form':especie_form,
        'animal_form':animal_form

    }
    return render(request, 'catalogo/animal-catalogo-cadastrar.html', context)

@staff_member_required
def listar_entrevistas(request):
    estrevistas = EntrevistaPrevia.objects.all()
    context = {
        'entrevistas':estrevistas
    }
    return render(request, 'adm/listar_entrevista_previa.html', context)

@staff_member_required
def questionario(request, id):
    entrevista = EntrevistaPrevia.objects.get(pk=id)
    form_entrevista = Form_EntrevistaPrevia(instance=entrevista)
    context = {
        'entrevista':entrevista,
        'form_entrevista':form_entrevista
    }
    return render(request, 'adm/questionario.html', context)

@staff_member_required
def gerarToken(request):
    #pra conseguir só os tutores que tem animal cadastrado
    tutores = Tutor.objects.all()
    count_s = 0
    count_n = 0
    for tutor in tutores:
        if len(Animal.objects.filter(tutor=tutor))!=0:
            try:
                TokenDesconto.objects.get(tutor=tutor)
            except:
                token = generateToken(tutor.id)
                new = TokenDesconto.objects.create(token=token, tutor=tutor)
                new.save()
                count_s += 1
        else:
            count_n += 1
    context = {
        'tutor_animal':count_s,
        'tutor_s_animal':count_n
    }
    return render(request, 'adm/gerar-token.html', context)

@staff_member_required
def censo(request):
    animais_tutor = Animal.objects.exclude(tutor=None)
    animais_tutor.filter(castrado=True)
    errantes = Errante.objects.all().count()
    adocao = Catalogo.objects.all().count()
    tutores = Tutor.objects.all().count()
    animal = Animal.objects.all()

    #só de tutores
    castrados = [
        {'tipo': 'Castrados', 'quantidade': animais_tutor.filter(castrado=True).count()},
        {'tipo': 'Não castrados', 'quantidade': animais_tutor.filter(castrado=False).count()}
    ]
    animais = [
        {'tipo':'Animais c/ tutor', 'quantidade':animal.exclude(tutor=None).count(), 'color':'#d43f35'},
        {'tipo':'Animais p/ adoção', 'quantidade':animal.filter(tutor=None).count(), 'color':'#4585F4'},
        {'tipo':'Animais errantes', 'quantidade':errantes, 'color':'#099E57'}


    ] #vacinados precisa de cadastro de informação extra por parte da adm
    context = {
        'castrados':castrados,
        'errantes':errantes,
        'adocao':adocao,
        'tutores':tutores,
        'animais':animais,
        'animais_tutor':animais_tutor.count()
    }
    return render(request, 'adm/censo.html', context)

#quantidade de animais castrados e não castrados
# vacinados (mas não pede essa informação no usuário, só na hora de cadastrar as informações extras)
@staff_member_required
def gambiarra_cevest(request):
    users = User.objects.all()
    for user in users:
        try:
            pessoa = Pessoa.objects.get(user=user)
            if len(user.username) != 11: 
                user.username = pessoa.cpf  
                user.save()
            if not Aluno.objects.filter(pessoa=pessoa).exists():
                Aluno.objects.create(
                    pessoa=pessoa,
                    profissão='Não informado',
                    escolaridade='emc',
                    estado_civil='s',
                    aceita_mais_informacoes=True,
                    li_e_aceito_termos=True
                )
                print(f'Aluno criado para o usuario {user.username} - {pessoa.nome}')
        except Pessoa.DoesNotExist:
            print(f"Pessoa nao encontrada para o usuario {user.username}")
        except Exception as e:
            print(f"Erro ao criar Aluno para o usuario {user.username}: {e}")
    return redirect('/')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def adm_cadastro_aluno(request):
    form = Form_Alterar_Pessoa()
    if request.method == 'POST':
        try:
            pessoa=Pessoa.objects.get(cpf=request.POST['cpf'])
            # messages.error(request, 'Usuário já cadastrado')
        except:
            pessoa = None
            
        if not pessoa:
            form = Form_Alterar_Pessoa(request.POST)
            if form.is_valid():
                pessoa=form.save()
                partes=request.POST['dt_nascimento'].split('-')
                user = User.objects.create_user(username=str(validate_cpf(request.POST['cpf'])), first_name=request.POST['nome'] ,email=request.POST['email'] or None, password=partes[2] + partes[1] + partes[0])
                print(partes[2] + partes[1] + partes[0])
                pessoa.user=user
                pessoa.save()
                Aluno.objects.create(
                    pessoa=pessoa,
                    profissão='Não informado',
                    escolaridade='emc',
                    estado_civil='s',
                    aceita_mais_informacoes=True,
                    li_e_aceito_termos=True
                )
                # aluno.save()
                messages.success(request, 'Usuário e aluno cadastrado com sucesso!')
    else:
        try:
            aluno = Aluno.objects.get(pessoa=pessoa)
        except:
            aluno = None
        if not aluno:
            form = Form_Alterar_Pessoa(request.POST)
            if form.is_valid():
                Aluno.objects.create(
                            pessoa=pessoa,
                            profissão='Não informado',
                            escolaridade='emc',
                            estado_civil='s',
                            aceita_mais_informacoes=True,
                            li_e_aceito_termos=True
                        )
                messages.success(request, 'Pessoa cadastrada como aluno com sucesso!')
        else:
            messages.warning(request, 'Este aluno já está cadastrado')
        
    context = {
        'form': form
    }
    return render(request, 'adm/adm_cadastro.html', context)


# ==================== DEMO FUNCTIONS ====================

from django.contrib.auth.models import User
from datetime import datetime, timedelta
import random
from django.core.files.base import ContentFile
import os


@staff_member_required
def demo_install(request):
    """
    Instala dados de demonstração para o sistema
    """
    try:
        # Criar locais
        locais = [
            {'nome': 'Centro de Ensino CEVEST', 'endereco': 'Rua Principal, 123', 'bairro': 'Centro', 'cep': '12345-678'},
            {'nome': 'Polo Norte', 'endereco': 'Av. Norte, 456', 'bairro': 'Vila Norte', 'cep': '12345-679'},
            {'nome': 'Polo Sul', 'endereco': 'Rua Sul, 789', 'bairro': 'Vila Sul', 'cep': '12345-680'},
        ]
        
        for local_data in locais:
            local, created = Local.objects.get_or_create(**local_data)
        
        # Criar instituições
        instituicoes = [
            {'nome': 'Centro Educacional CEVEST', 'sigla': 'CEVEST', 'local': Local.objects.first()},
            {'nome': 'Instituto de Tecnologia', 'sigla': 'ITECH', 'local': Local.objects.last()},
        ]
        
        for inst_data in instituicoes:
            instituicao, created = Instituicao.objects.get_or_create(**inst_data)
        
        # Criar categorias
        categorias = [
            {'nome': 'Tecnologia', 'cor': '#007bff'},
            {'nome': 'Administração', 'cor': '#28a745'},
            {'nome': 'Design', 'cor': '#dc3545'},
            {'nome': 'Marketing', 'cor': '#ffc107'},
            {'nome': 'Idiomas', 'cor': '#17a2b8'},
        ]
        
        for cat_data in categorias:
            categoria, created = Categoria.objects.get_or_create(**cat_data)
        
        # Criar professores/instrutores
        for i in range(1, 6):
            instrutor, created = Instrutor.objects.get_or_create(
                cpf=f'000.000.00{i}-0{i}',
                defaults={
                    'nome': f'Professor {i}',
                    'matricula': f'PROF{i:03d}',
                    'celular': f'(47) 9999-000{i}',
                    'email': f'prof{i}@cevest.edu.br',
                    'endereco': f'Rua Professor, {i}00',
                    'bairro': 'Centro'
                }
            )
        
        # Criar cursos
        # Primeiro, vamos definir o caminho da imagem padrão
        default_image_path = os.path.join(settings.BASE_DIR, 'cursos', 'static', 'images', 'sem-imagem.png')
        
        cursos_demo = [
            {
                'nome': 'Programação Python',
                'sigla': 'PYT',
                'tipo': 'C',
                'categoria': Categoria.objects.get(nome='Tecnologia'),
                'instituicao': Instituicao.objects.first(),
                'carga_horaria': 40,
                'tipo_carga_horaria': 'h',
                'nivel_ensino': 'M',
                'descricao': 'Curso completo de Python para iniciantes',
                'ativo': True,
                'user_inclusao': User.objects.filter(is_staff=True).first()
            },
            {
                'nome': 'Design Gráfico',
                'sigla': 'DGR',
                'tipo': 'C',
                'categoria': Categoria.objects.get(nome='Design'),
                'instituicao': Instituicao.objects.first(),
                'carga_horaria': 60,
                'tipo_carga_horaria': 'h',
                'nivel_ensino': 'M',
                'descricao': 'Aprenda design gráfico do básico ao avançado',
                'ativo': True,
                'user_inclusao': User.objects.filter(is_staff=True).first()
            },
            {
                'nome': 'Marketing Digital',
                'sigla': 'MKT',
                'tipo': 'C',
                'categoria': Categoria.objects.get(nome='Marketing'),
                'instituicao': Instituicao.objects.first(),
                'carga_horaria': 30,
                'tipo_carga_horaria': 'h',
                'nivel_ensino': 'M',
                'descricao': 'Estratégias de marketing digital para pequenas empresas',
                'ativo': True,
                'user_inclusao': User.objects.filter(is_staff=True).first()
            },
            {
                'nome': 'Inglês Básico',
                'sigla': 'ING',
                'tipo': 'C',
                'categoria': Categoria.objects.get(nome='Idiomas'),
                'instituicao': Instituicao.objects.first(),
                'carga_horaria': 80,
                'tipo_carga_horaria': 'h',
                'nivel_ensino': 'F',
                'descricao': 'Curso de inglês para iniciantes',
                'ativo': True,
                'user_inclusao': User.objects.filter(is_staff=True).first()
            },
            {
                'nome': 'Gestão de Pessoas',
                'sigla': 'GES',
                'tipo': 'C',
                'categoria': Categoria.objects.get(nome='Administração'),
                'instituicao': Instituicao.objects.first(),
                'carga_horaria': 20,
                'tipo_carga_horaria': 'h',
                'nivel_ensino': 'S',
                'descricao': 'Técnicas modernas de gestão de pessoas',
                'ativo': True,
                'user_inclusao': User.objects.filter(is_staff=True).first()
            }
        ]
        
        for curso_data in cursos_demo:
            curso, created = Curso.objects.get_or_create(
                sigla=curso_data['sigla'],
                defaults=curso_data
            )
            
            # Adicionar imagem padrão se o curso foi criado e a imagem existe
            if created and os.path.exists(default_image_path):
                try:
                    with open(default_image_path, 'rb') as f:
                        curso.banner.save(
                            f'demo_banner_{curso.sigla}.png',
                            ContentFile(f.read()),
                            save=True
                        )
                except:
                    pass  # Se der erro na imagem, continua sem ela
        
        # Criar alunos
        for i in range(1, 21):
            user, created = User.objects.get_or_create(
                username=f'aluno{i}',
                defaults={
                    'first_name': f'Aluno {i}',
                    'email': f'aluno{i}@email.com',
                    'is_staff': False
                }
            )
            if created:
                user.set_password('demo123')
                user.save()
            
            pessoa, created = Pessoa.objects.get_or_create(
                user=user,
                defaults={
                    'nome': f'Aluno {i}',
                    'email': f'aluno{i}@email.com',
                    'cpf': f'111.111.{i:03d}-{i:02d}',
                    'telefone': f'(47) 8888-{i:04d}',
                    'dt_nascimento': datetime(1990 + (i % 20), 1 + (i % 12), 1 + (i % 28)).date(),
                    'bairro': 'Centro',
                    'endereco': f'Rua Aluno, {i}',
                    'numero': f'{i}',
                    'cep': '12345-678'
                }
            )
            
            aluno, created = Aluno.objects.get_or_create(
                pessoa=pessoa,
                defaults={
                    'profissão': 'Estudante',
                    'escolaridade': 'emc',
                    'estado_civil': 's',
                    'aceita_mais_informacoes': True,
                    'li_e_aceito_termos': True
                }
            )
        
        # Criar turmas
        instrutores = Instrutor.objects.all()
        cursos = Curso.objects.all()
        locais_list = Local.objects.all()
        
        for i, curso in enumerate(cursos, 1):
            turma, created = Turma.objects.get_or_create(
                curso=curso,
                local=random.choice(locais_list),
                defaults={
                    'quantidade_permitido': random.randint(15, 30),
                    'data_inicio': datetime.now().date() + timedelta(days=random.randint(7, 30)),
                    'data_final': datetime.now().date() + timedelta(days=random.randint(60, 120)),
                    'status': 'pre',
                    'user_inclusao': User.objects.filter(is_staff=True).first()
                }
            )
            
            # Adicionar instrutor à turma (ManyToMany)
            if created:
                turma.instrutores.add(random.choice(instrutores))
            
            # Matricular alguns alunos aleatoriamente
            alunos = list(Aluno.objects.all())
            random.shuffle(alunos)
            for aluno in alunos[:random.randint(5, 15)]:
                Matricula.objects.get_or_create(
                    aluno=aluno,
                    turma=turma,
                    defaults={
                        'status': random.choice(['c', 's', 'a'])
                    }
                )
        
        messages.success(request, 'Dados de demonstração instalados com sucesso!')
        
    except Exception as e:
        messages.error(request, f'Erro ao instalar dados de demonstração: {str(e)}')
    
    return redirect('administrativo2')


@staff_member_required
def demo_uninstall(request):
    """
    Remove todos os dados de demonstração do sistema
    """
    try:
        # Deletar em ordem para evitar problemas de foreign key
        Matricula.objects.filter(aluno__pessoa__user__username__startswith='aluno').delete()
        Turma.objects.filter(codigo__startswith='T').delete()
        
        # Deletar alunos demo
        alunos_demo = Aluno.objects.filter(pessoa__user__username__startswith='aluno')
        for aluno in alunos_demo:
            aluno.pessoa.user.delete()  # Isso também deleta Pessoa e Aluno
        
        # Deletar instrutores demo
        instrutores_demo = Instrutor.objects.filter(cpf__startswith='000.000.00')
        instrutores_demo.delete()
        
        # Deletar cursos demo
        cursos_demo = ['PYT', 'DGR', 'MKT', 'ING', 'GES']
        Curso.objects.filter(sigla__in=cursos_demo).delete()
        
        # Deletar categorias demo
        categorias_demo = ['Tecnologia', 'Administração', 'Design', 'Marketing', 'Idiomas']
        Categoria.objects.filter(nome__in=categorias_demo).delete()
        
        # Deletar instituições demo
        Instituicao.objects.filter(sigla__in=['CEVEST', 'ITECH']).delete()
        
        # Deletar locais demo
        locais_demo = ['Centro de Ensino CEVEST', 'Polo Norte', 'Polo Sul']
        Local.objects.filter(nome__in=locais_demo).delete()
        
        messages.success(request, 'Dados de demonstração removidos com sucesso!')
        
    except Exception as e:
        messages.error(request, f'Erro ao remover dados de demonstração: {str(e)}')
    
    return redirect('administrativo2')


# API Views para Turnos
@staff_member_required
def api_instrutores_listar(request):
    """API para listar instrutores"""
    instrutores = Instrutor.objects.all().values('id', 'nome')
    return JsonResponse(list(instrutores), safe=False)


@staff_member_required
def api_turno_cadastrar(request):
    """API para cadastrar novo turno"""
    if request.method == 'POST':
        try:
            turma_id = request.POST.get('turma_id')
            turma = get_object_or_404(Turma, pk=turma_id)
            
            # Criar objeto Turno
            turno = Turno.objects.create(
                periodo=request.POST.get('periodo'),
                dias_semana=request.POST.get('dias_semana'),
                hora_inicio=request.POST.get('hora_inicio'),
                hora_termino=request.POST.get('hora_termino'),
                carga_horaria=request.POST.get('carga_horaria') or None,
                instrutor_id=request.POST.get('instrutor') or None,
                observacoes=request.POST.get('observacoes', '')
            )
            
            # Criar associação com a turma
            AssociacaoTurmaTurno.objects.create(
                turma=turma,
                turno=turno
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Horário cadastrado com sucesso!',
                'turno_id': turno.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao cadastrar horário: {str(e)}'
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)


@staff_member_required
def api_turno_detalhar(request, turno_id):
    """API para obter detalhes de um turno"""
    try:
        turno = get_object_or_404(Turno, pk=turno_id)
        
        data = {
            'id': turno.id,
            'periodo': turno.periodo,
            'dias_semana': turno.dias_semana,
            'hora_inicio': turno.hora_inicio.strftime('%H:%M') if turno.hora_inicio else '',
            'hora_termino': turno.hora_termino.strftime('%H:%M') if turno.hora_termino else '',
            'carga_horaria': turno.carga_horaria,
            'instrutor_id': turno.instrutor.id if turno.instrutor else None,
            'observacoes': turno.observacoes or ''
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao carregar turno: {str(e)}'
        }, status=400)


@staff_member_required
def api_turno_atualizar(request, turno_id):
    """API para atualizar turno"""
    if request.method == 'POST':
        try:
            turno = get_object_or_404(Turno, pk=turno_id)
            
            # Atualizar campos
            turno.periodo = request.POST.get('periodo', turno.periodo)
            turno.dias_semana = request.POST.get('dias_semana', turno.dias_semana)
            turno.hora_inicio = request.POST.get('hora_inicio', turno.hora_inicio)
            turno.hora_termino = request.POST.get('hora_termino', turno.hora_termino)
            turno.carga_horaria = request.POST.get('carga_horaria') or turno.carga_horaria
            turno.observacoes = request.POST.get('observacoes', turno.observacoes)
            
            # Atualizar instrutor
            instrutor_id = request.POST.get('instrutor')
            if instrutor_id:
                turno.instrutor = get_object_or_404(Instrutor, pk=instrutor_id)
            else:
                turno.instrutor = None
                
            turno.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Horário atualizado com sucesso!'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao atualizar horário: {str(e)}'
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)


@staff_member_required
def api_turno_excluir(request, turno_id):
    """API para excluir turno"""
    if request.method == 'DELETE':
        try:
            turno = get_object_or_404(Turno, pk=turno_id)
            
            # Excluir associações primeiro
            AssociacaoTurmaTurno.objects.filter(turno=turno).delete()
            
            # Excluir o turno
            turno.delete()
            
            return JsonResponse({
                'success': True,
                'message': 'Horário excluído com sucesso!'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao excluir horário: {str(e)}'
            }, status=400)
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'}, status=405)

# ==================== NOVAS FUNCIONALIDADES ====================

@staff_member_required
def adm_turma_inscrever_aluno(request, turma_id):
    turma = get_object_or_404(Turma, pk=turma_id)
    
    if request.method == 'POST':
        cpf = request.POST.get('cpf', '').strip()
        
        if not cpf:
            messages.error(request, 'CPF é obrigatório!')
            return redirect('adm_turma_inscrever_aluno', turma_id=turma_id)
        
        try:
            # Buscar pessoa pelo CPF
            pessoa = Pessoa.objects.get(cpf=cpf)
            
            # Verificar se existe aluno para essa pessoa
            try:
                aluno = Aluno.objects.get(pessoa=pessoa)
            except Aluno.DoesNotExist:
                messages.error(request, f'Pessoa com CPF {cpf} não está cadastrada como aluno.')
                return redirect('adm_turma_inscrever_aluno', turma_id=turma_id)
            
            # Verificar se já está matriculado nesta turma
            if Matricula.objects.filter(turma=turma, aluno=aluno).exists():
                messages.warning(request, f'Aluno {aluno.pessoa.nome} já está matriculado nesta turma.')
                return redirect('adm_turma_inscrever_aluno', turma_id=turma_id)
            
            # Criar matrícula
            matricula = Matricula.objects.create(
                turma=turma,
                aluno=aluno,
                status='a'  # Aluno ativo
            )
            
            messages.success(request, f'Aluno {aluno.pessoa.nome} inscrito com sucesso! Matrícula: {matricula.matricula}')
            return redirect('adm_turma_visualizar', id=turma_id)
            
        except Pessoa.DoesNotExist:
            messages.error(request, f'Pessoa com CPF {cpf} não encontrada no sistema.')
            return redirect('adm_turma_inscrever_aluno', turma_id=turma_id)
        except Exception as e:
            messages.error(request, f'Erro ao inscrever aluno: {str(e)}')
            return redirect('adm_turma_inscrever_aluno', turma_id=turma_id)
    
    # Buscar alunos já matriculados para não mostrar na pesquisa
    alunos_matriculados = Matricula.objects.filter(turma=turma).values_list('aluno_id', flat=True)
    alunos_disponiveis = Aluno.objects.exclude(id__in=alunos_matriculados).select_related('pessoa')
    
    context = {
        'turma': turma,
        'alunos_disponiveis': alunos_disponiveis
    }
    return render(request, 'adm/adm_turma_inscrever_aluno.html', context)

@staff_member_required
def adm_aluno_inscrever_turma(request, aluno_id):
    aluno = get_object_or_404(Aluno, pk=aluno_id)
    
    if request.method == 'POST':
        turma_id = request.POST.get('turma_id')
        
        if not turma_id:
            messages.error(request, 'Turma é obrigatória!')
            return redirect('adm_aluno_inscrever_turma', aluno_id=aluno_id)
        
        try:
            turma = Turma.objects.get(id=turma_id)
            
            # Verificar se já está matriculado nesta turma
            if Matricula.objects.filter(turma=turma, aluno=aluno).exists():
                messages.warning(request, f'Aluno já está matriculado na turma {turma}.')
                return redirect('adm_aluno_inscrever_turma', aluno_id=aluno_id)
            
            # Criar matrícula
            matricula = Matricula.objects.create(
                turma=turma,
                aluno=aluno,
                status='a'  # Aluno ativo
            )
            
            messages.success(request, f'Aluno inscrito na turma {turma} com sucesso! Matrícula: {matricula.matricula}')
            return redirect('adm_aluno_visualizar', id=aluno_id)
            
        except Turma.DoesNotExist:
            messages.error(request, 'Turma não encontrada.')
            return redirect('adm_aluno_inscrever_turma', aluno_id=aluno_id)
        except Exception as e:
            messages.error(request, f'Erro ao inscrever aluno: {str(e)}')
            return redirect('adm_aluno_inscrever_turma', aluno_id=aluno_id)
    
    # Buscar turmas onde o aluno não está matriculado
    turmas_matriculadas = Matricula.objects.filter(aluno=aluno).values_list('turma_id', flat=True)
    turmas_disponiveis = Turma.objects.exclude(id__in=turmas_matriculadas).select_related('curso')
    
    context = {
        'aluno': aluno,
        'turmas_disponiveis': turmas_disponiveis
    }
    return render(request, 'adm/adm_aluno_inscrever_turma.html', context)

@staff_member_required
def adm_aluno_cadastro_completo(request):
    if request.method == 'POST':
        form = Form_Alterar_Pessoa(request.POST)
        
        if form.is_valid():
            try:
                # Verificar se CPF já existe
                cpf = form.cleaned_data['cpf']
                if Pessoa.objects.filter(cpf=cpf).exists():
                    messages.error(request, f'Já existe uma pessoa cadastrada com o CPF {cpf}.')
                    return render(request, 'adm/adm_aluno_cadastro_completo.html', {'form': form})
                
                # Criar pessoa
                pessoa = form.save()
                
                # Criar usuário
                partes = form.cleaned_data['dt_nascimento'].strftime('%d%m%Y')
                user = User.objects.create_user(
                    username=str(validate_cpf(cpf)),
                    first_name=form.cleaned_data['nome'],
                    email=form.cleaned_data.get('email') or None,
                    password=partes  # Data de nascimento como senha (DDMMAAAA)
                )
                
                pessoa.user = user
                pessoa.save()
                
                # Criar aluno
                Aluno.objects.create(
                    pessoa=pessoa,
                    profissão='Não informado',
                    escolaridade='emc',
                    estado_civil='s',
                    aceita_mais_informacoes=True,
                    li_e_aceito_termos=True
                )
                
                messages.success(request, f'Aluno {pessoa.nome} cadastrado com sucesso! Senha: {partes}')
                return redirect('adm_alunos_listar')
                
            except Exception as e:
                messages.error(request, f'Erro ao cadastrar aluno: {str(e)}')
                return render(request, 'adm/adm_aluno_cadastro_completo.html', {'form': form})
    else:
        form = Form_Alterar_Pessoa()
    
    context = {
        'form': form
    }
    return render(request, 'adm/adm_aluno_cadastro_completo.html', context) 