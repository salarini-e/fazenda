from django.contrib import admin
from .models import Servico, PaginasRelacionadas


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "ativo", "ordem")
    list_editable = ("ativo", "ordem")
    search_fields = ("titulo", "descricao")

@admin.register(PaginasRelacionadas)
class PaginasRelacionadasAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'link')
