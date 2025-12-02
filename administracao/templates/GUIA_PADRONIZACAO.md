# Guia de Padronização - Admin Page Header

Este guia documenta os novos componentes padronizados baseados no `dashboard-topbar` para criar uma experiência consistente em todas as páginas administrativas.

## 🎯 Objetivo

Substituir os elementos `admin-page-header` e `admin-breadcrumb` por componentes mais modernos e consistentes, baseados no design do dashboard.

## 📦 Componentes Disponíveis

### 1. Admin Page Header (`includes/admin_page_header.html`)

Componente reutilizável que substitui o header antigo com design padronizado.

#### Uso Básico:
```django
{% include 'includes/admin_page_header.html' with 
   page_title="Título da Página" 
   page_subtitle="Descrição da página" 
   page_icon="fas fa-icon" 
   show_back_btn=True 
   back_url="nome_da_url" 
   show_dashboard_btn=True 
   show_breadcrumb=True 
%}
```

#### Parâmetros Disponíveis:
- `page_title`: Título principal da página
- `page_subtitle`: Subtítulo/descrição
- `page_icon`: Ícone FontAwesome (ex: "fas fa-users")
- `show_back_btn`: Exibir botão "Voltar" (boolean)
- `back_url`: URL para o botão voltar
- `show_dashboard_btn`: Exibir botão "Dashboard" (boolean)
- `show_breadcrumb`: Exibir breadcrumb (boolean)
- `show_refresh_btn`: Exibir botão de atualizar (boolean)

### 2. Base Template (`base_admin_page.html`)

Template base que já inclui o header e fornece estrutura padronizada.

#### Uso Básico:
```django
{% extends 'base_admin_page.html' %}
{% block title %}Título da Página{% endblock %}

{% with page_title="Título" page_subtitle="Subtítulo" page_icon="fas fa-icon" %}

{% block card_content %}
<!-- Seu conteúdo aqui -->
{% endblock %}

{% endwith %}
```

#### Blocos Disponíveis:
- `breadcrumb_items`: Itens personalizados do breadcrumb
- `nav_items`: Itens de navegação (tabs)
- `card_header`: Header personalizado do card
- `card_content`: Conteúdo principal
- `card_footer`: Footer do card
- `additional_content`: Conteúdo fora do card

## 🚀 Exemplos de Uso

### Exemplo 1: Página Simples
```django
{% extends 'base_admin_page.html' %}
{% block title %}Lista de Usuários{% endblock %}

{% with page_title="Usuários" page_subtitle="Gerenciar usuários do sistema" page_icon="fas fa-users" show_dashboard_btn=True %}

{% block card_content %}
<div class="table-responsive">
  <table class="table table-hover">
    <!-- Sua tabela aqui -->
  </table>
</div>
{% endblock %}

{% endwith %}
```

### Exemplo 2: Página com Navegação
```django
{% extends 'base_admin_page.html' %}
{% block title %}Editar Usuário{% endblock %}

{% with page_title="Editar Usuário" page_subtitle="Atualizar informações do usuário" page_icon="fas fa-user-edit" show_back_btn=True back_url="lista_usuarios" show_navigation=True %}

{% block breadcrumb_items %}
<li class="breadcrumb-item"><a href="{% url 'lista_usuarios' %}">Usuários</a></li>
<li class="breadcrumb-item active">Editar</li>
{% endblock %}

{% block nav_items %}
<div class="nav-item">
  <a href="{% url 'novo_usuario' %}" class="nav-link">
    <i class="fas fa-plus me-2"></i>Novo Usuário
  </a>
</div>
<div class="nav-item">
  <a href="{% url 'lista_usuarios' %}" class="nav-link active">
    <i class="fas fa-list me-2"></i>Listar Usuários
  </a>
</div>
{% endblock %}

{% block card_content %}
<form method="POST">
  {% csrf_token %}
  <!-- Seu formulário aqui -->
</form>
{% endblock %}

{% endwith %}
```

### Exemplo 3: Página com Header Personalizado
```django
{% extends 'base_admin_page.html' %}
{% block title %}Relatórios{% endblock %}

{% with page_title="Relatórios" page_subtitle="Análises e estatísticas" page_icon="fas fa-chart-bar" show_refresh_btn=True %}

{% block card_header %}
<div class="card-header">
  <h5 class="card-title mb-0">
    <i class="fas fa-file-alt me-2"></i>
    Relatório Mensal
  </h5>
  <p class="card-subtitle text-muted mb-0">Dados consolidados do mês atual</p>
</div>
{% endblock %}

{% block card_content %}
<!-- Conteúdo do relatório -->
{% endblock %}

{% endwith %}
```

## 🎨 Classes CSS Disponíveis

### Botões:
- `.btn-page-action`: Botões do header
- `.btn-page-action.btn-primary`: Botão primário
- `.btn-page-action.btn-secondary`: Botão secundário
- `.btn-page-action.btn-outline`: Botão outline

### Navegação:
- `.admin-nav-tabs`: Container das tabs
- `.nav-item .nav-link`: Links de navegação
- `.nav-link.active`: Link ativo

### Cards:
- `.card`: Card principal
- `.card-header`: Header do card
- `.card-body`: Corpo do card
- `.card-footer`: Footer do card

### Tabelas:
- `.table-action-btn`: Botões de ação em tabelas

## 📱 Responsividade

O sistema é totalmente responsivo e se adapta automaticamente a diferentes tamanhos de tela:

- **Desktop**: Layout completo com todos os elementos
- **Tablet**: Botões com texto reduzido
- **Mobile**: Navegação empilhada, botões somente com ícones

## 🔄 Migração do Sistema Antigo

### Antes (sistema antigo):
```django
<div class="admin-page-header">
  <h1 class="page-title">Título</h1>
  <p class="page-subtitle">Subtítulo</p>
</div>
<div class="admin-breadcrumb">
  <!-- breadcrumb -->
</div>
```

### Depois (sistema novo):
```django
{% include 'includes/admin_page_header.html' with page_title="Título" page_subtitle="Subtítulo" %}
```

### Ou usando o template base:
```django
{% extends 'base_admin_page.html' %}
{% with page_title="Título" page_subtitle="Subtítulo" %}
{% block card_content %}
<!-- conteúdo -->
{% endblock %}
{% endwith %}
```

## ✅ Benefícios

1. **Consistência**: Design uniforme em todas as páginas
2. **Modernidade**: Visual baseado no dashboard moderno
3. **Responsividade**: Funciona perfeitamente em todos os dispositivos
4. **Flexibilidade**: Fácil customização através de parâmetros
5. **Manutenibilidade**: Centralização do código de header
6. **Acessibilidade**: ARIA labels e navegação por teclado

## 🔧 Próximos Passos

1. Aplicar o novo padrão em todas as páginas administrativas
2. Remover referências ao sistema antigo (`admin-page-header`, `admin-breadcrumb`)
3. Padronizar ícones e cores em todo o sistema
4. Criar templates específicos para diferentes tipos de página (listagem, formulário, etc.)

---

**Nota**: Este sistema foi baseado no excelente design do `dashboard-topbar` e expandido para atender todas as necessidades do painel administrativo.