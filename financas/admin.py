from django.contrib import admin
from .models import Servico


@admin.register(Servico)
class ServicoAdmin(admin.ModelAdmin):
    list_display = ("titulo", "ativo", "ordem")
    list_editable = ("ativo", "ordem")
    search_fields = ("titulo", "descricao")
